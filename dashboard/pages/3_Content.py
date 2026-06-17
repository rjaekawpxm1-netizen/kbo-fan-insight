import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402
from src.utils import io  # noqa: E402

st.title("콘텐츠 이용 현황")
st.markdown("**이 페이지가 답하는 질문:** 어떤 하이라이트 콘텐츠가 팬 반응(댓글·좋아요)을 많이 끌어내는가?")

com = io.load_comments()
if com is None:
    st.info("`python -m src.collect.youtube_comments` 먼저 실행하세요.")
    st.stop()

if "title" in com.columns:
    agg = (com.groupby("title")
           .agg(댓글수=("text", "count"), 좋아요합=("like_count", "sum"))
           .sort_values("댓글수", ascending=False))
    c1, c2 = st.columns(2)
    c1.metric("분석 영상 수", f"{agg.shape[0]:,}")
    c2.metric("최다 반응 영상 댓글수", f"{int(agg['댓글수'].max()):,}")

    top = agg.head(15).reset_index()
    st.subheader("영상별 댓글 수 (상위 15)")
    st.plotly_chart(px.bar(top, x="댓글수", y="title", orientation="h"), use_container_width=True)
    st.dataframe(top, use_container_width=True)
    st.caption("댓글·좋아요가 많은 영상 = 팬 관심이 큰 콘텐츠 유형.")

    st.divider()
    st.markdown("**시사점:** 반응이 큰 콘텐츠 유형을 앱 홈 추천 정렬 상단에 배치 → 체류 시간 향상. "
                "(docs/05 · 기능요구사항 F-04 참조)")