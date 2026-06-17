import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st  # noqa: E402
from src.utils import io  # noqa: E402

st.set_page_config(page_title="KBO Fan Insight", page_icon="⚾", layout="wide")

st.title("⚾ KBO AI Fan Insight Platform")
st.markdown("##### KBO 공개 데이터로 관중·팬 반응을 분석하고, 앱 개선 방향까지 연결한 데이터 분석 + 서비스 기획 프로젝트")
st.caption("수집 → 분석 → 검증 → 대시보드 → 앱 개선 제안 · 모든 분석은 baseline 비교와 검증을 거쳤습니다")

att = io.load_attendance_features()
com = io.load_comments()

st.subheader("핵심 결과")
cols = st.columns(4)
with cols[0]:
    with st.container(border=True):
        st.metric("분석 경기수", f"{len(att):,}" if att is not None else "—")
with cols[1]:
    with st.container(border=True):
        st.metric("평균 관중", f"{att['attendance'].mean():,.0f}명" if att is not None else "—")
with cols[2]:
    with st.container(border=True):
        mae_txt = "—"
        bundle = io.load_model()
        if att is not None and bundle is not None:
            try:
                from sklearn.metrics import mean_absolute_error
                from src.analysis.attendance_forecast import CAT_COLS, NUM_COLS, time_split, TEST_FRAC
                df = att.sort_values("date").reset_index(drop=True)
                for c in CAT_COLS:
                    df[c] = df[c].astype("category")
                _, test = time_split(df, TEST_FRAC)
                pred = bundle["model"].predict(test[CAT_COLS + NUM_COLS])
                mae_txt = f"{mean_absolute_error(test['attendance'], pred):,.0f}명"
            except Exception:
                pass
        st.metric("관중 예측 MAE", mae_txt, "구장별평균 대비 개선")
with cols[3]:
    with st.container(border=True):
        st.metric("수집 댓글", f"{len(com):,}건" if com is not None else "—")

st.write("")
left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.markdown(
            "### 이 프로젝트가 답하는 질문\n"
            "1. **관중은 언제·어디서 몰리고, 예측할 수 있는가?** → Attendance\n"
            "2. **팬들은 무엇에 반응하고 무엇을 이야기하는가?** → Sentiment\n"
            "3. **어떤 콘텐츠가 반응을 끄는가?** → Content\n\n"
            "그리고 그 결과를 **앱 개선(개인화 홈·추천 경기·콘텐츠 정렬)** 으로 연결합니다."
        )
with right:
    with st.container(border=True):
        st.markdown(
            "### 방법론 · 신뢰성\n"
            "- 관중 예측: **시간순 분할 + 누수 방지**, 전체·구장별 평균 **baseline과 비교**\n"
            "- 감성: 범용 모델을 **수기 200건으로 검증(정확도 39.5%)** → 한계 확인 후 **LLM 요약으로 전환**\n"
            "- LLM: 댓글에만 근거하도록 **그라운딩**, 통계는 코드가 계산\n"
            "- 데이터는 공개 출처(KBO 관중 · YouTube)만 사용"
        )

st.caption("좌측 사이드바에서 상세 페이지로 이동하세요. 데이터가 없는 페이지는 실행 안내를 표시합니다.")