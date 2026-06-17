"""댓글 키워드 빈도 분석 (모델 불필요 → 감성분석보다 신뢰 가능).

입력: data/raw/youtube/comments_*.csv
출력: data/processed/keyword_overall.csv (word, count)
      data/processed/keyword_by_team.csv (team, word, count)

방식: 형태소 분석기 없이 한글 음절 단어(2자 이상)를 정규식으로 추출하고,
      경량 조사 제거 + 불용어 필터. ㅋㅋ/ㅎㅎ 등 자모는 [가-힣]에 안 잡혀 자동 제외.
      (정밀 명사 추출이 필요하면 KoNLPy(Okt/Mecab)로 업그레이드 — Java/시스템 설치 필요)

실행: python -m src.analysis.keyword_freq
"""

import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

TOKEN_RE = re.compile(r"[가-힣]{2,}")
TOP_N = 30

# 조사(접미) 경량 제거: 토큰 끝에 붙은 흔한 조사를 떼되, 남는 길이 2자 이상일 때만.
JOSA_2 = ["으로", "에서", "에게", "한테", "까지", "부터", "처럼", "보다", "라고", "이나", "네요"]
JOSA_1 = ["을", "를", "이", "가", "은", "는", "에", "의", "도", "로", "와", "과", "만"]

STOPWORDS = {
    "그냥", "진짜", "너무", "정말", "우리", "그리고", "하지만", "근데", "이거", "저거", "그거",
    "이건", "저건", "그건", "오늘", "어제", "내일", "지금", "다시", "이번", "그래도", "그렇게",
    "이렇게", "저렇게", "라고", "라는", "인데", "는데", "정도", "때문", "경기", "선수", "진짜로",
    "그게", "이게", "저게", "거의", "완전", "역시", "약간", "조금", "많이", "아주", "계속",
}


def _strip_josa(tok: str) -> str:
    for j in JOSA_2:
        if tok.endswith(j) and len(tok) - len(j) >= 2:
            return tok[: -len(j)]
    for j in JOSA_1:
        if tok.endswith(j) and len(tok) - 1 >= 2:
            return tok[:-1]
    return tok


def tokenize(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    out = []
    for tok in TOKEN_RE.findall(text):
        tok = _strip_josa(tok)
        if len(tok) >= 2 and tok not in STOPWORDS:
            out.append(tok)
    return out


def _latest_comments() -> Path:
    files = sorted((config.RAW_DIR / "youtube").glob("comments_*.csv"))
    if not files:
        raise FileNotFoundError("댓글 CSV 없음. youtube_comments 먼저 실행.")
    return files[-1]


def main() -> None:
    df = pd.read_csv(_latest_comments())
    print(f"[로드] 댓글 {len(df)}개")

    df["tokens"] = df["text"].map(tokenize)

    # 전체 빈도
    overall = Counter(t for toks in df["tokens"] for t in toks)
    ov = (pd.DataFrame(overall.most_common(TOP_N), columns=["word", "count"]))

    # 팀별 빈도 (매치업 단위: 댓글 토큰을 team1·team2 모두에 귀속)
    rows = []
    if {"team1", "team2"}.issubset(df.columns):
        for col in ["team1", "team2"]:
            for team, sub in df.groupby(col):
                c = Counter(t for toks in sub["tokens"] for t in toks)
                for w, n in c.most_common(TOP_N):
                    rows.append({"team": team, "word": w, "count": n})
    by_team = pd.DataFrame(rows)
    if not by_team.empty:  # 같은 팀이 team1/team2로 중복 → 합산
        by_team = (by_team.groupby(["team", "word"], as_index=False)["count"].sum()
                   .sort_values(["team", "count"], ascending=[True, False]))

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ov.to_csv(config.PROCESSED_DIR / "keyword_overall.csv", index=False, encoding="utf-8-sig")
    by_team.to_csv(config.PROCESSED_DIR / "keyword_by_team.csv", index=False, encoding="utf-8-sig")

    print(f"\n[전체 상위 20]\n{ov.head(20).to_string(index=False)}")
    print(f"\n[저장] keyword_overall.csv / keyword_by_team.csv")


if __name__ == "__main__":
    main()