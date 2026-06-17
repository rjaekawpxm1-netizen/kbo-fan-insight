"""관중 원본 CSV → 관중수 예측 모델 학습용 피처셋 구축.

입력: data/raw/attendance/attendance_*.csv  (kbo_attendance.py 산출물)
출력: data/processed/attendance_features.csv

설계 원칙:
- 타깃 누수 방지: 과거 정보만 쓰는 피처는 현재 경기를 제외(shift)하고 계산한다.
- 외부 수치 하드코딩 금지: 구장 수용규모는 임의 숫자 대신 '시즌 내 최대 관중'을 대용 지표로 쓴다.
- 순위/최근승률은 결과 데이터가 필요하므로 지금은 제외(아래 TODO 참조).

실행: 프로젝트 루트에서
    python -m src.preprocess.build_dataset
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

WEEKDAY_MAP = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}


def _latest_attendance_csv() -> Path:
    files = sorted((config.RAW_DIR / "attendance").glob("attendance_*.csv"))
    if not files:
        raise FileNotFoundError(
            "관중 CSV가 없습니다. 먼저 `python -m src.collect.kbo_attendance` 실행."
        )
    return files[-1]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """관중 원본에 모델 피처를 추가한다. 입력은 날짜 오름차순 정렬 가정."""
    df = df.sort_values("date").reset_index(drop=True)

    # 시간 피처
    df["season"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["dow"] = df["weekday"].map(WEEKDAY_MAP)
    df["is_weekend"] = df["weekday"].isin(["토", "일"]).astype(int)
    df["is_friday"] = (df["weekday"] == "금").astype(int)

    # 시즌 진행도: 홈팀이 시즌에서 치른 홈경기 누적 순번(현재 포함, 진행도 의미)
    df["home_game_no"] = df.groupby("home").cumcount() + 1

    # 홈팀의 '직전까지' 평균 홈 관중 (현재 경기 제외 → 누수 방지). 첫 경기는 NaN.
    df["home_prev_avg"] = df.groupby("home")["attendance"].transform(
        lambda s: s.shift().expanding().mean()
    )

    # 구장 효과는 stadium 범주형(XGBoost categorical)이 학습한다.
    # 과거에 쓰던 stadium_cap_proxy(시즌 전체 max)는 train/test 분리 전 계산되어
    # 테스트 구간 정보가 새는 미세 누수가 있어 제거했다.

    # ── TODO(enhancement): 결과 데이터 확보 후 병합 ───────────────────────
    # df = df.merge(rank_df,    on=["date", "home"], how="left")   # 홈팀 순위
    # df = df.merge(winrate_df, on=["date", "home"], how="left")   # 홈팀 최근 승률
    # 결과 데이터는 Schedule.aspx(JS 렌더) → Selenium 또는 AJAX 엔드포인트 필요.
    # ─────────────────────────────────────────────────────────────────────

    return df


FEATURE_COLS = [
    "date", "season", "month", "dow", "is_weekend", "is_friday",
    "home", "away", "stadium",
    "home_game_no", "home_prev_avg",
    "attendance",  # 타깃
]


def main() -> None:
    src_path = _latest_attendance_csv()
    df = pd.read_csv(src_path, parse_dates=["date"])
    print(f"[로드] {src_path.name} — {len(df)}행")

    feat = build_features(df)[FEATURE_COLS]

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = config.PROCESSED_DIR / "attendance_features.csv"
    feat.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"[저장] {out_path} — {feat.shape[0]}행 {feat.shape[1]}열")
    print("[결측] home_prev_avg 결측 수:", int(feat["home_prev_avg"].isna().sum()),
          "(홈팀별 첫 경기 → 정상)")
    print("[미리보기]")
    print(feat.head(8).to_string(index=False))


if __name__ == "__main__":
    main()