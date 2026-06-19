import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402
from src.utils import io  # noqa: E402

st.set_page_config(page_title="KBO Fan Insight", page_icon="⚾", layout="wide")

# ====================================================================
# KBO 디자인 테마 (네이비 #0a1c45 / 화이트 / 레드 #c8102e)
# ====================================================================
NAVY = "#0a1c45"
NAVY2 = "#2b5bd4"
RED = "#c8102e"
RED2 = "#e0364f"
GRAY = "#8aa0cc"
INK = "#101a36"
SUB = "#5a6378"

# 차트 색 팔레트
SEQ = [NAVY, NAVY2, GRAY, "#c3ccdd", "#26365f"]
# 감성 색 (긍정=네이비 / 부정=레드 / 중립=회색)
SENT_COLORS = {
    "positive": NAVY, "negative": RED, "neutral": "#c2c8d4",
    "긍정": NAVY, "부정": RED, "중립": "#c2c8d4",
}

def inject(s):
    """CSS/HTML 주입. st.html은 마크다운 파서를 거치지 않아 raw text로 새지 않음.
    (구버전 Streamlit 대비 markdown 폴백)"""
    s = "\n".join(line.strip() for line in s.splitlines())
    if hasattr(st, "html"):
        st.html(s)
    else:
        st.markdown(s, unsafe_allow_html=True)


inject(
    """
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
      html, body, [class*="css"], .stMarkdown, .stApp,
      [data-testid="stAppViewContainer"] { font-family:'Pretendard',-apple-system,'Apple SD Gothic Neo',sans-serif; }
      .stApp, [data-testid="stAppViewContainer"] { background:#eef0f4; }
      header[data-testid="stHeader"] { background:transparent; }
      #MainMenu, footer { visibility:hidden; }
      .block-container { padding-top:1.2rem; padding-bottom:3rem; max-width:1200px; }

      /* ---- 상단 네비 (가로 라디오) ---- */
      div[data-testid="stRadio"] > div[role="radiogroup"] {
        display:flex !important; flex-wrap:wrap; align-items:center;
        gap:2px !important; border-bottom:2px solid #0a1c45; padding-bottom:0;
      }
      div[role="radiogroup"] > label {
        background:transparent !important; border:0; border-bottom:3px solid transparent;
        border-radius:0; padding:10px 18px 9px; margin:0 !important;
        color:#7a8398; font-weight:700; display:flex; align-items:center;
      }
      div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {
        font-size:15px; font-weight:700; margin:0;
      }
      div[role="radiogroup"] > label:hover { color:#0a1c45; }
      /* 라디오 동그라미/네이티브 input 숨김 */
      div[role="radiogroup"] > label > div:first-child { display:none !important; }
      div[role="radiogroup"] input { position:absolute !important; opacity:0 !important; width:0 !important; height:0 !important; }
      div[role="radiogroup"] > label:has(input:checked) {
        border-bottom:3px solid #c8102e;
      }
      div[role="radiogroup"] > label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        color:#0a1c45;
      }

      /* ---- 카드 (container border) ---- */
      div[data-testid="stVerticalBlockBorderWrapper"] {
        background:#fff; border:1px solid #e2e6ee !important; border-radius:4px;
      }
      /* ---- metric ---- */
      div[data-testid="stMetric"] { background:transparent; }
      div[data-testid="stMetricValue"] { color:#101a36; font-weight:800; }

      h1 { color:#101a36; font-weight:800; letter-spacing:-0.01em; }
      h2, h3 { color:#101a36; font-weight:800; }

      /* ---- KBO 배너 ---- */
      .kbo-topbar {
        background:#06122e; border-radius:4px; padding:9px 16px; margin-bottom:14px;
        display:flex; align-items:center; gap:12px;
      }
      .kbo-topbar b { color:#fff; letter-spacing:0.04em; font-size:14px; }
      .kbo-topbar span { color:#7c89ab; font-size:11px; letter-spacing:0.12em; }

      .kbo-hero {
        background:#0a1c45; border-radius:6px; padding:30px 34px; margin:18px 0 22px;
      }
      .kbo-hero .eyebrow { color:#e0364f; font-weight:700; font-size:13px; letter-spacing:0.1em; }
      .kbo-hero h1 { color:#fff; font-size:34px; margin:8px 0 0; }
      .kbo-hero p { color:#aeb8d4; font-size:14.5px; margin:12px 0 0; max-width:680px; line-height:1.6; }
      .kbo-hero .stats { display:flex; gap:0; margin-top:26px; flex-wrap:wrap; }
      .kbo-hero .stat { padding:0 34px; border-left:1px solid #25366a; }
      .kbo-hero .stat:first-child { padding-left:0; border-left:0; }
      .kbo-hero .stat .v { color:#fff; font-size:30px; font-weight:800; }
      .kbo-hero .stat .v.red { color:#e0364f; }
      .kbo-hero .stat .l { color:#9fabcc; font-size:12px; margin-top:2px; }

      .kbo-pagehead { background:#0a1c45; border-radius:6px; padding:24px 30px; margin:18px 0 22px; }
      .kbo-pagehead .eyebrow { color:#e0364f; font-weight:700; font-size:12.5px; letter-spacing:0.08em; }
      .kbo-pagehead h1 { color:#fff; font-size:27px; margin:8px 0 0; }
      .kbo-pagehead p { color:#aeb8d4; font-size:14px; margin:9px 0 0; line-height:1.5; }
    </style>
    """
)


