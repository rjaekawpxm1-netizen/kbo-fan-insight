"""KBO 하이라이트 댓글 감성분석.

입력: data/raw/youtube/comments_*.csv  (youtube_comments.py 산출물)
출력: data/processed/sentiment_labeled.csv  + 분포·검증 리포트

설계 원칙:
- 모델 우선, 규칙 폴백: MODEL_NAME이 지정되고 로드되면 transformers 모델을 쓰고,
  실패하면 규칙기반(어휘 사전)으로 자동 전환한다. (이전 품질진단 프로젝트와 동일한 폴백 패턴)
- 정직한 한계: 규칙기반은 baseline이다. 반어법·맥락을 못 잡는다(README에 명시).
- 검증 필수: data/raw/youtube/labeled_sample.csv(text,label)가 있으면
  예측 정확도를 측정해 점수 신뢰도를 확인한다. (앞서 합의한 수기 200~300건 검증)

⚠ MODEL_NAME은 추측해 박지 않았다. 한국어 감성 체크포인트는 HuggingFace에서
  실제 존재·라이선스·라벨 체계를 확인한 뒤 지정하고, LABEL_MAP을 그 모델에 맞춰라.

실행: 프로젝트 루트에서
    python -m src.analysis.sentiment
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

# 모델을 쓰려면 실제 확인한 체크포인트명을 넣고 LABEL_MAP을 맞춰라. 비우면 규칙기반.
MODEL_NAME = "tabularisai/multilingual-sentiment-analysis"
LABEL_MAP = {  # tabularisai 5분류 → 표준 3분류 (predict에서 .lower() 비교)
    "very negative": "negative", "negative": "negative",
    "neutral": "neutral",
    "positive": "positive", "very positive": "positive",
}
LABELS = ["positive", "negative", "neutral"]

# 규칙기반 baseline 사전 (야구 댓글 맥락 포함). 확장 가능.
POS_WORDS = [
    "최고", "대박", "미쳤", "멋지", "멋진", "역전", "승리", "이겼", "이긴", "좋다", "좋아",
    "잘한", "잘했", "잘해", "짱", "사랑", "응원", "화이팅", "파이팅", "명장면", "클러치",
    "감동", "레전드", "행복", "고맙", "자랑", "굿", "최고다", "기대",
]
NEG_WORDS = [
    "졌", "패배", "한심", "답답", "실책", "에러", "짜증", "화나", "최악", "못한", "못해",
    "실망", "노답", "별로", "싫", "망했", "어이없", "한숨", "부진", "방출", "폭망", "분노",
]
NEG_CUES = ["안", "못", "전혀", "별로"]  # 부정어(긍정 단어 무력화용, 경량 처리)


def clean_text(t: str) -> str:
    if not isinstance(t, str):
        return ""
    t = re.sub(r"https?://\S+", " ", t)        # URL 제거
    t = re.sub(r"\s+", " ", t).strip()          # 공백 정리
    return t


def rule_score(text: str) -> str:
    """어휘 사전 기반 감성 라벨(baseline). 반어/맥락 미처리."""
    t = clean_text(text)
    pos = sum(t.count(w) for w in POS_WORDS)
    neg = sum(t.count(w) for w in NEG_WORDS)
    # 경량 부정어 처리: 부정어가 있으면 긍정 점수를 일부 상쇄
    if any(c in t for c in NEG_CUES) and pos > 0:
        pos -= 1
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def load_model_pipeline():
    """모델 로드 시도. 실패하면 None 반환(→ 규칙기반)."""
    if not MODEL_NAME:
        return None
    try:
        from transformers import pipeline
        clf = pipeline("text-classification", model=MODEL_NAME, truncation=True)
        # 실제 라벨 확인용 출력(추측 방지). 여기 라벨이 LABEL_MAP 키와 맞는지 확인할 것.
        print(f"[모델 라벨] {clf.model.config.id2label}")
        return clf
    except Exception as e:  # noqa: BLE001
        print(f"[경고] 모델 로드 실패 → 규칙기반 폴백. ({e})")
        return None


def predict(texts: list[str], clf) -> list[str]:
    if clf is None:
        return [rule_score(t) for t in texts]
    cleaned = [clean_text(t)[:300] for t in texts]
    preds, unmapped = [], set()
    BATCH = 64
    for i in range(0, len(cleaned), BATCH):
        chunk = cleaned[i:i + BATCH]
        try:
            res = clf(chunk, batch_size=BATCH, truncation=True)
        except Exception:  # noqa: BLE001
            preds.extend(rule_score(t) for t in chunk)
            continue
        for r in res:
            raw = r["label"].lower()
            if raw not in LABEL_MAP:
                unmapped.add(r["label"])
            preds.append(LABEL_MAP.get(raw, "neutral"))
    if unmapped:
        print(f"[경고] 매핑 안 된 라벨 {unmapped} → neutral 처리됨. LABEL_MAP 확인 필요.")
    return preds


def validate(clf) -> None:
    """수기 라벨 샘플로 정확도 검증."""
    path = config.RAW_DIR / "youtube" / "labeled_sample.csv"
    if not path.exists():
        print("[검증] labeled_sample.csv 없음 → 정확도 검증 건너뜀 "
              "(권장: 댓글 200~300건 수기 라벨링).")
        return
    from sklearn.metrics import accuracy_score, classification_report
    lab = pd.read_csv(path)
    pred = predict(lab["text"].tolist(), clf)
    acc = accuracy_score(lab["label"], pred)
    print(f"\n[검증] 수기 {len(lab)}건 기준 정확도 {acc:.3f}")
    print(classification_report(lab["label"], pred, labels=LABELS, zero_division=0))


def _latest_comments_csv() -> Path:
    files = sorted((config.RAW_DIR / "youtube").glob("comments_*.csv"))
    if not files:
        raise FileNotFoundError(
            "댓글 CSV가 없습니다. 먼저 `python -m src.collect.youtube_comments` 실행."
        )
    return files[-1]


def main() -> None:
    clf = load_model_pipeline()
    mode = f"모델({MODEL_NAME})" if clf else "규칙기반(baseline)"
    print(f"[모드] {mode}")

    validate(clf)

    src = _latest_comments_csv()
    df = pd.read_csv(src)
    print(f"\n[로드] {src.name} — 댓글 {len(df)}개")

    df["text_clean"] = df["text"].map(clean_text)
    df = df[df["text_clean"].str.len() > 0].reset_index(drop=True)
    df["sentiment"] = predict(df["text_clean"].tolist(), clf)

    print("\n[전체 분포]")
    print(df["sentiment"].value_counts().to_string())

    # 팀 귀속: 영상의 두 팀 모두에 매칭(매치업 단위 반응) → team 기준 분포
    if {"team1", "team2"}.issubset(df.columns):
        long = pd.concat([
            df[["team1", "sentiment"]].rename(columns={"team1": "team"}),
            df[["team2", "sentiment"]].rename(columns={"team2": "team"}),
        ]).reset_index(drop=True)
        print("\n[팀별 분포] (매치업 단위 — 홈/원정·승패 통제는 다음 단계)")
        print(pd.crosstab(long["team"], long["sentiment"]).to_string())

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PROCESSED_DIR / "sentiment_labeled.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n[저장] {out}")


if __name__ == "__main__":
    main()