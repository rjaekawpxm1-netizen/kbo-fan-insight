import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402
from sklearn.metrics import mean_absolute_error  # noqa: E402
from src.utils import io  # noqa: E402

st.title("관중 분석 · 예측")
st.markdown("**이 페이지가 답하는 질문:** 관중은 언제·어디서 몰리는가? 그리고 예측할 수 있는가?")

att = io.load_attendance_features()
if att is None:
    st.info("`python -m src.preprocess.build_dataset` 먼저 실행하세요.")
    st.stop()

DOW = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}

wk = att[att.is_weekend == 1]["attendance"].mean()
wd = att[att.is_weekend == 0]["attendance"].mean()
diff = (wk - wd) / wd * 100
st_mean = att.groupby("stadium")["attendance"].mean()

st.subheader("핵심 발견")
c1, c2, c3 = st.columns(3)
c1.metric("주말 평균 관중", f"{wk:,.0f}명", f"평일 대비 {diff:+.0f}%")
c2.metric("최다 동원 구장", st_mean.idxmax(), f"{st_mean.max():,.0f}명")
c3.metric("최소 동원 구장", st_mean.idxmin(), f"{st_mean.min():,.0f}명")

daily = att.groupby("date")["attendance"].mean().reset_index()
st.subheader("일자별 평균 관중 추이")
st.plotly_chart(px.line(daily, x="date", y="attendance"), use_container_width=True)
st.caption("시즌 흐름에 따른 관중 변동. 급등락 시점은 연휴·라이벌전 등과 연관될 수 있음.")

c1, c2 = st.columns(2)
by_dow = att.groupby("dow")["attendance"].mean().reset_index()
by_dow["요일"] = by_dow["dow"].map(DOW)
c1.subheader("요일별 평균")
c1.plotly_chart(px.bar(by_dow, x="요일", y="attendance"), use_container_width=True)
c1.caption(f"주말이 평일보다 약 {diff:.0f}% 높음 → 평일 관중 유도가 개선 포인트.")

by_st = st_mean.sort_values().reset_index()
c2.subheader("구장별 평균")
c2.plotly_chart(px.bar(by_st, x="attendance", y="stadium", orientation="h"), use_container_width=True)
c2.caption("구장 간 동원력 격차가 큼 → 모델이 구장을 핵심 변수로 학습하는 이유.")

st.subheader("모델 예측 vs 실제 (테스트 구간)")
bundle = io.load_model()
if bundle is None:
    st.info("`python -m src.analysis.attendance_forecast` 실행 시 표시됩니다.")
else:
    from src.analysis.attendance_forecast import CAT_COLS, NUM_COLS, time_split, TEST_FRAC
    df = att.sort_values("date").reset_index(drop=True)
    for c in CAT_COLS:
        df[c] = df[c].astype("category")
    _, test = time_split(df, TEST_FRAC)
    pred = bundle["model"].predict(test[CAT_COLS + NUM_COLS])
    mae = mean_absolute_error(test["attendance"], pred)
    st.metric("테스트 MAE", f"{mae:,.0f}명")
    comp = pd.DataFrame({"실제": test["attendance"].values, "예측": pred})
    fig = px.scatter(comp, x="실제", y="예측")
    fig.add_shape(type="line", x0=comp["실제"].min(), y0=comp["실제"].min(),
                  x1=comp["실제"].max(), y1=comp["실제"].max())
    st.plotly_chart(fig, use_container_width=True)
    st.caption("점이 대각선에 가까울수록 정확. 요일·구장·상대팀 기반 예측.")

st.divider()
st.markdown(
    "**시사점:** 주말·인기구장에 관중이 집중됨 → 앱에서 ① 평일/저동원 경기 관심 유도(추천·혜택) "
    "② 응원팀 기준 '오늘의 추천 경기' 노출에 예측 결과 활용. (docs/05 참조)"
)