def style_fig(fig, h=320):
    """plotly 차트를 KBO 테마로."""
    fig.update_layout(
        height=h, template="plotly_white",
        font=dict(family="Pretendard, sans-serif", color=INK, size=13),
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#eef0f4")
    return fig


DOW = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}

# ---------- 데이터 로드 ----------
att = io.load_attendance_features()
sent = io.load_sentiment()
com = io.load_comments()
kw = io.load_keyword_overall()
by_team = io.load_keyword_by_team()
fan = io.load_fan_report()
bundle = io.load_model()


def attendance_mae():
    if att is None or bundle is None:
        return None
    try:
        from sklearn.metrics import mean_absolute_error
        from src.analysis.attendance_forecast import CAT_COLS, NUM_COLS, time_split, TEST_FRAC
        df = att.sort_values("date").reset_index(drop=True)
        for c in CAT_COLS:
            df[c] = df[c].astype("category")
        _, test = time_split(df, TEST_FRAC)
        pred = bundle["model"].predict(test[CAT_COLS + NUM_COLS])
        return mean_absolute_error(test["attendance"], pred), test, pred
    except Exception:
        return None


_mae = attendance_mae()


def kpi(col, label, value, badge=None, desc=None):
    with col:
        with st.container(border=True):
            st.caption(label)
            st.markdown(f"### {value}")
            if badge:
                st.markdown(f":red[**{badge}**]")
            if desc:
                st.caption(desc)


# ---------- 상단 네비 ----------
inject(
    '<div class="kbo-topbar"><b>KBO</b>'
    '<span>FAN INSIGHT · 공개 데이터 분석 · 서비스 기획</span></div>'
)
page = st.radio(
    "메뉴",
    ["종합 대시보드", "관중 분석·예측", "팬 감성·반응", "콘텐츠 이용", "분석 → 제언"],
    horizontal=True, label_visibility="collapsed",
)


