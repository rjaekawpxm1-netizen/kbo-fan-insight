"""관중수 예측 모델 (XGBoost) — 학습·평가.

입력: data/processed/attendance_features.csv  (build_dataset.py 산출물)
출력: models/attendance_xgb.pkl  + 콘솔에 실제 성능 지표

설계 원칙:
- 시간순 분할: 랜덤 분할은 미래→과거 누수가 되므로 금지. 시즌 뒤쪽을 테스트로 둔다.
- baseline 비교: '학습기간 평균 관중으로 전부 찍기'와 비교해 모델의 실익을 확인한다.
- 범주형(홈/원정/구장)은 XGBoost 네이티브 categorical 처리. 코드 일치를 위해
  분할 전 전체 데이터에서 category 타입을 확정한다(타깃이 아닌 어휘 정보라 누수 아님).

실행: 프로젝트 루트에서
    python -m src.analysis.attendance_forecast
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

CAT_COLS = ["home", "away", "stadium"]
NUM_COLS = ["dow", "is_weekend", "is_friday", "month", "home_game_no",
            "home_prev_avg"]
TARGET = "attendance"
TEST_FRAC = 0.2


def load_dataset() -> pd.DataFrame:
    path = config.PROCESSED_DIR / "attendance_features.csv"
    if not path.exists():
        raise FileNotFoundError(
            "피처셋이 없습니다. 먼저 `python -m src.preprocess.build_dataset` 실행."
        )
    df = pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    for c in CAT_COLS:  # 분할 전 category 확정 → train/test 코드 일치
        df[c] = df[c].astype("category")
    return df


def time_split(df: pd.DataFrame, frac: float):
    n_test = max(1, int(len(df) * frac))
    return df.iloc[:-n_test].copy(), df.iloc[-n_test:].copy()


def metrics(y_true, y_pred) -> dict:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)
    return {"MAE": mae, "RMSE": rmse, "MAPE(%)": mape}


def main() -> None:
    df = load_dataset()
    train, test = time_split(df, TEST_FRAC)
    print(f"[데이터] 전체 {len(df)} · 학습 {len(train)} · 테스트 {len(test)}")
    print(f"[기간] 테스트 {test['date'].min().date()} ~ {test['date'].max().date()}")

    X_train, y_train = train[CAT_COLS + NUM_COLS], train[TARGET]
    X_test, y_test = test[CAT_COLS + NUM_COLS], test[TARGET]

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        tree_method="hist",
        enable_categorical=True,
        random_state=42,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    # baseline1: 학습기간 전체 평균
    base_pred = np.full(len(y_test), y_train.mean())
    # baseline2: 학습기간 '구장별 평균' (구장만 보는 단순 룩업 — 진짜 비교 대상)
    stadium_mean = y_train.groupby(train["stadium"], observed=True).mean().to_dict()
    base2_pred = (test["stadium"].map(stadium_mean)
                  .astype("float64").fillna(y_train.mean()).to_numpy())

    m_model = metrics(y_test.values, pred)
    m_base = metrics(y_test.values, base_pred)
    m_base2 = metrics(y_test.values, base2_pred)

    print("\n[성능] 테스트셋 기준")
    print(f"{'지표':<10}{'평균':>12}{'구장별평균':>14}{'XGBoost':>12}")
    for k in m_model:
        print(f"{k:<10}{m_base[k]:>12,.1f}{m_base2[k]:>14,.1f}{m_model[k]:>12,.1f}")

    imp_vs_avg = (m_base["MAE"] - m_model["MAE"]) / m_base["MAE"] * 100
    imp_vs_st = (m_base2["MAE"] - m_model["MAE"]) / m_base2["MAE"] * 100
    print(f"\n[해석] MAE 개선 — 평균 대비 {imp_vs_avg:.1f}% / 구장별평균 대비 {imp_vs_st:.1f}%")
    print("       (구장별평균 대비 개선이 작으면, 현재 피처로는 구장 효과가 대부분이고")
    print("        요일·상대팀 효과는 작다는 의미 → 순위·승률 피처 추가가 다음 과제)")

    print("\n[피처 중요도]")
    imp = pd.Series(model.feature_importances_, index=CAT_COLS + NUM_COLS)
    for name, val in imp.sort_values(ascending=False).items():
        print(f"  {name:<18}{val:.3f}")

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = config.MODELS_DIR / "attendance_xgb.pkl"
    joblib.dump({"model": model, "cat_cols": CAT_COLS, "num_cols": NUM_COLS}, out_path)
    print(f"\n[저장] {out_path}")


if __name__ == "__main__":
    main()