import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402
from src.utils import io  # noqa: E402

st.title("팬 감성 분석")
st.markdown("**이 페이지가 답하는 질문:** 팬들이 어떤 반응을 보이고, 무엇을 이야기하는가?")
sent = io.load_sentiment()
if sent is None:
    st.info("`python -m src.analysis.sentiment` 먼저 실행하세요.")
    st.stop()

st.warning(
    "**감성 모델 검증 결과 — 아래 분포는 신뢰도가 낮습니다.**\n\n"
    "범용 다국어 감성 모델을 수기 200건으로 검증한 결과 **정확도 39.5%**로, "
    "다수class baseline(58.5%)에도 미치지 못했습니다. 야구 은어(사이다·개추 등)를 "
    "부정으로 오분류하는 한계가 확인되었습니다(긍정 recall 0.36).\n\n"
    "**수기 검증 표본(n=200) 기준 실제 분포는 긍정 약 59% 우세**입니다. "
    "아래 모델 기반 분포는 도메인 한계를 보여주는 참고용이며, 도메인 파인튜닝이 향후 과제입니다."
)
st.caption("하이라이트 댓글 기반. 팀 분포는 매치업 단위(홈/원정·승패 통제는 향후).")

dist = sent["sentiment"].value_counts().reset_index()
dist.columns = ["sentiment", "count"]
st.subheader("전체 감성 분포")
st.plotly_chart(px.bar(dist, x="sentiment", y="count", color="sentiment"), use_container_width=True)

if {"team1", "team2"}.issubset(sent.columns):
    long = pd.concat([
        sent[["team1", "sentiment"]].rename(columns={"team1": "team"}),
        sent[["team2", "sentiment"]].rename(columns={"team2": "team"}),
    ]).reset_index(drop=True)
    ct = long.groupby(["team", "sentiment"]).size().reset_index(name="count")
    st.subheader("팀별 감성 분포")
    st.plotly_chart(px.bar(ct, x="team", y="count", color="sentiment", barmode="stack"), use_container_width=True)

st.subheader("예시 댓글 (좋아요순)")
cols = [c for c in ["text", "like_count", "sentiment", "team1", "team2"] if c in sent.columns]
sort_col = "like_count" if "like_count" in sent.columns else cols[0]
st.dataframe(sent.sort_values(sort_col, ascending=False)[cols].head(20), use_container_width=True)

st.divider()
st.header("키워드 빈도 (모델 불필요 · 신뢰 가능)")
st.caption("감성 모델과 달리 단어 빈도는 모델 추정이 아니라 직접 집계라 신뢰할 수 있다. "
           "'팬이 무엇을 이야기하는가'를 보여준다.")

kw = io.load_keyword_overall()
if kw is None:
    st.info("`python -m src.analysis.keyword_freq` 실행 시 표시됩니다.")
else:
    top = kw.head(20).sort_values("count")
    st.metric("가장 많이 언급된 단어", str(kw.iloc[0]["word"]), f"{int(kw.iloc[0]['count']):,}회")
    st.subheader("전체 상위 키워드")
    st.plotly_chart(px.bar(top, x="count", y="word", orientation="h"), use_container_width=True)

    by_team = io.load_keyword_by_team()
    if by_team is not None and not by_team.empty:
        st.subheader("팀별 상위 키워드")
        team = st.selectbox("팀 선택", sorted(by_team["team"].unique()))
        sub = by_team[by_team["team"] == team].head(15).sort_values("count")
        st.plotly_chart(px.bar(sub, x="count", y="word", orientation="h"),
                        use_container_width=True)

    st.divider()
    st.markdown("**시사점:** 감성 모델은 한계가 있었지만, 키워드 빈도는 모델 없이 신뢰 가능한 "
                "'팬 관심사' 지표다. 자주 언급되는 선수·상황을 앱 콘텐츠·푸시 주제 선정에 활용 가능. (docs/05 참조)")

st.divider()
st.header("AI 팬 반응 요약 (Claude)")
st.caption("범용 감성 모델이 야구 슬랭에 실패해, 한국어 맥락을 더 잘 읽는 LLM으로 정성 요약. "
           "학습 모델이 아니라 LLM 요약이며, 주어진 댓글에 근거하도록 그라운딩했다. "
           "⚠ 하이라이트는 두 팀이 함께 등장 → **매치업(경기) 단위 반응**이며 상대팀 선수가 섞일 수 있음.")
fr = io.load_fan_report()
if fr is None:
    st.info("`python -m src.analysis.llm_fan_report` 실행 시 표시됩니다. (.env에 ANTHROPIC_API_KEY 필요)")
else:
    teams = [k for k in fr.keys() if not k.startswith("_")]
    if teams:
        t = st.selectbox("팀 선택", sorted(teams), key="fanreport")
        st.markdown(fr[t])
        meta = fr.get("_meta", {})
        if meta:
            st.caption(f"모델: {meta.get('model','?')} · 팀당 댓글 표본 {meta.get('sample_per_team','?')}개")