# ---------- 1. 종합 대시보드 ----------
def render_overview():
    n_games = f"{len(att):,}" if att is not None else "—"
    n_com = f"{len(com):,}" if com is not None else "—"
    mae_v = f"{_mae[0]:,.0f}" if _mae else "—"
    inject(
        f"""
        <div class="kbo-hero">
          <div class="eyebrow">2026 KBO · 공개 데이터 분석 리포트</div>
          <h1>데이터로 읽는 KBO 팬의 마음</h1>
          <p>KBO 공개 데이터(관중·유튜브 댓글)를 직접 수집·분석해 관중수를 예측하고 팬 반응을 검증한 <b style="color:#fff;">데이터 분석 포트폴리오</b>입니다.</p>
          <div class="stats">
            <div class="stat"><div class="v">{n_games}</div><div class="l">분석 경기수</div></div>
            <div class="stat"><div class="v">{n_com}</div><div class="l">수집 댓글</div></div>
            <div class="stat"><div class="v red">{mae_v}</div><div class="l">관중 예측 MAE · 구장별평균 대비 개선</div></div>
            <div class="stat"><div class="v">75.5%</div><div class="l">LLM·사람 판단 일치율</div></div>
          </div>
        </div>
        """
    )

    st.subheader("핵심 지표")
    cols = st.columns(4)
    kpi(cols[0], "분석 경기수", n_games if att is None else f"{len(att):,}",
        "KBO 공식 관중", "2026 시즌, 크롤링 검증")
    kpi(cols[1], "평균 관중", f"{att['attendance'].mean():,.0f}명" if att is not None else "—",
        None, "경기당 평균 입장 관중")
    kpi(cols[2], "관중 예측 MAE", f"{_mae[0]:,.0f}명" if _mae else "—",
        "시간순 검증", "구장별평균 baseline 대비 개선")
    kpi(cols[3], "수집 댓글", f"{len(com):,}건" if com is not None else "—",
        "YouTube API", "하이라이트 영상 댓글")

    st.subheader("한눈에 보는 핵심 발견")
    st.caption("분석에서 나온 가장 중요한 결과만 추렸습니다.")
    c = st.columns(3)
    if att is not None:
        wk = att[att.is_weekend == 1]["attendance"].mean()
        wd = att[att.is_weekend == 0]["attendance"].mean()
        diff = (wk - wd) / wd * 100
        sm = att.groupby("stadium")["attendance"].mean()
        with c[0]:
            with st.container(border=True):
                st.markdown("**1 · 주말에 관중이 몰린다**")
                st.markdown(f"주말 평균이 평일보다 약 **{diff:.0f}% 높음** → 평일 관중 유도가 개선 포인트.")
        with c[1]:
            with st.container(border=True):
                st.markdown("**2 · 구장 동원력 격차가 크다**")
                st.markdown(f"최다 **{sm.idxmax()}({sm.max():,.0f}명)** vs 최소 **{sm.idxmin()}({sm.min():,.0f}명)**. 모델의 핵심 변수.")
    with c[2]:
        with st.container(border=True):
            st.markdown("**3 · 범용 감성 모델 실패 → LLM 전환**")
            st.markdown("범용 모델 검증 **39.5%**(실패) → Claude 어노테이터 전환, 사람이 직접 확인한 200건과 **75.5% 일치**. 2000건 라벨링.")

    with st.container(border=True):
        st.markdown("**종합 시사점** — 팬은 '기록 수치'보다 **극적 장면·스토리**에 반응하고, 관중은 주말·인기구장에 집중된다. "
                    "→ 앱은 ① 응원팀 기반 개인화 홈 ② 평일·저동원 경기 관심 유도 ③ 스토리 중심 콘텐츠 큐레이션이 필요. "
                    "(상세: 상단 메뉴 및 docs/)")


