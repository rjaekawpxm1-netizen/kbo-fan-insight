"""LLM(Claude) 기반 감성 라벨링 + 인간 라벨 대비 검증.

범용 모델이 야구 슬랭에서 39.5%로 실패 → Claude를 어노테이터로 사용하되,
Claude 자체를 사람이 라벨한 200건과 비교해 신뢰도를 먼저 검증한다.

흐름:
 1) labeled_sample.csv(수기 200건)를 Claude로 라벨 → 인간 대비 일치율(정확도·F1) 측정
 2) 일치율이 높으면 대규모 샘플을 Claude로 라벨 → 신뢰할 감성 분포 산출

출력:
 - data/processed/llm_sentiment.csv  (text, like_count, team1, team2, llm_sentiment)
 - data/processed/llm_sentiment_meta.json  (검증 일치율 등)

비용 절감: 한 번에 BATCH개를 묶어 1콜로 처리.
실행: pip install anthropic 후  python -m src.analysis.llm_sentiment
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

load_dotenv()

MODEL = "claude-sonnet-4-6"   # 비용 더 줄이려면 "claude-haiku-4-5-20251001"
BATCH = 20
SAMPLE_N = 2000               # 대규모 라벨링 표본 수
DELAY = 0.4
LABELS = ["positive", "negative", "neutral"]
LABELSET = set(LABELS)

PROMPT = """다음은 KBO 야구 하이라이트 영상 댓글입니다. 각 댓글의 감성을 분류하세요.
야구 응원 맥락을 반영하세요. 예: '사이다','개추','미쳤다','지렸다','레전드'는 대개 긍정,
비꼼·실책 지적·욕설은 부정, 단순 사실·질문은 중립입니다.
각 댓글에 positive / negative / neutral 중 하나만 부여하세요.
반드시 입력과 같은 개수의 JSON 배열로만 출력하세요. 설명·코드펜스 금지.

댓글:
{items}
"""


_dbg = {"n": 0}


def _parse(raw: str, n: int) -> list[str]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
    labels = None
    # 1) JSON 시도: 문자열 배열 또는 객체 배열({"sentiment":...}) 모두 처리
    try:
        arr = json.loads(raw)
        if isinstance(arr, list):
            tmp = []
            for x in arr:
                if isinstance(x, str):
                    v = x.lower().strip()
                elif isinstance(x, dict):
                    v = str(x.get("sentiment") or x.get("label") or x.get("감성") or "").lower().strip()
                else:
                    v = ""
                tmp.append(v if v in LABELSET else None)
            if tmp and all(t is not None for t in tmp):
                labels = tmp
    except Exception:  # noqa: BLE001
        pass
    # 2) 실패 시 원문에서 라벨을 순서대로 추출(번호목록·객체 등 어떤 형식이든)
    if labels is None:
        labels = re.findall(r"positive|negative|neutral", raw.lower())
    out = []
    for i in range(n):
        out.append(labels[i] if i < len(labels) else "neutral")
    return out


def label_batch(client, texts: list[str]) -> list[str]:
    items = "\n".join(f"{i+1}. {str(t)[:200]}" for i, t in enumerate(texts))
    msg = client.messages.create(
        model=MODEL, max_tokens=1500,
        messages=[{"role": "user", "content": PROMPT.format(items=items)}],
    )
    raw = "".join(b.text for b in msg.content if b.type == "text")
    if _dbg["n"] < 1:  # 첫 응답 형식 확인용(1회)
        print(f"[디버그] 첫 응답 예시: {raw[:200]!r}")
        _dbg["n"] += 1
    return _parse(raw, len(texts))


def label_all(client, texts: list[str]) -> list[str]:
    res = []
    for i in range(0, len(texts), BATCH):
        chunk = list(texts[i:i + BATCH])
        try:
            res.extend(label_batch(client, chunk))
        except Exception as e:  # noqa: BLE001
            print(f"[배치 실패] {i}: {e}")
            res.extend(["neutral"] * len(chunk))
        time.sleep(DELAY)
    return res


def validate(client) -> dict:
    p = config.RAW_DIR / "youtube" / "labeled_sample.csv"
    if not p.exists():
        print("[검증] labeled_sample.csv 없음 → 생략")
        return {}
    lab = pd.read_csv(p)
    lab = lab[lab["label"].isin(LABELSET)].reset_index(drop=True)
    if lab.empty:
        print("[검증] 유효 수기 라벨 없음 → 생략")
        return {}
    preds = label_all(client, lab["text"].tolist())
    from sklearn.metrics import accuracy_score, classification_report
    acc = accuracy_score(lab["label"], preds)
    print(f"\n[검증] Claude vs 인간 라벨 {len(lab)}건 — 일치율(정확도) {acc:.3f}")
    print(classification_report(lab["label"], preds, labels=LABELS, zero_division=0))
    return {"agreement": round(float(acc), 3), "n_validated": int(len(lab))}


def _latest_comments() -> Path:
    files = sorted((config.RAW_DIR / "youtube").glob("comments_*.csv"))
    if not files:
        raise FileNotFoundError("댓글 CSV 없음. youtube_comments 먼저 실행.")
    return files[-1]


def main() -> None:
    try:
        import anthropic
    except ImportError:
        print("[중단] `pip install anthropic` 후 재실행.")
        return
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[중단] .env에 ANTHROPIC_API_KEY가 없습니다.")
        return
    client = anthropic.Anthropic()

    # 1) 인간 라벨 대비 검증
    meta = {"model": MODEL}
    meta.update(validate(client))

    # 2) 대규모 라벨링 (대표성 위해 무작위 표본)
    df = pd.read_csv(_latest_comments())
    n = min(SAMPLE_N, len(df))
    sample = df.sample(n, random_state=42).reset_index(drop=True)
    print(f"\n[라벨링] {n}건 Claude 라벨링 시작 (배치 {BATCH})...")
    sample["llm_sentiment"] = label_all(client, sample["text"].tolist())

    cols = [c for c in ["text", "like_count", "team1", "team2", "llm_sentiment"] if c in sample.columns]
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    sample[cols].to_csv(config.PROCESSED_DIR / "llm_sentiment.csv", index=False, encoding="utf-8-sig")
    meta["n_labeled"] = int(n)
    (config.PROCESSED_DIR / "llm_sentiment_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    dist = sample["llm_sentiment"].value_counts()
    print(f"\n[분포] {dict(dist)}")
    print(f"[저장] llm_sentiment.csv / llm_sentiment_meta.json  메타={meta}")


if __name__ == "__main__":
    main()