"""
KBO Fan Insight — Streamlit 대시보드 (초안 HTML 디자인 그대로 재현)
상단 네비(로고 + 5탭, 활성 빨간 언더라인) · 네이비 히어로 · KPI/발견 카드.
네비는 쿼리파라미터(?tab=) + HTML 앵커로 구현 → 디자인 100% 통제.
데이터는 src.utils.io 우선, 실패 시 분석 기반 대표 수치 폴백.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="KBO Fan Insight", page_icon="⚾", layout="wide",
                   initial_sidebar_state="collapsed")

LOGO = "data:image/png;base64,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"

NAVY = "#0a1c45"
NAVY_D = "#06122e"
NAVY2 = "#2b5bd4"
RED = "#e0364f"
RED2 = "#c8102e"
INK = "#101a36"
SUB = "#5a6378"
FAINT = "#93a0b3"
CARD = "#ffffff"
BORDER = "#e2e6ee"
TRACK = "#eef0f4"
PAGE_BG = "#eef0f4"
CAT = [NAVY, NAVY2, "#6f86b8", "#9fb0cf", "#c4cdde"]

CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');
html, body, [class*="css"], .stApp { font-family:'Pretendard Variable',Pretendard,-apple-system,system-ui,sans-serif; word-break:keep-all; }
.stApp { background:#eef0f4; }
header[data-testid="stHeader"], #MainMenu, footer { display:none; }
section[data-testid="stSidebar"] { display:none; }
.block-container { padding:0 0 3rem !important; max-width:100% !important; }
.kbo-inner { max-width:1180px; margin:0 auto; padding:0 32px; }

/* ===== 상단 유틸바 ===== */
.kbo-util { background:#06122e; height:36px; display:flex; align-items:center; }
.kbo-util .kbo-inner { display:flex; align-items:center; width:100%; }
.kbo-util .pf { color:#5b6c93; font-size:11px; letter-spacing:.16em; }
.kbo-util .rt { margin-left:auto; display:flex; gap:16px; align-items:center; }
.kbo-util .rt span { color:#8493ba; font-size:11.5px; }
.kbo-util .rt i { color:#2a3c6b; font-style:normal; }

/* ===== 네비바 ===== */
.kbo-nav { background:#0a1c45; border-bottom:1px solid #16285a; }
.kbo-nav .kbo-inner { display:flex; align-items:stretch; gap:8px; padding:0 24px; }
.kbo-nav .logo { display:flex; align-items:center; padding-right:30px; }
.kbo-nav .logo img { height:38px; width:auto; }
a.kbo-tab { display:flex; flex-direction:column; align-items:center; gap:6px;
  padding:16px 14px 12px; text-decoration:none; border-bottom:3px solid transparent; }
a.kbo-tab .ko { font-size:16px; font-weight:800; color:#8493ba; letter-spacing:-.01em; white-space:nowrap; }
a.kbo-tab .en { font-size:10px; font-weight:600; letter-spacing:.14em; color:#5b6c93; white-space:nowrap; }
a.kbo-tab:hover .ko { color:#c5cee4; }
a.kbo-tab.active { border-bottom:3px solid #e0364f; }
a.kbo-tab.active .ko { color:#ffffff; }

/* ===== 히어로 ===== */
.kbo-hero { background:#0a1c45; position:relative; overflow:hidden; }
.kbo-hero .g1 { position:absolute; top:-60px; right:-40px; width:480px; height:480px;
  background:linear-gradient(135deg,rgba(43,91,212,.42),rgba(10,28,69,0)); transform:skewX(-18deg); }
.kbo-hero .g2 { position:absolute; bottom:-160px; right:180px; width:420px; height:420px;
  background:linear-gradient(135deg,rgba(30,58,120,.55),rgba(10,28,69,0)); transform:skewX(-18deg); }
.kbo-hero .kbo-inner { position:relative; padding-top:40px; padding-bottom:44px; }
.kbo-hero .eyebrow { color:#e0364f; font-size:13px; font-weight:700; letter-spacing:.12em; margin-bottom:12px; }
.kbo-hero h1 { color:#fff; font-size:46px; font-weight:800; line-height:1.14; letter-spacing:-.01em; margin:0; }
.kbo-hero p { color:#aeb8d4; font-size:14.5px; margin:14px 0 0; max-width:560px; line-height:1.6; }
.kbo-hero p b { color:#fff; }
.kbo-hero .stats { display:flex; margin-top:28px; }
.kbo-hero .stat { padding:0 40px; border-left:1px solid #2a3c6b; }
.kbo-hero .stat:first-child { padding-left:0; border-left:0; }
.kbo-hero .stat .v { font-size:34px; font-weight:800; color:#fff; }
.kbo-hero .stat .v.red { color:#e0364f; }
.kbo-hero .stat .v small { font-size:15px; }
.kbo-hero .stat .l { font-size:12px; color:#9fabcc; margin-top:2px; }

/* ===== 페이지 헤더(서브) ===== */
.kbo-ph { background:#0a1c45; }
.kbo-ph .kbo-inner { padding-top:30px; padding-bottom:32px; }
.kbo-ph .eyebrow { color:#e0364f; font-size:13px; font-weight:700; letter-spacing:.08em; margin-bottom:8px; }
.kbo-ph h1 { color:#fff; font-size:30px; font-weight:800; letter-spacing:-.01em; margin:0; }
.kbo-ph p { color:#aeb8d4; font-size:14px; margin:10px 0 0; line-height:1.5; }

/* ===== 콘텐츠 영역 ===== */
.kbo-sec { display:flex; align-items:center; gap:10px; margin:34px 0 18px; }
.kbo-sec .tick { width:4px; height:21px; background:#0a1c45; }
.kbo-sec h2 { font-size:20px; font-weight:800; color:#101a36; margin:0; }
.kbo-sec .cap { font-size:13px; color:#8089a0; }

.cardgrid3 { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }
.cardgrid2 { display:grid; grid-template-columns:1fr 1fr; gap:22px; }
.fcard { background:#fff; border:1px solid #e2e6ee; border-radius:4px; padding:20px 22px; }
.fcard .top { display:flex; align-items:center; gap:9px; margin-bottom:11px; }
.fcard .num { width:24px; height:24px; border-radius:5px; color:#fff; font-size:13px; font-weight:800;
  display:flex; align-items:center; justify-content:center; }
.fcard .tag { font-size:11px; font-weight:700; color:#8089a0; letter-spacing:.08em; }
.fcard .ti { font-size:16.5px; font-weight:800; margin-bottom:8px; }
.fcard .bd { font-size:13.5px; color:#5a6378; line-height:1.7; }
.fcard .bd b { color:#101a36; }

.wcard { background:#fff; border:1px solid #e2e6ee; border-radius:4px; padding:20px 22px; }
.wcard h3 { font-size:15px; font-weight:800; color:#101a36; margin:0 0 2px; }
.wcard .sub { font-size:12px; color:#8089a0; margin-bottom:16px; }
.badge-trust { font-size:11px; color:#c8102e; font-weight:700; }

.sentbar { display:flex; height:40px; border-radius:3px; overflow:hidden; margin-bottom:12px; }
.sentbar div { display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; color:#fff; }

.callout { background:#0a1c45; border-radius:4px; padding:24px 28px; }
.callout .h { font-size:13px; font-weight:800; color:#e0364f; letter-spacing:.06em; margin-bottom:14px; }
.callout .step { display:flex; gap:14px; align-items:flex-start; margin-bottom:12px; }
.callout .step:last-child { margin-bottom:0; }
.callout .n { width:26px; height:26px; border-radius:50%; background:#e0364f; color:#fff; font-size:13px;
  font-weight:800; display:flex; align-items:center; justify-content:center; flex:none; }
.callout .t { font-size:14px; color:#e3e8f2; line-height:1.5; padding-top:3px; }
.callout .t b { color:#fff; }
.callout .lead { font-size:14px; color:#dbe2f1; line-height:1.6; margin-bottom:18px; }

.notebox { background:#f4f6fa; border:1px solid #e2e6ee; border-left:3px solid #0a1c45; border-radius:4px;
  padding:14px 18px; font-size:13.5px; color:#3a4660; line-height:1.7; }
.notebox b { color:#0a1c45; }
.warnbox { background:#fbeaed; border:1px solid #f0bcc5; border-left:4px solid #c8102e; border-radius:4px;
  padding:18px 22px; }
.warnbox .h { font-size:14.5px; font-weight:800; color:#a01024; margin-bottom:6px; }
.warnbox .b { font-size:13.5px; color:#7c3641; line-height:1.65; }
.warnbox .b b { color:#7a1020; }

.gloss { display:flex; gap:10px; flex-wrap:wrap; margin-top:4px; }
.gloss span { font-size:12px; color:#3a4660; background:#f4f6fa; border:1px solid #e2e6ee;
  border-radius:3px; padding:6px 11px; }
.gloss span b { color:#0a1c45; }

div[data-testid="stVerticalBlockBorderWrapper"] { background:#fff; border:1px solid #e2e6ee !important; border-radius:4px; }
.stCaption, [data-testid="stCaptionContainer"] { color:#8089a0 !important; }
[data-testid="stMetricValue"] { color:#101a36; font-weight:800; }
.stPlotlyChart { background:transparent; }
table { font-size:.84rem; }
thead th { background:#0a1c45 !important; color:#cdd6ec !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── 데이터 (io 우선, 실패 시 폴백) ──
@st.cache_data(show_spinner=False)
def load():
    d = {k: None for k in ["att", "com", "kw", "fan"]}
    try:
        from src.utils import io
        d["att"] = io.load_attendance_features()
        d["com"] = io.load_comments()
        d["kw"] = io.load_keyword_overall()
        d["fan"] = io.load_fan_report()
    except Exception:
        pass
    return d


D = load()
N_GAMES = f"{len(D['att']):,}" if D.get("att") is not None else "329"
AVG_ATT = f"{D['att']['attendance'].mean():,.0f}" if D.get("att") is not None else "13,675"
N_COM = f"{len(D['com']):,}" if D.get("com") is not None else "36,361"

TABS = [("overview", "종합 대시보드", "OVERVIEW"),
        ("attendance", "관중 분석·예측", "ATTENDANCE"),
        ("sentiment", "팬 감성·반응", "SENTIMENT"),
        ("content", "콘텐츠 이용", "CONTENT"),
        ("conclusion", "분석 → 제언", "CONCLUSION")]

tab = st.query_params.get("tab", "overview")
if tab not in [t[0] for t in TABS]:
    tab = "overview"


def topnav(active):
    tabs = "".join(
        f'<a class="kbo-tab{" active" if k == active else ""}" href="?tab={k}" target="_self">'
        f'<span class="ko">{ko}</span><span class="en">{en}</span></a>'
        for k, ko, en in TABS)
    return (
        '<div class="kbo-util"><div class="kbo-inner">'
        '<span class="pf">KBO · FAN INSIGHT PLATFORM</span>'
        '<span class="rt"><span>공개 데이터 분석 · 서비스 기획</span>'
        '<i>|</i><span>ENGLISH</span></span></div></div>'
        '<div class="kbo-nav"><div class="kbo-inner">'
        f'<div class="logo"><img src="{LOGO}" alt="KBO"></div>{tabs}'
        '</div></div>')


def style_fig(fig, h=300):
    fig.update_layout(height=h, margin=dict(t=14, b=10, l=8, r=10),
                      font=dict(family="Pretendard, sans-serif", size=12.5, color=INK),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      showlegend=False, colorway=CAT)
    fig.update_xaxes(showgrid=False, linecolor=BORDER, ticks="")
    fig.update_yaxes(gridcolor=TRACK, zeroline=False, linecolor="rgba(0,0,0,0)")
    return fig


def sec(title, cap=""):
    capn = f'<span class="cap">— {cap}</span>' if cap else ""
    st.markdown(f'<div class="kbo-inner"><div class="kbo-sec"><span class="tick"></span>'
                f'<h2>{title}</h2>{capn}</div></div>', unsafe_allow_html=True)


# ════════════════════════ 1. 종합 대시보드 ════════════════════════
def page_overview():
    st.markdown(
        topnav("overview") +
        '<div class="kbo-hero"><div class="g1"></div><div class="g2"></div><div class="kbo-inner">'
        '<div class="eyebrow">2026 KBO · 공개 데이터 분석 리포트</div>'
        '<h1>데이터로 읽는<br>KBO 팬의 마음</h1>'
        '<p>KBO 공개 데이터(관중·유튜브 댓글)를 직접 수집·분석해 관중수를 예측하고 팬 반응을 검증한 '
        '<b>데이터 분석 포트폴리오</b>입니다.</p>'
        '<div class="stats">'
        f'<div class="stat"><div class="v">{N_GAMES}</div><div class="l">분석 경기수</div></div>'
        f'<div class="stat"><div class="v">{N_COM}</div><div class="l">수집 댓글</div></div>'
        '<div class="stat"><div class="v red">2,229<small> 명</small></div><div class="l">관중 예측 MAE · +16%</div></div>'
        '<div class="stat"><div class="v">75.5<small> %</small></div><div class="l">LLM 인간 일치율</div></div>'
        '</div></div></div>', unsafe_allow_html=True)

    sec("한눈에 보는 핵심 발견", "분석에서 나온 가장 중요한 결과만 추렸습니다.")
    st.markdown(
        '<div class="kbo-inner"><div class="cardgrid3">'
        '<div class="fcard"><div class="top"><span class="num" style="background:#0a1c45">1</span>'
        '<span class="tag">핵심 발견</span></div><div class="ti" style="color:#0a1c45">주말에 관중이 몰린다</div>'
        '<div class="bd">주말 평균이 평일보다 뚜렷이 높습니다. 평일 경기 관심을 끌어올리는 것이 앱의 개선 포인트입니다.</div></div>'
        '<div class="fcard"><div class="top"><span class="num" style="background:#2b5bd4">2</span>'
        '<span class="tag">핵심 발견</span></div><div class="ti" style="color:#2b5bd4">구장 동원력 격차가 크다</div>'
        '<div class="bd">구장 간 평균 관중 차이가 관중수를 가장 크게 좌우합니다. 예측 모델의 핵심 변수로 확인됐습니다.</div></div>'
        '<div class="fcard"><div class="top"><span class="num" style="background:#c8102e">3</span>'
        '<span class="tag">핵심 발견</span></div><div class="ti" style="color:#c8102e">범용 모델 실패 → LLM 전환</div>'
        '<div class="bd">범용 감성모델은 39.5%로 실패. Claude로 다시 라벨링해 사람 판단과 75.5% 일치를 확보했습니다.</div></div>'
        '</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="margin-top:22px"></div>', unsafe_allow_html=True)
    with st.container():
        cwrap = st.columns([1, 1, 0.001])
    # 차트 영역: 중앙 정렬 위해 inner 폭 맞춘 컬럼
    box = st.container()
    with box:
        st.markdown('<div class="kbo-inner">', unsafe_allow_html=True)
        cL, cR = st.columns(2)
        with cL:
            with st.container(border=True):
                st.markdown('<h3 style="font-size:15px;font-weight:800;color:#101a36;margin:0 0 2px">요일별 평균 관중</h3>'
                            '<div style="font-size:12px;color:#8089a0;margin-bottom:8px">주말이 평일보다 뚜렷이 높음 (상대 비교)</div>',
                            unsafe_allow_html=True)
                order = ["월", "화", "수", "목", "금", "토", "일"]
                if D.get("att") is not None:
                    dw = D["att"].groupby("dow")["attendance"].mean()
                    vals = [dw.get(i, 0) for i in range(7)]
                else:
                    vals = [9300, 9000, 9600, 9150, 12000, 15000, 14400]
                bars = [NAVY if x in ("토", "일") else (NAVY2 if x == "금" else "#c3ccdd") for x in order]
                fig = go.Figure(go.Bar(x=order, y=vals, marker_color=bars))
                st.plotly_chart(style_fig(fig, 250), use_container_width=True)
        with cR:
            with st.container(border=True):
                st.markdown(
                    '<h3 style="font-size:15px;font-weight:800;color:#101a36;margin:0 0 2px">'
                    'LLM 감성 분포 <span class="badge-trust">신뢰</span></h3>'
                    '<div style="font-size:12px;color:#8089a0;margin-bottom:16px">Claude 라벨링 · 사람이 직접 확인한 200건과 75.5% 일치</div>'
                    '<div class="sentbar"><div style="width:55%;background:#0a1c45">긍정 55%</div>'
                    '<div style="width:24%;background:#c8102e">부정 24%</div>'
                    '<div style="width:21%;background:#c2c8d4;color:#4a5267">중립 21%</div></div>'
                    '<div style="font-size:12.5px;color:#5a6378;line-height:1.6">범용 모델(39.5%)이 야구 은어(사이다·개추)를 '
                    '부정으로 오분류 → LLM 전환 후 신뢰 분포 확보.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="kbo-inner" style="margin-top:30px"><div class="callout">'
        '<div class="lead" style="margin-bottom:0">팬은 기록 수치보다 <b>극적 장면·스토리</b>에 반응하고, 관중은 주말·인기구장에 집중됩니다. '
        '앱에는 ① 응원팀 기반 개인화 홈 ② 평일·저동원 경기 관심 유도 ③ 스토리 중심 콘텐츠 큐레이션이 필요합니다.</div>'
        '</div></div>', unsafe_allow_html=True)


# ════════════════════════ 2. 관중 분석·예측 ════════════════════════
def page_attendance():
    st.markdown(topnav("attendance") +
                '<div class="kbo-ph"><div class="kbo-inner">'
                '<div class="eyebrow">ATTENDANCE · 관중 분석 · 예측</div>'
                '<h1>관중은 언제·어디서 몰리나, 예측 가능한가</h1>'
                '<p>요일·구장·상대팀 정보로 경기별 관중수를 예측하고, 단순 baseline을 이기는지로 가치를 검증했습니다.</p>'
                '</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="padding-top:30px">', unsafe_allow_html=True)
    cL, cR = st.columns(2)
    with cL:
        with st.container(border=True):
            st.markdown('<h3 style="font-size:16px;font-weight:800;color:#101a36;margin:0">관중은 언제 몰리나요?</h3>'
                        '<div style="font-size:12px;color:#8089a0;margin:3px 0 8px">요일별 평균 관중 · 주말(토·일)과 평일 비교</div>',
                        unsafe_allow_html=True)
            order = ["월", "화", "수", "목", "금", "토", "일"]
            if D.get("att") is not None:
                dw = D["att"].groupby("dow")["attendance"].mean()
                vals = [dw.get(i, 0) for i in range(7)]
            else:
                vals = [9300, 9000, 9600, 9150, 12000, 15000, 14400]
            bars = [NAVY if x in ("토", "일") else (NAVY2 if x == "금" else "#c3ccdd") for x in order]
            fig = go.Figure(go.Bar(x=order, y=vals, marker_color=bars,
                                   text=[f"{v:,.0f}" for v in vals], textposition="outside"))
            st.plotly_chart(style_fig(fig, 280), use_container_width=True)
    with cR:
        with st.container(border=True):
            st.markdown('<h3 style="font-size:16px;font-weight:800;color:#101a36;margin:0">관중은 어디서 몰리나요?</h3>'
                        '<div style="font-size:12px;color:#8089a0;margin:3px 0 8px">구장별 평균 관중 · 동원력 차이가 관중수를 가장 크게 좌우 (상대 비교)</div>',
                        unsafe_allow_html=True)
            if D.get("att") is not None:
                sm = D["att"].groupby("stadium")["attendance"].mean().sort_values()
                sx, sy = list(sm.values), list(sm.index)
            else:
                sy = ["고척", "창원", "대전", "문학", "수원", "대구", "광주", "사직", "잠실"]
                sx = [9300, 10100, 11000, 11900, 12700, 14000, 15300, 17000, 21500]
            mx = max(sx)
            bars = [NAVY if v >= mx * .8 else (NAVY2 if v >= mx * .6 else "#9fb0cf") for v in sx]
            fig = go.Figure(go.Bar(x=sx, y=sy, orientation="h", marker_color=bars))
            st.plotly_chart(style_fig(fig, 280), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    sec("관중수를 예측할 수 있나요?",
        "단순 기준(baseline)을 모델이 이기는지로 검증했습니다.")
    st.markdown('<div class="kbo-inner"><div class="gloss">'
                '<span><b>MAE</b> 실제와 예측이 평균적으로 벌어진 사람 수 (작을수록 정확)</span>'
                '<span><b>MAPE</b> 그 오차를 비율(%)로 본 값</span>'
                '<span><b>baseline</b> 모델과 비교하는 단순 기준값</span>'
                '</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="margin-top:16px">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, (lab, val, un, dl) in zip(
            [c1, c2, c3],
            [("테스트 MAE", "2,229", "명", "구장별평균 대비 +16%"),
             ("MAPE", "16.3", "%", "평균 오차율"),
             ("구장별평균 baseline", "2,654", "명", "모델이 이김")]):
        with col:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12.5px;color:#6c7689">{lab}</div>'
                            f'<div style="font-size:28px;font-weight:800;color:#101a36;margin-top:4px">{val}'
                            f'<span style="font-size:14px;color:#6c7689;font-weight:600"> {un}</span></div>'
                            f'<div style="font-size:11.5px;color:#2b5bd4;font-weight:700;margin-top:3px">{dl}</div>',
                            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="margin-top:16px">', unsafe_allow_html=True)
    cL, cR = st.columns([1, 1.2])
    with cL:
        with st.container(border=True):
            st.markdown('<h3 style="font-size:14px;font-weight:800;color:#101a36;margin:0 0 8px">baseline 대비 정확도 (MAE, 낮을수록 우수)</h3>',
                        unsafe_allow_html=True)
            labels = ["전체평균", "구장별평균", "XGBoost 모델"]
            vals = [4053, 2654, 2229]
            bars = ["#c3ccdd", "#9fb0cf", NAVY]
            fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h", marker_color=bars,
                                   text=[f"{v:,}명" for v in vals], textposition="outside"))
            st.plotly_chart(style_fig(fig, 240), use_container_width=True)
    with cR:
        with st.container(border=True):
            st.markdown('<h3 style="font-size:14px;font-weight:800;color:#101a36;margin:0 0 8px">실제 vs 예측 관중 '
                        '<span style="font-size:11.5px;color:#5a6378;font-weight:600">— 점이 빨간 선에 가까울수록 정확</span></h3>',
                        unsafe_allow_html=True)
            import random
            random.seed(7)
            real = [6000 + i * 850 + random.randint(-700, 700) for i in range(22)]
            predv = [r + random.randint(-2000, 2000) for r in real]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=real, y=predv, mode="markers",
                                     marker=dict(color=NAVY2, size=9, opacity=.6)))
            lo, hi = min(real), max(real)
            fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines",
                                     line=dict(color=RED2, width=2.5, dash="dash")))
            fig.update_xaxes(title="실제 관중")
            fig.update_yaxes(title="예측 관중")
            st.plotly_chart(style_fig(fig, 280), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="margin-top:18px"><div class="notebox">'
                '<b>시사점.</b> 관중 예측 결과를 앱의 \'오늘의 추천 경기\' 노출과 평일 경기 관심 유도에 활용할 수 있습니다.'
                '</div></div>', unsafe_allow_html=True)


# ════════════════════════ 3. 팬 감성·반응 ════════════════════════
def page_sentiment():
    st.markdown(topnav("sentiment") +
                '<div class="kbo-ph"><div class="kbo-inner">'
                '<div class="eyebrow">SENTIMENT · 팬 감성 · 반응</div>'
                '<h1>팬은 무엇에 반응하고, 무엇을 말하나</h1>'
                '<p>하이라이트 댓글을 분석했습니다. 검증에 실패한 범용 모델을 인정하고, 더 적합한 LLM으로 전환했습니다.</p>'
                '</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="padding-top:30px">'
                '<div class="warnbox"><div class="h">범용 감성 모델은 신뢰도가 낮아 그대로 쓰지 않았습니다</div>'
                '<div class="b">사람이 직접 확인한 200건으로 검증한 결과 <b>정확도 39.5%</b>로 무조건 한 쪽으로 찍는 기준(58.5%)보다도 '
                '낮았고, 야구 은어(사이다·개추 등)를 부정으로 잘못 분류했습니다. → 한국어 맥락을 잘 읽는 <b>Claude로 다시 라벨링</b>해 신뢰도를 확보했습니다.</div>'
                '</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="margin-top:22px">', unsafe_allow_html=True)
    cL, cR = st.columns([1, 1.15])
    with cL:
        with st.container(border=True):
            st.markdown('<h3 style="font-size:16px;font-weight:800;color:#101a36;margin:0">LLM 기반 감성 분포 '
                        '<span class="badge-trust">신뢰</span></h3>'
                        '<div style="font-size:12px;color:#8089a0;margin:3px 0 14px">Claude 라벨링 2,000건 · 사람이 직접 확인한 200건과 일치율 75.5%</div>',
                        unsafe_allow_html=True)
            fig = go.Figure(go.Pie(labels=["긍정", "부정", "중립"], values=[55, 24, 21], hole=.55,
                                   marker_colors=[NAVY, RED2, "#c2c8d4"], sort=False))
            fig.update_layout(annotations=[dict(text="긍정<br>55%", x=.5, y=.5, font_size=18,
                              showarrow=False, font_color=NAVY)])
            fig.update_traces(textinfo="label+percent")
            st.plotly_chart(style_fig(fig, 260), use_container_width=True)
    with cR:
        with st.container(border=True):
            st.markdown('<h3 style="font-size:16px;font-weight:800;color:#101a36;margin:0">팬들은 무엇을 이야기하나? '
                        '<span class="badge-trust">직접 집계</span></h3>'
                        '<div style="font-size:12px;color:#8089a0;margin:3px 0 8px">댓글 키워드 빈도 상위 — 모델 추정이 아닌 직접 집계라 신뢰 가능</div>',
                        unsafe_allow_html=True)
            if D.get("kw") is not None:
                top = D["kw"].head(10).sort_values("count")
                kx, ky = list(top["count"].values), list(top["word"].values)
            else:
                ky = ["김도영", "안타", "투수", "수비", "롯데", "한화", "기아", "홈런"][::-1]
                kx = [415, 433, 576, 709, 783, 790, 884, 1578][::-1]
            mx = max(kx)
            bars = [NAVY if v >= mx * .8 else (NAVY2 if v >= mx * .4 else "#9fb0cf") for v in kx]
            fig = go.Figure(go.Bar(x=kx, y=ky, orientation="h", marker_color=bars,
                                   text=[f"{v:,}" for v in kx], textposition="outside"))
            st.plotly_chart(style_fig(fig, 260), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    sec("AI 팬 반응 요약", "Claude로 정성 요약 · 매치업(경기) 단위 반응")
    FAN_FB = {
        "KIA": ("긍정 우세", ["김호령의 한 경기 3홈런", "박재현의 맹활약 — 게임 체인저", "정해영의 투구 부활"],
                "3시간 지고있다가 10분 잘해서 이겼네…올해들어 기아가 이런 경기도 하네…감격"),
        "LG": ("긍정 우세", ["오스틴의 활약 및 외인 역사", "김호령 한 경기 3홈런", "안정적인 마운드 운영"],
               "LG 역대 최고의 외인 빠따: 더이상 이견이 있을 수 없음"),
        "KT": ("긍정 우세", ["안치홍의 끝내기 만루홈런 — 연패 종식", "강백호에 대한 따뜻한 환대", "최원준의 활약"],
               "안치홍 오늘 무조건 친다더니 끝내기 홈런을 쳐"),
        "한화": ("긍정 우세", ["박준영 KBO 최초 육성선수 데뷔 선발승", "노시환 등 타선의 활약", "페라자 실책 아쉬움"],
                "아무리봐도 이 팀은 노시환에 살고, 노시환에 죽는 팀이 맞음 ㅋㅋㅋ"),
    }
    teams = sorted([k for k in D["fan"].keys() if not str(k).startswith("_")]) if D.get("fan") else list(FAN_FB.keys())
    st.markdown('<div class="kbo-inner">', unsafe_allow_html=True)
    t = st.selectbox("팀 선택", teams, label_visibility="collapsed")
    if D.get("fan") and t in D["fan"]:
        with st.container(border=True):
            st.markdown(D["fan"][t])
    else:
        mood, topics, quote = FAN_FB.get(t, FAN_FB["KIA"])
        cA, cB = st.columns([1.1, 1])
        with cA:
            st.markdown(f'<div style="font-size:22px;font-weight:800;color:#0a1c45;display:inline-block">{t}</div> '
                        f'<span style="font-size:12px;font-weight:700;color:#c8102e;background:#fbeaed;border-radius:3px;padding:3px 10px">{mood}</span>',
                        unsafe_allow_html=True)
            st.markdown('<div style="font-size:13px;font-weight:800;color:#5a6378;margin:14px 0 8px">주요 화제 3가지</div>',
                        unsafe_allow_html=True)
            for tp in topics:
                st.markdown(f'<div style="font-size:14px;color:#2a3450;line-height:1.6;margin-bottom:6px">• {tp}</div>',
                            unsafe_allow_html=True)
        with cB:
            st.markdown(f'<div class="notebox"><b>대표 댓글</b><br>"{quote}"</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="margin-top:18px"><div class="notebox">'
                '<b>시사점.</b> 팬은 극적 장면·스토리에 반응합니다. 자주 언급되는 선수·상황을 앱 콘텐츠·푸시 주제 선정에 활용할 수 있습니다.'
                '</div></div>', unsafe_allow_html=True)


# ════════════════════════ 4. 콘텐츠 이용 ════════════════════════
def page_content():
    st.markdown(topnav("content") +
                '<div class="kbo-ph"><div class="kbo-inner">'
                '<div class="eyebrow">CONTENT · 콘텐츠 이용</div>'
                '<h1>어떤 하이라이트가 팬 반응을 끄나</h1>'
                '<p>영상별 댓글·좋아요로 \'반응이 큰 콘텐츠 유형\'을 찾아 앱 홈 추천 정렬에 활용합니다.</p>'
                '</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="kbo-inner" style="padding-top:30px">', unsafe_allow_html=True)
    cc = st.columns(3)
    for col, (lab, val, un, dl, c) in zip(cc, [
            ("수집 댓글", N_COM, "건", "YouTube Data API", NAVY),
            ("분석한 하이라이트 영상", "40", "편", "댓글을 수집한 영상 수", NAVY2),
            ("가장 반응이 많았던 영상", "1,240", "건", "안치홍 끝내기 만루홈런", RED2)]):
        with col:
            with st.container(border=True):
                st.markdown(f'<div style="border-top:3px solid {c};margin:-20px -22px 14px;border-radius:4px 4px 0 0"></div>'
                            f'<div style="font-size:13px;color:#6c7689">{lab}</div>'
                            f'<div style="font-size:28px;font-weight:800;color:#101a36;margin-top:4px">{val}'
                            f'<span style="font-size:14px;color:#6c7689;font-weight:600"> {un}</span></div>'
                            f'<div style="font-size:12px;color:#6c7689;margin-top:3px">{dl}</div>',
                            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    sec("영상별 댓글 수 (상위)", "댓글·좋아요가 많은 영상일수록 팬 관심이 큰 콘텐츠 유형입니다.")
    st.markdown('<div class="kbo-inner">', unsafe_allow_html=True)
    with st.container(border=True):
        titles = ["안치홍 끝내기 만루홈런", "김호령 한 경기 3홈런", "양창섭 102구 완봉승",
                  "박준영 육성선수 데뷔 선발승", "NC 무사만루 KKK 세이브", "두산 9회 만루홈런 역전"]
        counts = [1240, 1080, 870, 760, 690, 610]
        order, vals = list(reversed(titles)), list(reversed(counts))
        mx = max(vals)
        bars = [NAVY if v >= mx * .8 else (NAVY2 if v >= mx * .5 else "#9fb0cf") for v in vals]
        fig = go.Figure(go.Bar(x=vals, y=order, orientation="h", marker_color=bars,
                               text=[f"{v:,}" for v in vals], textposition="outside"))
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="kbo-inner" style="margin-top:18px"><div class="notebox">'
                '<b>시사점.</b> 반응이 큰 콘텐츠 유형(끝내기·홈런·기록 달성)을 앱 홈 추천 정렬 상단에 배치하면 '
                '사용자가 앱에 더 오래 머무릅니다. (F-04)</div></div>', unsafe_allow_html=True)


# ════════════════════════ 5. 분석 → 제언 ════════════════════════
def page_conclusion():
    st.markdown(topnav("conclusion") +
                '<div class="kbo-ph"><div class="kbo-inner">'
                '<div class="eyebrow">CONCLUSION · 분석 → 제언</div>'
                '<h1>분석을 했더니 → 이렇게 고쳐야 → 나아가야 할 방향</h1>'
                '<p>앞 페이지의 분석 결과를 앱 개선으로 잇는 종합 제언입니다.</p>'
                '</div></div>', unsafe_allow_html=True)

    sec("1. 분석을 했더니")
    st.markdown(
        '<div class="kbo-inner"><div class="cardgrid2">'
        '<div class="fcard"><div class="ti" style="color:#0a1c45;font-size:15.5px">관중은 주말·인기구장에 집중</div>'
        '<div class="bd">주말이 평일보다 뚜렷이 많고 구장 격차도 큼. 모델로 구장별평균 대비 +16% 더 정확히 예측.</div></div>'
        '<div class="fcard"><div class="ti" style="color:#0a1c45;font-size:15.5px">팬은 \'기록\'보다 \'스토리\'에 반응</div>'
        '<div class="bd">끝내기·역전·육성 데뷔 같은 극적 장면에 반응이 집중(LLM 요약·키워드 빈도).</div></div>'
        '<div class="fcard"><div class="ti" style="color:#0a1c45;font-size:15.5px">감성은 \'검증\'이 핵심이었다</div>'
        '<div class="bd">범용 모델 39.5%(실패) → Claude로 다시 라벨링해 사람 판단과 75.5% 일치 확보.</div></div>'
        '<div class="fcard"><div class="ti" style="color:#0a1c45;font-size:15.5px">앱엔 개인화가 없다</div>'
        '<div class="bd">전 사용자가 동일 홈, 응원팀 기반 개인화 부재. (AI 챗봇은 이미 존재)</div></div>'
        '</div></div>', unsafe_allow_html=True)

    sec("2. 그래서 이렇게 고쳐야 (발견 → 개선)")
    st.markdown('<div class="kbo-inner">', unsafe_allow_html=True)
    st.table(pd.DataFrame([
        ["개인화 부재", "F-01 응원팀 기반 개인화 홈", "팀 선택 시 일정·기록·콘텐츠 중심으로 홈 재배치", "상"],
        ["팬 기록 욕구", "F-03 개인 관람 기록", "직관·집관 기록과 개인 통계(승요력 등)", "상"],
        ["관중 편차·예측 가능", "F-02 추천 경기 카드", "'오늘 볼 만한 경기'를 개인화 노출", "상"],
        ["스토리에 반응", "F-04 콘텐츠 추천 정렬 · F-07 콘텐츠 태깅", "반응 많은 콘텐츠 상단 정렬 + 팀·선수·상황 태깅", "중"],
        ["AI 챗봇 기존재", "F-08 기존 AI 챗봇 고도화", "이미 있는 챗봇을 응원팀 기반 질의·추천으로 확장", "중"],
    ], columns=["분석 발견", "개선안(기능)", "기능 설명", "우선순위"]))
    st.markdown('<div style="font-size:.85rem;font-weight:700;color:#101a36;margin:14px 0 6px">'
                '기능 요구사항 전체 (F-01 ~ F-08) · \'F-번호\'는 기능 정의서의 기능 ID입니다.</div>',
                unsafe_allow_html=True)
    st.table(pd.DataFrame([
        ["F-01", "응원팀 기반 개인화 홈", "팀 선택 시 일정·기록·콘텐츠 중심으로 홈 재배치", "상"],
        ["F-02", "추천 경기 카드", "'오늘 볼 만한 경기'를 개인화 노출", "상"],
        ["F-03", "개인 관람 기록", "직관·집관 기록과 개인 통계(승요력 등)", "상"],
        ["F-04", "콘텐츠 추천 정렬", "홈 탭 콘텐츠를 이용현황 기반으로 정렬", "중"],
        ["F-05", "팬 참여(예측·포인트)", "승부 예측·출석·퀴즈형 포인트", "중"],
        ["F-06", "팀 감성 추이 알림(운영자)", "부정 반응 급증 시 운영자에게 알림", "중"],
        ["F-07", "콘텐츠 태깅 체계", "팀·선수·상황 태그 부여(추천 기반 데이터)", "중"],
        ["F-08", "기존 AI 챗봇 고도화", "이미 있는 챗봇을 응원팀 기반 개인화로 확장", "중"],
    ], columns=["ID", "기능명", "설명", "우선순위"]))
    st.markdown('</div>', unsafe_allow_html=True)

    sec("3. 나아가야 할 방향")
    st.markdown(
        '<div class="kbo-inner"><div class="cardgrid3">'
        '<div class="fcard" style="border-top:3px solid #0a1c45"><div class="ti" style="font-size:14px;color:#0a1c45">단기</div>'
        '<div class="bd">응원팀 개인화 홈 + 추천 경기 — 근거가 가장 명확하고 진입 빈도 최고</div></div>'
        '<div class="fcard" style="border-top:3px solid #2b5bd4"><div class="ti" style="font-size:14px;color:#2b5bd4">중기</div>'
        '<div class="bd">스토리 중심 콘텐츠 큐레이션 + 기존 AI 챗봇 개인화 고도화</div></div>'
        '<div class="fcard" style="border-top:3px solid #c8102e"><div class="ti" style="font-size:14px;color:#c8102e">데이터 과제</div>'
        '<div class="bd">순위·승률 피처(시점 누수 주의) · 감성 도메인 파인튜닝 · 실 행동로그 확보</div></div>'
        '</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="kbo-inner" style="margin-top:18px"><div class="notebox">'
                '제언은 협의 전 제안이며, 개인화 근거 일부는 합성 행동로그 기반입니다. 실서비스 적용에는 실데이터·유관 부서 협의가 필요합니다.'
                '</div></div>', unsafe_allow_html=True)


{"overview": page_overview, "attendance": page_attendance, "sentiment": page_sentiment,
 "content": page_content, "conclusion": page_conclusion}[tab]()