# ---------- 2. 관중 분석·예측 ----------
def render_attendance():
    inject(
        """
        <div class="kbo-pagehead">
          <div class="eyebrow">ATTENDANCE · 관중 분석 · 예측</div>
          <h1>관중은 언제·어디서 몰리나, 예측 가능한가</h1>
          <p>요일·구장·상대팀 정보로 경기별 관중수를 예측하고, 단순 baseline을 이기는지로 가치를 검증했습니다.</p>
        </div>
        """
    )
    if att is None:
        st.info("`python -m src.preprocess.build_dataset` 먼저 실행하세요.")
        return

    st.subheader("관중은 언제 몰리나요?")
    st.caption("요일별 평균 관중입니다. 주말(토·일)과 평일의 차이를 봅니다.")
    by_dow = att.groupby("dow")["attendance"].mean().reset_index()
    by_dow["요일"] = by_dow["dow"].map(DOW)
    fig = px.bar(by_dow, x="요일", y="attendance", labels={"attendance": "평균 관중"},
                 color_discrete_sequence=[NAVY])
    st.plotly_chart(style_fig(fig), use_container_width=True)
    wk = att[att.is_weekend == 1]["attendance"].mean()
    wd = att[att.is_weekend == 0]["attendance"].mean()
    with st.container(border=True):
        st.markdown(f"**발견.** 주말 평균({wk:,.0f}명)이 평일({wd:,.0f}명)보다 약 **{(wk-wd)/wd*100:.0f}% 높습니다.** "
                    "평일 경기 관심을 끌어올리는 것이 앱의 개선 포인트입니다.")

    st.subheader("관중은 어디서 몰리나요?")
    st.caption("구장별 평균 관중입니다. 구장 간 동원력 차이가 관중수를 가장 크게 좌우합니다.")
    sm = att.groupby("stadium")["attendance"].mean().sort_values().reset_index()
    fig = px.bar(sm, x="attendance", y="stadium", orientation="h",
                 labels={"attendance": "평균 관중", "stadium": "구장"},
                 color_discrete_sequence=[NAVY])
    st.plotly_chart(style_fig(fig, h=360), use_container_width=True)

    st.subheader("관중수를 예측할 수 있나요?")
    st.caption("요일·구장·상대팀 정보로 경기별 관중수를 예측하는 XGBoost 모델입니다. "
               "'그냥 평균'과 '구장별 평균'이라는 단순 기준(baseline)을 모델이 이기는지로 가치를 검증했습니다.")
    # 용어 설명
    with st.container(border=True):
        st.markdown(
            "**용어** — "
            "**MAE**: 실제 관중과 예측이 평균적으로 벌어진 사람 수(작을수록 정확) · "
            "**MAPE**: 그 오차를 비율(%)로 본 값 · "
            "**baseline**: 모델과 비교하는 단순 기준값"
        )
    if _mae is None:
        st.info("`python -m src.analysis.attendance_forecast` 실행 시 표시됩니다.")
        return
    mae, test, pred = _mae
    cc = st.columns(2)
    with cc[0]:
        with st.container(border=True):
            st.metric("테스트 MAE", f"{mae:,.0f}명")
            st.caption("평균적으로 실제 관중과 이만큼 차이. 작을수록 정확.")
    with cc[1]:
        with st.container(border=True):
            st.markdown("**검증 방식**")
            st.caption("시즌을 시간순으로 나눠 뒤쪽을 테스트로 사용(미래로 과거 예측하는 누수 방지). "
                       "전체평균·구장별평균 baseline과 비교.")
    comp = pd.DataFrame({"실제": test["attendance"].values, "예측": pred})
    fig = px.scatter(comp, x="실제", y="예측", labels={"실제": "실제 관중", "예측": "예측 관중"},
                     color_discrete_sequence=[NAVY2], opacity=0.6)
    fig.add_shape(type="line", x0=comp["실제"].min(), y0=comp["실제"].min(),
                  x1=comp["실제"].max(), y1=comp["실제"].max(),
                  line=dict(color=RED, width=2.5, dash="dash"))
    fig.add_annotation(x=comp["실제"].max(), y=comp["실제"].max(), text="완벽 예측선",
                       showarrow=False, font=dict(color=RED, size=12), yshift=12, xanchor="right")
    st.plotly_chart(style_fig(fig, h=380), use_container_width=True)
    st.caption("점이 빨간 선(실제=예측)에 가까울수록 예측이 정확합니다.")

    with st.container(border=True):
        st.markdown("**시사점.** 관중 예측 결과를 앱의 '오늘의 추천 경기' 노출, 평일 경기 관심 유도에 활용 가능. (docs/05)")


