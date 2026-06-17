"""LLM(Claude) 기반 팀별 팬 반응 요약.

실패한 범용 감성 모델의 후속: Claude는 한국어 야구 슬랭·맥락을 더 잘 읽는다.
단 '학습 모델'이 아니라 'LLM 정성 요약'임을 명확히 한다.

입력: data/raw/youtube/comments_*.csv
출력: data/processed/fan_report.json  ({team: 요약텍스트, "_meta": {...}})

설계 원칙:
- 그라운딩: "주어진 댓글에 있는 내용만, 없는 건 지어내지 마라" 프롬프트로 못박음.
- 통계는 LLM에 안 맡김(코드가 계산). LLM은 자연어 요약만.
- 샘플링: 팀당 좋아요 상위 N개만 전송(비용·레이트 절약).
- 팀별 호출 분리: 하나 실패해도 나머지 진행.

실행: .env에 ANTHROPIC_API_KEY 추가 후
    pip install anthropic
    python -m src.analysis.llm_fan_report
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

load_dotenv()

MODEL = "claude-sonnet-4-6"   # 비용 더 줄이려면 "claude-haiku-4-5-20251001"
SAMPLE_PER_TEAM = 60
MAX_CHARS = 150               # 댓글당 길이 제한
DELAY_SEC = 1.0               # 호출 간 간격(레이트 보호)

PROMPT_TMPL = """다음은 {team}의 KBO 하이라이트 영상 댓글 {n}개다.
아래 댓글에 담긴 내용만 근거로 분석하라. 댓글에 없는 사실·통계·경기 결과·선수 정보는 절대 지어내지 마라.

출력 형식(한국어, 간결하게):
1) 주요 화제 3가지 (각 한 줄)
2) 전반적 분위기 (긍정/부정/중립 중 우세 + 근거 한 줄)
3) 대표 댓글 2개 (그대로 인용)

[댓글]
{comments}
"""


def team_comments(df: pd.DataFrame, team: str, n: int) -> list[str]:
    m = (df.get("team1") == team) | (df.get("team2") == team)
    sub = df[m]
    if "like_count" in sub.columns:
        sub = sub.sort_values("like_count", ascending=False)
    return [str(t)[:MAX_CHARS] for t in sub["text"].dropna().head(n).tolist()]


def build_prompt(team: str, comments: list[str]) -> str:
    numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(comments))
    return PROMPT_TMPL.format(team=team, n=len(comments), comments=numbered)


def summarize_team(client, team: str, comments: list[str]) -> str:
    msg = client.messages.create(
        model=MODEL, max_tokens=700,
        messages=[{"role": "user", "content": build_prompt(team, comments)}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def _latest_comments() -> Path:
    files = sorted((config.RAW_DIR / "youtube").glob("comments_*.csv"))
    if not files:
        raise FileNotFoundError("댓글 CSV 없음. youtube_comments 먼저 실행.")
    return files[-1]


def main() -> None:
    try:
        import anthropic
    except ImportError:
        print("[중단] anthropic 미설치 → `pip install anthropic` 후 재실행.")
        return

    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[중단] .env에 ANTHROPIC_API_KEY가 없습니다.")
        return

    client = anthropic.Anthropic()
    df = pd.read_csv(_latest_comments())
    if not {"team1", "team2"}.issubset(df.columns):
        print("[중단] team1/team2 컬럼이 없습니다.")
        return

    teams = sorted(set(df["team1"].dropna()) | set(df["team2"].dropna()))
    report = {"_meta": {"model": MODEL, "sample_per_team": SAMPLE_PER_TEAM}}
    for t in teams:
        cmts = team_comments(df, t, SAMPLE_PER_TEAM)
        if not cmts:
            continue
        try:
            report[t] = summarize_team(client, t, cmts)
            print(f"[완료] {t} ({len(cmts)}개 댓글 기반)")
        except Exception as e:  # noqa: BLE001
            print(f"[실패] {t}: {e}")
        time.sleep(DELAY_SEC)

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PROCESSED_DIR / "fan_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[저장] {out}")


if __name__ == "__main__":
    main()