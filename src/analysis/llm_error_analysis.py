"""LLM 감성 오분류 분석 — Claude가 인간 라벨과 '어디서·어떻게' 갈리는지.

목적: 일치율 75.5%의 '나머지 25%'를 분해해 면접 질문("못 맞춘 건 뭐냐")에 데이터로 답한다.
입력: data/raw/youtube/labeled_sample.csv (수기 200건: text, label)
출력: data/processed/llm_error_analysis.csv (불일치 케이스)
실행: python -m src.analysis.llm_error_analysis
"""

import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402
from src.analysis.llm_sentiment import LABELS, LABELSET, label_all  # noqa: E402

load_dotenv()


def analyze(lab: pd.DataFrame) -> pd.DataFrame:
    """lab: label(인간), claude 컬럼 보유. 혼동행렬·오분류 방향·예시 출력, 불일치 반환."""
    lab = lab.copy()
    lab["agree"] = lab["label"] == lab["claude"]

    print("\n[혼동행렬]  행=인간 라벨, 열=Claude 라벨")
    cm = pd.crosstab(lab["label"], lab["claude"]).reindex(
        index=LABELS, columns=LABELS, fill_value=0)
    print(cm.to_string())

    print("\n[클래스별 일치율]")
    for c in LABELS:
        sub = lab[lab["label"] == c]
        if len(sub):
            print(f"  인간 {c:<9} {sub['agree'].mean()*100:5.1f}%  (n={len(sub)})")

    mism = lab[~lab["agree"]]
    print(f"\n[불일치] {len(mism)}/{len(lab)}건 ({len(mism)/len(lab)*100:.1f}%)")
    dirs = mism.groupby(["label", "claude"]).size().sort_values(ascending=False)
    print("\n[오분류 방향 상위]")
    for (h, c), n in dirs.items():
        print(f"  인간 {h} → Claude {c}: {n}건")

    print("\n[불일치 예시 (방향별 최대 3개)]")
    for (h, c), _ in list(dirs.items())[:4]:
        ex = mism[(mism["label"] == h) & (mism["claude"] == c)].head(3)
        print(f"\n  --- 인간 {h} / Claude {c} ---")
        for t in ex["text"]:
            print(f"    · {str(t)[:80]}")
    return mism


def main() -> None:
    try:
        import anthropic
    except ImportError:
        print("[중단] `pip install anthropic` 후 재실행.")
        return
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[중단] .env에 ANTHROPIC_API_KEY가 없습니다.")
        return

    p = config.RAW_DIR / "youtube" / "labeled_sample.csv"
    if not p.exists():
        print("[중단] labeled_sample.csv 없음.")
        return
    lab = pd.read_csv(p)
    lab = lab[lab["label"].isin(LABELSET)].reset_index(drop=True)
    if lab.empty:
        print("[중단] 유효 수기 라벨 없음.")
        return

    client = anthropic.Anthropic()
    print(f"[라벨링] 수기 {len(lab)}건을 Claude로 재라벨링...")
    lab["claude"] = label_all(client, lab["text"].tolist())

    mism = analyze(lab)
    out = config.PROCESSED_DIR / "llm_error_analysis.csv"
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    mism[["text", "label", "claude"]].to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n[저장] {out}")


if __name__ == "__main__":
    main()