# ---------- 3. 팬 감성·반응 ----------
def render_sentiment():
    inject(
        """
        <div class="kbo-pagehead">
          <div class="eyebrow">SENTIMENT · 팬 감성 · 반응</div>
          <h1>팬은 무엇에 반응하고, 무엇을 말하나</h1>
          <p>하이라이트 댓글을 분석했습니다. 검증에 실패한 범용 모델을 인정하고, 더 적합한 LLM으로 전환했습니다.</p>
        </div>
        """
    )
    if sent is None:
        st.info("`python -m src.analysis.sentiment` 먼저 실행하세요.")
        return

    st.warning(
        "**범용 감성 모델은 신뢰도가 낮아 그대로 쓰지 않았습니다.**\n\n"
        "사람이 직접 확인한 200건으로 검증한 결과 **정확도 39.5%**로 무조건 한 쪽으로 찍는 기준(58.5%)보다도 낮았고, "
        "야구 은어(사이다·개추 등)를 부정으로 잘못 분류했습니다. "
        "→ 한국어 맥락을 잘 읽는 **Claude로 다시 라벨링**해 신뢰도를 확보했습니다. (아래 분포는 한계를 보여주는 참고용)"
    )
    dist = sent["sentiment"].value_counts().reset_index()
    dist.columns = ["sentiment", "count"]
    fig = px.bar(dist, x="sentiment", y="count", color="sentiment",
                 labels={"sentiment": "감성", "count": "댓글 수"},
                 color_discrete_map=SENT_COLORS)
    st.plotly_chart(style_fig(fig), use_container_width=True)

    llm = io.load_llm_sentiment()
    if llm is not None:
        meta = io.load_llm_sentiment_meta() or {}
        st.subheader("LLM 기반 감성 분포 (신뢰)")
        ag = meta.get("agreement")
        cap = (f"Claude로 라벨링. **사람이 직접 확인한 {meta.get('n_validated','?')}건과 일치율 {ag*100:.1f}%**"
               if ag else "Claude로 라벨링.")
        st.caption(cap + " — 범용 모델(39.5%)보다 신뢰할 수 있는 분포입니다.")
        d2 = llm["llm_sentiment"].value_counts().reset_index()
        d2.columns = ["sentiment", "count"]
        cc = st.columns([1, 1])
        with cc[0]:
            fig = px.bar(d2, x="sentiment", y="count", color="sentiment",
                         labels={"sentiment": "감성", "count": "댓글 수"},
                         color_discrete_map=SENT_COLORS)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        if {"team1", "team2"}.issubset(llm.columns):
            long = pd.concat([
                llm[["team1", "llm_sentiment"]].rename(columns={"team1": "team"}),
                llm[["team2", "llm_sentiment"]].rename(columns={"team2": "team"}),
            ]).reset_index(drop=True)
            ct = long.groupby(["team", "llm_sentiment"]).size().reset_index(name="count")
            with cc[1]:
                fig = px.bar(ct, x="team", y="count", color="llm_sentiment",
                             barmode="stack", labels={"count": "댓글 수", "team": "팀"},
                             color_discrete_map=SENT_COLORS)
                st.plotly_chart(style_fig(fig), use_container_width=True)
        st.caption("⚠ 팀별은 매치업 단위(상대팀 포함) — 경기 반응으로 해석.")

    err = io.load_error_analysis()
    if err is not None and not err.empty and {"label", "claude"}.issubset(err.columns):
        with st.expander("🔍 오분류 분석 — Claude가 사람과 어디서 갈렸나 (일치율 75.5%의 '나머지')"):
            n = len(err)
            to_neu = int((err["claude"] == "neutral").sum())
            flips = int((((err["label"] == "positive") & (err["claude"] == "negative")) |
                        ((err["label"] == "negative") & (err["claude"] == "positive"))).sum())
            st.markdown(f"- 불일치 **{n}건** 중 **{to_neu}건({to_neu/n*100:.0f}%)**이 Claude가 '중립'으로 "
                        "물러난 경우 — 비꼼·인사이더 은어·암시적 감정")
            st.markdown(f"- 긍↔부 **극성 반전은 {flips}건뿐** → 모델이 방향을 틀리는 게 아니라 세기·모호함에서 갈림")
            dirs = (err.groupby(["label", "claude"]).size().reset_index(name="건수")
                    .sort_values("건수", ascending=False))
            st.dataframe(dirs, use_container_width=True, hide_index=True)
            st.caption("일부 불일치는 사람끼리도 갈리는 라벨 주관성 영역. "
                       "이 수치는 정답 대비가 아니라 사람 어노테이터 1명과의 '일치율' 기준이다.")

    st.subheader("그래서, 팬들은 무엇을 이야기하나요? (키워드 빈도)")
    st.caption("감성 모델과 달리 단어 빈도는 모델 추정이 아니라 직접 집계라 신뢰할 수 있습니다. "
               "댓글에 자주 등장한 단어로 '팬 관심사'를 봅니다.")
    if kw is None:
        st.info("`python -m src.analysis.keyword_freq` 실행 시 표시됩니다.")
    else:
        st.metric("가장 많이 언급된 단어", str(kw.iloc[0]["word"]), f"{int(kw.iloc[0]['count']):,}회")
        top = kw.head(20).sort_values("count")
        fig = px.bar(top, x="count", y="word", orientation="h",
                     labels={"count": "빈도", "word": "키워드"}, color_discrete_sequence=[NAVY])
        st.plotly_chart(style_fig(fig, h=420), use_container_width=True)
        if by_team is not None and not by_team.empty:
            team = st.selectbox("팀별 키워드 보기", sorted(by_team["team"].unique()))
            sub = by_team[by_team["team"] == team].head(15).sort_values("count")
            fig = px.bar(sub, x="count", y="word", orientation="h",
                         labels={"count": "빈도", "word": "키워드"}, color_discrete_sequence=[NAVY2])
            st.plotly_chart(style_fig(fig, h=360), use_container_width=True)

    st.subheader("AI 팬 반응 요약 (Claude)")
    st.caption("범용 모델이 슬랭에 실패해, 한국어 맥락을 잘 읽는 LLM으로 정성 요약했습니다. "
               "주어진 댓글에만 근거하도록 그라운딩했습니다. "
               "⚠ 하이라이트는 두 팀이 함께 등장 → 매치업(경기) 단위 반응이며 상대팀 선수가 섞일 수 있습니다.")
    if fan is None:
        st.info("`python -m src.analysis.llm_fan_report` 실행 시 표시됩니다. (.env에 ANTHROPIC_API_KEY 필요)")
    else:
        teams = [k for k in fan.keys() if not k.startswith("_")]
        if teams:
            t = st.selectbox("팀 선택", sorted(teams), key="fan")
            with st.container(border=True):
                st.markdown(fan[t])

    with st.container(border=True):
        st.markdown("**시사점.** 팬은 극적 장면·스토리에 반응. 자주 언급되는 선수·상황을 앱 콘텐츠·푸시 주제 선정에 활용. (docs/05)")


