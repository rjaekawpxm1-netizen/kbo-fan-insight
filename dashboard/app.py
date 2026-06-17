import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st  # noqa: E402
from src.utils import io  # noqa: E402

st.set_page_config(page_title="KBO Fan Insight", layout="wide")
st.title("KBO AI Fan Insight — Executive Dashboard")
st.markdown(
    "KBO 공개 데이터(관중·유튜브 댓글)를 수집·분석해 **관중수 예측**과 **팬 반응**을 살피고, "
    "결과를 앱 개선 방향으로 연결하는 프로젝트입니다. 모든 분석은 baseline 비교·검증을 거쳤습니다."
)

att = io.load_attendance_features()
sent = io.load_sentiment()

st.subheader("핵심 지표")
if att is None:
    st.info("관중 피처셋이 없습니다. `python -m src.preprocess.build_dataset` 먼저 실행하세요.")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 경기수", f"{len(att):,}")
    c2.metric("평균 관중", f"{att['attendance'].mean():,.0f}명")
    top = att.loc[att["attendance"].idxmax()]
    c3.metric("최다 관중 경기", f"{int(top['attendance']):,}명", f"{top['home']} vs {top['away']}")
    c4.metric("구장 수", f"{att['stadium'].nunique()}")

if sent is not None:
    pos = (sent["sentiment"] == "positive").mean() * 100
    neg = (sent["sentiment"] == "negative").mean() * 100
    c1, c2 = st.columns(2)
    c1.metric("댓글 긍정 비율(모델)", f"{pos:.1f}%")
    c2.metric("댓글 부정 비율(모델)", f"{neg:.1f}%")
    st.caption("⚠ 감성 모델은 검증 결과 신뢰도가 낮습니다(Sentiment 페이지 참조). 수치는 참고용.")

st.divider()
st.markdown(
    "#### 페이지 안내\n"
    "- **Attendance** — 관중은 언제·어디서 몰리는가 + 예측 모델 성능\n"
    "- **Sentiment** — 팬 반응(모델 한계 명시) + 키워드 빈도\n"
    "- **Content** — 어떤 영상 콘텐츠가 반응을 끄는가"
)