# ---------- 4. 콘텐츠 이용 ----------
def render_content():
    inject(
        """
        <div class="kbo-pagehead">
          <div class="eyebrow">CONTENT · 콘텐츠 이용</div>
          <h1>어떤 하이라이트가 팬 반응을 끄나</h1>
          <p>영상별 댓글·좋아요로 '반응이 큰 콘텐츠 유형'을 찾아 앱 홈 추천 정렬에 활용합니다.</p>
        </div>
        """
    )
    data = com if com is not None else sent  # 배포 시 원시 댓글 대신 감성 결과(제목·좋아요 포함) 사용
    if data is None:
        st.info("`python -m src.collect.youtube_comments` 먼저 실행하세요.")
        return
    if "title" not in data.columns:
        st.info("영상 제목 정보가 없습니다.")
        return
    agg = (data.groupby("title")
           .agg(댓글수=("text", "count"), 좋아요합=("like_count", "sum"))
           .sort_values("댓글수", ascending=False))
    cc = st.columns(2)
    kpi(cc[0], "분석한 하이라이트 영상", f"{agg.shape[0]:,}편", None, "댓글을 수집한 영상 수")
    kpi(cc[1], "가장 반응이 많았던 영상", f"{int(agg['댓글수'].max()):,}건", None, str(agg.index[0]))
    st.subheader("영상별 댓글 수 (상위 15)")
    st.caption("댓글·좋아요가 많은 영상일수록 팬 관심이 큰 콘텐츠 유형입니다.")
    top = agg.head(15).reset_index()
    fig = px.bar(top.sort_values("댓글수"), x="댓글수", y="title", orientation="h",
                 labels={"title": "영상"}, color_discrete_sequence=[NAVY])
    st.plotly_chart(style_fig(fig, h=420), use_container_width=True)
    st.dataframe(top, use_container_width=True, hide_index=True)
    with st.container(border=True):
        st.markdown("**시사점.** 반응이 큰 콘텐츠 유형을 앱 홈 추천 정렬 상단에 배치 → 사용자가 앱에 더 오래 머무름. (docs/05 · F-04)")


# ---------- 5. 분석 → 제언 ----------
def render_conclusion():
    inject(
        """
        <div class="kbo-pagehead">
          <div class="eyebrow">CONCLUSION · 분석 → 제언</div>
          <h1>분석을 했더니 → 이렇게 고쳐야 → 나아가야 할 방향</h1>
          <p>앞 페이지의 분석 결과를 앱 개선으로 잇는 종합 제언입니다.</p>
        </div>
        """
    )

    st.subheader("1. 분석을 했더니")
    c = st.columns(2)
    with c[0]:
        with st.container(border=True):
            st.markdown("**관중은 주말·인기구장에 집중**")
            if att is not None:
                wk = att[att.is_weekend == 1]["attendance"].mean()
                wd = att[att.is_weekend == 0]["attendance"].mean()
                sm = att.groupby("stadium")["attendance"].mean()
                st.markdown(f"주말이 평일보다 약 **{(wk-wd)/wd*100:.0f}% 많고**, 구장 격차도 큼"
                            f"({sm.idxmax()}↔{sm.idxmin()}). 모델로 구장별평균 대비 +16% 예측.")
            else:
                st.markdown("주말·인기구장 집중. 모델로 구장별평균 대비 +16% 예측.")
    with c[1]:
        with st.container(border=True):
            st.markdown("**팬은 '기록'보다 '스토리'에 반응**")
            st.markdown("끝내기·역전·육성 데뷔 같은 극적 장면에 반응이 집중(LLM 요약·키워드 빈도).")
    c2 = st.columns(2)
    with c2[0]:
        with st.container(border=True):
            st.markdown("**감성은 '검증'이 핵심이었다**")
            ag = (io.load_llm_sentiment_meta() or {}).get("agreement")
            st.markdown(f"범용 모델 39.5%(실패) → Claude 어노테이터로 전환, 사람 판단 대비 **{ag*100:.1f}% 일치**."
                        if ag else "범용 모델 39.5%(실패) → Claude로 전환·검증.")
    with c2[1]:
        with st.container(border=True):
            st.markdown("**앱엔 개인화가 없다 (AI 챗봇은 이미 존재)**")
            st.markdown("전 사용자가 동일 홈, 응원팀 개인화 부재. AI 챗봇은 이미 있음(docs/01).")

    st.subheader("2. 그래서 이렇게 고쳐야 (발견 → 개선)")
    rec = pd.DataFrame([
        ["개인화 부재", "F-01 응원팀 기반 개인화 홈", "팀 선택 시 그 팀 일정·기록·콘텐츠 중심으로 홈 재배치", "상"],
        ["팬 기록 욕구", "F-03 개인 관람 기록", "직관·집관 기록과 개인 통계(승요력 등)", "상"],
        ["관중 편차·예측 가능", "F-02 추천 경기 카드", "'오늘 볼 만한 경기'를 개인화 노출", "상"],
        ["스토리에 반응", "F-04 콘텐츠 추천 정렬 · F-07 콘텐츠 태깅", "반응 많은 콘텐츠를 상단 정렬 + 팀·선수·상황 태깅", "중"],
        ["AI 챗봇 기존재", "F-08 기존 AI 챗봇 고도화", "이미 있는 챗봇을 응원팀 기반 질의·추천으로 확장", "중"],
    ], columns=["분석 발견", "개선안(기능)", "기능 설명", "우선순위"])
    st.table(rec)

    st.markdown("**기능 요구사항 전체 (F-01 ~ F-08)** — 'F-번호'는 기능 요구사항 정의서의 기능 ID입니다.")
    glo = pd.DataFrame([
        ["F-01", "응원팀 기반 개인화 홈", "팀 선택 시 일정·기록·콘텐츠 중심으로 홈 재배치", "상"],
        ["F-02", "추천 경기 카드", "'오늘 볼 만한 경기'를 개인화 노출", "상"],
        ["F-03", "개인 관람 기록", "직관·집관 기록과 개인 통계(승요력 등)", "상"],
        ["F-04", "콘텐츠 추천 정렬", "홈 탭 콘텐츠를 이용현황 기반으로 정렬", "중"],
        ["F-05", "팬 참여(예측·포인트)", "승부 예측·출석·퀴즈형 포인트", "중"],
        ["F-06", "팀 감성 추이 알림(운영자)", "부정 반응 급증 시 운영자에게 알림", "중"],
        ["F-07", "콘텐츠 태깅 체계", "팀·선수·상황 태그 부여(추천 기반 데이터)", "중"],
        ["F-08", "기존 AI 챗봇 고도화", "이미 있는 챗봇을 응원팀 기반 개인화로 확장", "중"],
    ], columns=["ID", "기능명", "설명", "우선순위"])
    st.table(glo)

    st.subheader("3. 나아가야 할 방향")
    cc = st.columns(3)
    with cc[0]:
        with st.container(border=True):
            st.markdown("**단기**")
            st.markdown("응원팀 개인화 홈 + 추천 경기 — 근거가 가장 명확하고 진입 빈도 최고")
    with cc[1]:
        with st.container(border=True):
            st.markdown("**중기**")
            st.markdown("스토리 중심 콘텐츠 큐레이션 + 기존 AI 챗봇 개인화 고도화")
    with cc[2]:
        with st.container(border=True):
            st.markdown("**데이터 과제**")
            st.markdown("순위·승률 피처(시점 누수 주의) · 감성 도메인 파인튜닝 · 실 행동로그 확보")

    with st.container(border=True):
        st.markdown("⚠ 제언은 협의 전 제안이며, 개인화 근거 일부는 합성 행동로그 기반입니다. "
                    "실서비스 적용에는 실데이터·유관 부서 협의가 필요합니다. (상세: docs/04 · docs/05)")


# ---------- 라우터 ----------
if page == "종합 대시보드":
    render_overview()
elif page == "관중 분석·예측":
    render_attendance()
elif page == "팬 감성·반응":
    render_sentiment()
elif page == "콘텐츠 이용":
    render_content()
else:
    render_conclusion()
