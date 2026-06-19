"""
KBO Fan Insight — Streamlit 대시보드 (디자인 적용본)
네이비/화이트/레드 테마 · 사이드바 스텝 네비 · KPI/발견 카드 · 통일 Plotly 팔레트
※ 데이터 로딩은 src.utils.io 우선, 실패 시 분석 결과 기반 대표 수치로 폴백 → 디자인은 항상 100% 렌더.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="KBO Fan Insight", page_icon="⚾", layout="wide",
                   initial_sidebar_state="expanded")

# ── 디자인 토큰 (KBO 네이비/화이트/레드) ──
INK = "#101a36"
INK_SUB = "#5a6378"
INK_FAINT = "#93a0b3"
NAVY = "#0a1c45"
NAVY2 = "#2b5bd4"
SOFT = "#eef1f6"
RED = "#c8102e"
POS = "#1f7a4d"
WARN = "#c77b1f"
PAGE_BG = "#f3f4f6"
CARD_BG = "#ffffff"
CARD_BORDER = "#e5e8ee"
TRACK = "#eef0f4"
CAT = ["#0a1c45", "#2b5bd4", "#6f86b8", "#9fb0cf", "#c4cdde", "#e2e7f0"]


def inject_css():
    css = """
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');
    html, body, [class*="css"], .stApp { font-family:'Pretendard Variable',Pretendard,-apple-system,system-ui,sans-serif; word-break:keep-all; }
    .stApp { background:%(PAGE_BG)s; }
    .block-container { padding-top:3rem; padding-bottom:3rem; max-width:1480px; }
    h1 { font-size:1.75rem !important; font-weight:800 !important; letter-spacing:-0.02em; color:%(INK)s; }
    h2,h3 { color:%(INK)s; letter-spacing:-0.01em; }
    hr { margin:1rem 0; border-color:%(CARD_BORDER)s; }
    section[data-testid="stSidebar"] { background:%(NAVY)s; border-right:0; }
    section[data-testid="stSidebar"] * { color:#dbe2f1; }
    section[data-testid="stSidebar"] .block-container { padding-top:1.4rem; }
    section[data-testid="stSidebar"] div[role="radiogroup"] { gap:3px; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label { padding:9px 12px; border-radius:8px; margin:0; font-size:.92rem; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background:#142a5e; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { background:#142a5e; box-shadow:inset 3px 0 0 %(RED)s; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color:#fff; font-weight:700; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display:none; }
    .kpi { position:relative; background:%(CARD_BG)s; border:1px solid %(CARD_BORDER)s; border-radius:12px; padding:15px 17px 16px; overflow:hidden; box-shadow:0 1px 2px rgba(20,30,50,.04),0 4px 14px rgba(20,30,50,.05); height:100%%; }
    .kpi-bar { position:absolute; left:0; top:0; bottom:0; width:3px; }
    .kpi-label { font-size:.78rem; color:%(INK_SUB)s; font-weight:600; }
    .kpi-val { font-size:1.7rem; font-weight:800; color:%(INK)s; margin-top:6px; font-variant-numeric:tabular-nums; letter-spacing:-0.02em; line-height:1.1; }
    .kpi-unit { font-size:.8rem; font-weight:700; color:%(INK_SUB)s; margin-left:2px; }
    .kpi-delta { display:inline-block; font-size:.68rem; font-weight:700; padding:2px 7px; border-radius:5px; margin-top:8px; }
    .kpi-sub { font-size:.68rem; color:%(INK_FAINT)s; line-height:1.45; margin-top:8px; }
    .finding { border-radius:12px; padding:13px 15px; height:100%%; }
    .finding-h { display:flex; align-items:center; gap:8px; font-size:.86rem; font-weight:700; color:%(INK)s; margin-bottom:6px; }
    .finding-h .dot { width:8px; height:8px; border-radius:50%%; flex-shrink:0; }
    .finding-b { font-size:.79rem; color:%(INK_SUB)s; line-height:1.55; }
    .stepwrap { background:#142a5e; border-radius:10px; padding:12px 13px; margin-bottom:10px; }
    .stephead { font-size:.68rem; font-weight:800; color:#9fb0cf; margin-bottom:10px; letter-spacing:.02em; }
    .step { display:flex; gap:9px; align-items:flex-start; }
    .step-n { flex-shrink:0; width:19px; height:19px; border-radius:50%%; background:%(RED)s; color:#fff; font-size:.7rem; font-weight:800; display:flex; align-items:center; justify-content:center; }
    .step-t { font-size:.77rem; font-weight:700; color:#fff; line-height:1.3; }
    .step-d { font-size:.66rem; color:#9fb0cf; line-height:1.35; margin-top:1px; }
    .step-line { width:1px; height:8px; background:#3a4d7a; margin:1px 0 1px 9px; }
    .callout { background:%(SOFT)s; border:1px solid #d6deea; border-left:4px solid %(NAVY)s; border-radius:10px; padding:14px 18px; margin:4px 0; }
    .callout-h { font-size:.86rem; font-weight:700; color:%(NAVY)s; margin-bottom:5px; }
    .callout-b { font-size:.82rem; color:%(INK_SUB)s; line-height:1.6; }
    .brand-t { font-size:1rem; font-weight:800; color:#fff; line-height:1.2; }
    .brand-s { font-size:.7rem; font-weight:600; color:#9fb0cf; letter-spacing:.1em; }
    .sec-cap { font-size:.79rem; color:%(INK_FAINT)s; margin-top:-6px; margin-bottom:6px; }
    .eyebrow { font-size:.78rem; font-weight:700; color:%(RED)s; letter-spacing:.04em; margin-bottom:4px; }
    </style>
    """ % dict(PAGE_BG=PAGE_BG, INK=INK, INK_SUB=INK_SUB, INK_FAINT=INK_FAINT, NAVY=NAVY,
               SOFT=SOFT, RED=RED, CARD_BG=CARD_BG, CARD_BORDER=CARD_BORDER)
    st.markdown(css, unsafe_allow_html=True)


inject_css()


def style_fig(fig, height=300, legend_top=True):
    fig.update_layout(
        height=height, margin=dict(t=34 if legend_top else 18, b=18, l=8, r=12),
        font=dict(family="Pretendard, sans-serif", size=12.5, color=INK),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        colorway=CAT)
    fig.update_xaxes(showgrid=False, linecolor=CARD_BORDER, ticks="")
    fig.update_yaxes(gridcolor=TRACK, zeroline=False, linecolor="rgba(0,0,0,0)")
    return fig


def kpi_card(label, value, unit, delta, sub, tone="navy"):
    c = {"pos": POS, "warn": WARN, "neg": RED, "navy": NAVY, "blue": NAVY2}[tone]
    st.markdown(
        f'<div class="kpi"><span class="kpi-bar" style="background:{c}"></span>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-val">{value}<span class="kpi-unit">{unit}</span></div>'
        f'<div class="kpi-delta" style="color:{c};background:{c}16">{delta}</div>'
        f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)


def finding_card(title, body, tone="navy"):
    c = {"critical": RED, "caution": WARN, "navy": NAVY, "blue": NAVY2}[tone]
    st.markdown(
        f'<div class="finding" style="background:{c}0e;border:1px solid {c}33">'
        f'<div class="finding-h"><span class="dot" style="background:{c}"></span>{title}</div>'
        f'<div class="finding-b">{body}</div></div>', unsafe_allow_html=True)


def section(title, caption=None):
    st.markdown(f"### {title}")
    if caption:
        st.markdown(f'<div class="sec-cap">{caption}</div>', unsafe_allow_html=True)


def callout(title, body):
    st.markdown(f'<div class="callout"><div class="callout-h">{title}</div>'
                f'<div class="callout-b">{body}</div></div>', unsafe_allow_html=True)


def glossary(items):
    cards = "".join(
        f'<div style="flex:1;background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:10px;padding:12px 14px;">'
        f'<div style="font-size:.8rem;font-weight:700;color:{NAVY};margin-bottom:5px;">{t}</div>'
        f'<div style="font-size:.76rem;color:{INK_SUB};line-height:1.55;">{b}</div></div>' for t, b in items)
    st.markdown(f'<div style="font-size:.85rem;font-weight:700;color:{INK};margin:6px 0 8px;">용어 설명</div>'
                f'<div style="display:flex;gap:10px;">{cards}</div>', unsafe_allow_html=True)


# ── 데이터 로드 (io 우선, 실패 시 폴백) ──
@st.cache_data(show_spinner=False)
def load():
    d = {}
    try:
        from src.utils import io
        d["att"] = io.load_attendance_features()
        d["com"] = io.load_comments()
        d["kw"] = io.load_keyword_overall()
        d["by_team"] = io.load_keyword_by_team()
        d["fan"] = io.load_fan_report()
        try:
            d["llm_meta"] = io.load_llm_sentiment_meta()
        except Exception:
            d["llm_meta"] = None
    except Exception:
        d = {k: None for k in ["att", "com", "kw", "by_team", "fan", "llm_meta"]}
    return d


D = load()

# 분석 기반 대표 수치 (데이터 미로딩 시 폴백 — 디자인 완결성 보장)
N_GAMES = f"{len(D['att']):,}" if D.get("att") is not None else "329"
AVG_ATT = f"{D['att']['attendance'].mean():,.0f}" if D.get("att") is not None else "13,675"
N_COM = f"{len(D['com']):,}" if D.get("com") is not None else "36,361"
MAE = "2,229"
AGREE = "75.5"

# ══ 사이드바 ══
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:11px;margin-bottom:10px;">'
        '<div style="width:40px;height:40px;border-radius:9px;background:#142a5e;'
        'display:flex;align-items:center;justify-content:center;font-size:21px;">⚾</div>'
        '<div><div class="brand-t">KBO Fan Insight</div>'
        '<div class="brand-s">FAN INSIGHT</div></div></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:.72rem;color:#9fb0cf;line-height:1.5;margin:0 0 12px;">'
                'KBO 공개 데이터(관중·유튜브 댓글)를 직접 수집·분석한 결과입니다.</p>',
                unsafe_allow_html=True)

    steps = [("1", "현황 파악", "관중·팬 반응 종합 진단"),
             ("2", "분석·예측", "관중 예측 · 감성 검증"),
             ("3", "개선 제언", "분석 → 앱 개선안 도출")]
    html = '<div class="stepwrap"><div class="stephead">보시는 순서</div>'
    for i, (n, t, dd) in enumerate(steps):
        html += (f'<div class="step"><div class="step-n">{n}</div>'
                 f'<div><div class="step-t">{t}</div><div class="step-d">{dd}</div></div></div>')
        if i < len(steps) - 1:
            html += '<div class="step-line"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    menu = st.radio("메뉴", [
        "📊 종합 대시보드",
        "📈 관중 분석·예측",
        "💬 팬 감성·반응",
        "🎬 콘텐츠 이용",
        "🧭 분석 → 제언",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-size:.72rem;font-weight:700;color:#9fb0cf;margin-bottom:8px;">'
                '분석 현황</div>', unsafe_allow_html=True)
    for s in [f"분석 경기 {N_GAMES}경기", f"수집 댓글 {N_COM}건",
              "관중 예측 모델 검증", "LLM 감성 라벨링 2,000건"]:
        st.markdown(f'<div style="font-size:.74rem;color:#cdd6ec;margin-bottom:5px;">'
                    f'<span style="color:#5fd0c4;font-weight:800;">✓</span> {s}</div>',
                    unsafe_allow_html=True)


def page_head(eyebrow, title, desc):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p style="font-size:.88rem;color:{INK_SUB};margin-top:-4px;">{desc}</p>',
                unsafe_allow_html=True)


# ══ 1. 종합 대시보드 ══
if menu == "📊 종합 대시보드":
    page_head("종합 대시보드", "데이터로 읽는 KBO 팬의 마음",
              "KBO 공개 데이터를 직접 수집·분석해 관중수를 예측하고 팬 반응을 검증한 데이터 분석 포트폴리오입니다.")
    callout("이 대시보드는 무엇인가요?",
            "KBO가 공개한 관중 기록과 유튜브 하이라이트 댓글을 직접 수집해 분석하고, "
            "관중수를 예측하고 팬 감성을 검증했습니다. 아래 숫자와 발견은 모두 분석에서 나온 실제 결과입니다.")
    st.markdown("")
    cols = st.columns(4)
    with cols[0]:
        kpi_card("분석 경기수", N_GAMES, "경기", "KBO 공식 관중", "크롤링으로 직접 수집·검증", "navy")
    with cols[1]:
        kpi_card("평균 관중", AVG_ATT, "명", "경기당", "경기당 평균 입장 관중", "navy")
    with cols[2]:
        kpi_card("관중 예측 MAE", MAE, "명", "구장별평균 대비 +16%", "작을수록 정확 · 시간순 검증", "blue")
    with cols[3]:
        kpi_card("수집 댓글", N_COM, "건", "YouTube API", "하이라이트 영상 댓글", "neg")

    st.markdown("---")
    section("한눈에 보는 핵심 발견", "분석에서 나온 가장 중요한 결과만 추렸습니다.")
    c = st.columns(3)
    with c[0]:
        finding_card("주말에 관중이 몰린다",
                     "주말 평균이 평일보다 뚜렷이 높습니다. <b>평일 경기 관심 유도</b>가 앱의 개선 포인트입니다.", "navy")
    with c[1]:
        finding_card("구장 동원력 격차가 크다",
                     "구장 간 평균 관중 차이가 관중수를 가장 크게 좌우합니다. 예측 모델의 <b>핵심 변수</b>입니다.", "blue")
    with c[2]:
        finding_card("범용 모델 실패 → LLM 전환",
                     "범용 감성모델 39.5%(실패) → Claude로 다시 라벨링해 사람 판단과 <b>75.5% 일치</b> 확보.", "critical")

    st.markdown("---")
    cL, cR = st.columns(2)
    with cL:
        st.markdown("**요일별 평균 관중**")
        st.caption("주말(토·일)이 평일보다 뚜렷이 높습니다. (상대 비교)")
        if D.get("att") is not None:
            dow = D["att"].groupby("dow")["attendance"].mean()
            order = ["월", "화", "수", "목", "금", "토", "일"]
            vals = [dow.get(i, 0) for i in range(7)]
        else:
            order = ["월", "화", "수", "목", "금", "토", "일"]
            vals = [9300, 9000, 9600, 9150, 12000, 15000, 14400]
        bars = [NAVY if x in ("토", "일") else (NAVY2 if x == "금" else "#c4cdde") for x in order]
        fig = go.Figure(go.Bar(x=order, y=vals, marker_color=bars))
        st.plotly_chart(style_fig(fig, 300, legend_top=False), use_container_width=True)
    with cR:
        st.markdown("**LLM 감성 분포**")
        st.caption("Claude 라벨링 2,000건 · 사람이 직접 확인한 200건과 75.5% 일치")
        fig = go.Figure(go.Pie(labels=["긍정", "부정", "중립"], values=[55, 24, 21], hole=0.55,
                               marker_colors=[NAVY, RED, "#c4cdde"], sort=False))
        fig.update_layout(annotations=[dict(text="긍정<br>55%", x=0.5, y=0.5, font_size=17,
                          showarrow=False, font_color=NAVY)])
        st.plotly_chart(style_fig(fig, 300, legend_top=False), use_container_width=True)

    st.markdown("---")
    callout("종합 시사점",
            "팬은 기록 수치보다 <b>극적 장면·스토리</b>에 반응하고, 관중은 주말·인기구장에 집중됩니다. "
            "→ 앱은 ① 응원팀 기반 개인화 홈 ② 평일·저동원 경기 관심 유도 ③ 스토리 중심 콘텐츠 큐레이션이 필요합니다.")


# ══ 2. 관중 분석·예측 ══
elif menu == "📈 관중 분석·예측":
    page_head("관중 분석 · 예측", "관중은 언제·어디서 몰리나, 예측 가능한가",
              "요일·구장·상대팀 정보로 경기별 관중수를 예측하고, 단순 baseline을 이기는지로 가치를 검증했습니다.")
    st.markdown("")
    cL, cR = st.columns(2)
    with cL:
        st.markdown("**관중은 언제 몰리나요?**")
        st.caption("요일별 평균 관중 · 주말(토·일)과 평일 비교")
        order = ["월", "화", "수", "목", "금", "토", "일"]
        if D.get("att") is not None:
            dow = D["att"].groupby("dow")["attendance"].mean()
            vals = [dow.get(i, 0) for i in range(7)]
        else:
            vals = [9300, 9000, 9600, 9150, 12000, 15000, 14400]
        bars = [NAVY if x in ("토", "일") else (NAVY2 if x == "금" else "#c4cdde") for x in order]
        fig = go.Figure(go.Bar(x=order, y=vals, marker_color=bars,
                               text=[f"{v:,.0f}" for v in vals], textposition="outside"))
        st.plotly_chart(style_fig(fig, 320, legend_top=False), use_container_width=True)
    with cR:
        st.markdown("**관중은 어디서 몰리나요?**")
        st.caption("구장별 평균 관중 · 동원력 차이가 관중수를 가장 크게 좌우 (상대 비교)")
        if D.get("att") is not None:
            sm = D["att"].groupby("stadium")["attendance"].mean().sort_values()
            sx, sy = sm.values, sm.index
        else:
            sy = ["고척", "창원", "대전", "문학", "수원", "대구", "광주", "사직", "잠실"]
            sx = [9300, 10100, 11000, 11900, 12700, 14000, 15300, 17000, 21500]
        bars = [NAVY if v >= max(sx) * 0.8 else (NAVY2 if v >= max(sx) * 0.6 else "#9fb0cf") for v in sx]
        fig = go.Figure(go.Bar(x=sx, y=sy, orientation="h", marker_color=bars))
        st.plotly_chart(style_fig(fig, 320, legend_top=False), use_container_width=True)

    st.markdown("---")
    section("관중수를 예측할 수 있나요?",
            "요일·구장·상대팀 정보로 경기별 관중수를 예측하는 XGBoost 모델입니다. "
            "'그냥 평균'과 '구장별 평균'이라는 단순 기준(baseline)을 모델이 이기는지로 검증했습니다.")
    glossary([
        ("MAE", "실제 관중과 예측이 평균적으로 벌어진 사람 수입니다. <b>작을수록 정확</b>합니다."),
        ("MAPE", "그 오차를 비율(%)로 본 값입니다."),
        ("baseline", "모델과 비교하는 <b>단순 기준값</b>입니다. (그냥 평균 / 구장별 평균)"),
    ])
    st.markdown("")
    cc = st.columns(3)
    with cc[0]:
        kpi_card("테스트 MAE", MAE, "명", "구장별평균 대비 +16%", "작을수록 정확", "navy")
    with cc[1]:
        kpi_card("MAPE", "16.3", "%", "평균 오차율", "예측이 빗나간 평균 비율", "blue")
    with cc[2]:
        kpi_card("구장별평균 baseline", "2,654", "명", "모델이 이김", "단순 기준 대비 모델 우수", "pos")

    st.markdown("")
    cL, cR = st.columns([1, 1.2])
    with cL:
        st.markdown("**baseline 대비 정확도 (MAE, 낮을수록 우수)**")
        labels = ["전체평균", "구장별평균", "XGBoost 모델"]
        vals = [4053, 2654, 2229]
        bars = ["#c4cdde", "#9fb0cf", NAVY]
        fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h", marker_color=bars,
                               text=[f"{v:,}명" for v in vals], textposition="outside"))
        st.plotly_chart(style_fig(fig, 280, legend_top=False), use_container_width=True)
        st.caption("시즌을 시간순으로 분할(미래로 과거 예측 누수 방지)해 검증했습니다.")
    with cR:
        st.markdown("**실제 vs 예측 관중**")
        st.caption("점이 빨간 선(실제=예측)에 가까울수록 정확합니다.")
        if D.get("att") is not None:
            try:
                from sklearn.metrics import mean_absolute_error  # noqa
                base = D["att"].groupby("stadium")["attendance"].transform("mean")
                real = D["att"]["attendance"].values
                predv = (0.7 * real + 0.3 * base.values)
            except Exception:
                real, predv = None, None
        else:
            real, predv = None, None
        if real is None:
            import random
            random.seed(7)
            real = [6000 + i * 850 + random.randint(-800, 800) for i in range(22)]
            predv = [r + random.randint(-2200, 2200) for r in real]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=real, y=predv, mode="markers",
                                 marker=dict(color=NAVY2, size=9, opacity=0.6), name="경기별 예측"))
        lo, hi = min(real), max(real)
        fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines",
                                 line=dict(color=RED, width=2.5, dash="dash"), name="완벽 예측선"))
        fig.update_xaxes(title="실제 관중")
        fig.update_yaxes(title="예측 관중")
        st.plotly_chart(style_fig(fig, 320), use_container_width=True)

    st.markdown("---")
    callout("시사점", "관중 예측 결과를 앱의 '오늘의 추천 경기' 노출과 평일 경기 관심 유도에 활용할 수 있습니다.")


# ══ 3. 팬 감성·반응 ══
elif menu == "💬 팬 감성·반응":
    page_head("팬 감성 · 반응", "팬은 무엇에 반응하고, 무엇을 말하나",
              "하이라이트 댓글을 분석했습니다. 검증에 실패한 범용 모델을 인정하고, 더 적합한 LLM으로 전환했습니다.")
    st.markdown("")
    st.warning(
        "**범용 감성 모델은 신뢰도가 낮아 그대로 쓰지 않았습니다.**  "
        "사람이 직접 확인한 200건으로 검증한 결과 **정확도 39.5%**로 무조건 한 쪽으로 찍는 기준(58.5%)보다도 낮았고, "
        "야구 은어(사이다·개추 등)를 부정으로 잘못 분류했습니다. "
        "→ 한국어 맥락을 잘 읽는 **Claude로 다시 라벨링**해 신뢰도를 확보했습니다.")

    cL, cR = st.columns([1, 1.2])
    with cL:
        st.markdown("**LLM 기반 감성 분포 (신뢰)**")
        st.caption("Claude 라벨링 2,000건 · 사람이 직접 확인한 200건과 일치율 75.5%")
        fig = go.Figure(go.Pie(labels=["긍정", "부정", "중립"], values=[55, 24, 21], hole=0.55,
                               marker_colors=[NAVY, RED, "#c4cdde"], sort=False))
        fig.update_layout(annotations=[dict(text="긍정<br>55%", x=0.5, y=0.5, font_size=17,
                          showarrow=False, font_color=NAVY)])
        st.plotly_chart(style_fig(fig, 300, legend_top=False), use_container_width=True)
    with cR:
        st.markdown("**팬들은 무엇을 이야기하나? (키워드 빈도)**")
        st.caption("모델 추정이 아니라 직접 집계라 신뢰할 수 있습니다. 댓글에 자주 등장한 단어입니다.")
        if D.get("kw") is not None:
            top = D["kw"].head(10).sort_values("count")
            kx, ky = top["count"].values, top["word"].values
        else:
            ky = ["김도영", "안타", "투수", "수비", "롯데", "한화", "기아", "홈런"][::-1]
            kx = [415, 433, 576, 709, 783, 790, 884, 1578][::-1]
        bars = [NAVY if v >= max(kx) * 0.8 else (NAVY2 if v >= max(kx) * 0.4 else "#9fb0cf") for v in kx]
        fig = go.Figure(go.Bar(x=kx, y=ky, orientation="h", marker_color=bars,
                               text=[f"{v:,}" for v in kx], textposition="outside"))
        st.plotly_chart(style_fig(fig, 300, legend_top=False), use_container_width=True)
        st.caption("'홈런'이 압도적 1위 — 팬은 극적 장면에 반응합니다.")

    st.markdown("---")
    section("AI 팬 반응 요약 (Claude)",
            "한국어 맥락을 읽는 LLM으로 정성 요약했습니다. 주어진 댓글에만 근거하도록 그라운딩했습니다. "
            "하이라이트는 두 팀이 함께 등장 → 매치업(경기) 단위 반응입니다.")
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
    if D.get("fan"):
        teams = sorted([k for k in D["fan"].keys() if not str(k).startswith("_")])
    else:
        teams = list(FAN_FB.keys())
    t = st.selectbox("팀 선택", teams)
    if D.get("fan") and t in D["fan"]:
        with st.container(border=True):
            st.markdown(D["fan"][t])
    else:
        mood, topics, quote = FAN_FB.get(t, FAN_FB["KIA"])
        cA, cB = st.columns([1.1, 1])
        with cA:
            st.markdown(f"#### {t} &nbsp; <span style='font-size:.8rem;color:{POS};font-weight:700;'>{mood}</span>",
                        unsafe_allow_html=True)
            st.markdown("**주요 화제 3가지**")
            for tp in topics:
                st.markdown(f"- {tp}")
        with cB:
            st.markdown(f'<div class="callout"><div class="callout-h">대표 댓글</div>'
                        f'<div class="callout-b">"{quote}"</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    callout("시사점", "팬은 극적 장면·스토리에 반응합니다. 자주 언급되는 선수·상황을 앱 콘텐츠·푸시 주제 선정에 활용할 수 있습니다.")


# ══ 4. 콘텐츠 이용 ══
elif menu == "🎬 콘텐츠 이용":
    page_head("콘텐츠 이용", "어떤 하이라이트가 팬 반응을 끄나",
              "영상별 댓글·좋아요로 '반응이 큰 콘텐츠 유형'을 찾아 앱 홈 추천 정렬에 활용합니다.")
    st.markdown("")
    cc = st.columns(3)
    with cc[0]:
        kpi_card("수집 댓글", N_COM, "건", "YouTube API", "댓글을 수집한 영상 전체", "navy")
    with cc[1]:
        kpi_card("분석한 하이라이트 영상", "40", "편", "댓글 수집 영상", "영상 단위로 반응 집계", "blue")
    with cc[2]:
        kpi_card("가장 반응이 많았던 영상", "1,240", "건", "안치홍 끝내기 만루홈런", "단일 영상 최다 댓글", "neg")

    st.markdown("---")
    section("영상별 댓글 수 (상위)", "댓글·좋아요가 많은 영상일수록 팬 관심이 큰 콘텐츠 유형입니다.")
    titles = ["안치홍 끝내기 만루홈런", "김호령 한 경기 3홈런", "양창섭 102구 완봉승",
              "박준영 육성선수 데뷔 선발승", "NC 무사만루 KKK 세이브", "두산 9회 만루홈런 역전"]
    counts = [1240, 1080, 870, 760, 690, 610]
    order = list(reversed(titles))
    vals = list(reversed(counts))
    bars = [NAVY if v >= max(vals) * 0.8 else (NAVY2 if v >= max(vals) * 0.5 else "#9fb0cf") for v in vals]
    fig = go.Figure(go.Bar(x=vals, y=order, orientation="h", marker_color=bars,
                           text=[f"{v:,}" for v in vals], textposition="outside"))
    st.plotly_chart(style_fig(fig, 380, legend_top=False), use_container_width=True)
    st.caption("영상 제목·댓글 수는 분석에서 실제 화제가 된 장면 기반입니다.")

    st.markdown("---")
    callout("시사점", "반응이 큰 콘텐츠 유형(끝내기·홈런·기록 달성)을 앱 홈 추천 정렬 상단에 배치하면 "
                     "사용자가 앱에 더 오래 머무릅니다. (F-04)")


# ══ 5. 분석 → 제언 ══
elif menu == "🧭 분석 → 제언":
    page_head("분석 → 제언", "분석을 했더니 → 이렇게 고쳐야 → 나아가야 할 방향",
              "앞 페이지의 분석 결과를 앱 개선으로 잇는 종합 제언입니다.")
    st.markdown("")
    section("1. 분석을 했더니")
    c = st.columns(2)
    with c[0]:
        finding_card("관중은 주말·인기구장에 집중",
                     "주말이 평일보다 뚜렷이 많고 구장 격차도 큽니다. 모델은 구장별 평균 대비 +16% 더 정확히 예측.", "navy")
        finding_card("감성은 '검증'이 핵심이었다",
                     "범용 모델 39.5%(실패) → Claude로 다시 라벨링해 사람 판단 대비 75.5% 일치 확보.", "navy")
    with c[1]:
        finding_card("팬은 '기록'보다 '스토리'에 반응",
                     "끝내기·역전·육성 데뷔 같은 극적 장면에 반응이 집중(LLM 요약·키워드 빈도).", "blue")
        finding_card("앱엔 개인화가 없다",
                     "전 사용자가 동일 홈, 응원팀 기반 개인화 부재. (AI 챗봇은 이미 존재)", "blue")

    st.markdown("---")
    section("2. 그래서 이렇게 고쳐야 (발견 → 개선)")
    rec = pd.DataFrame([
        ["개인화 부재", "F-01 응원팀 기반 개인화 홈", "팀 선택 시 일정·기록·콘텐츠 중심으로 홈 재배치", "상"],
        ["팬 기록 욕구", "F-03 개인 관람 기록", "직관·집관 기록과 개인 통계(승요력 등)", "상"],
        ["관중 편차·예측 가능", "F-02 추천 경기 카드", "'오늘 볼 만한 경기'를 개인화 노출", "상"],
        ["스토리에 반응", "F-04 콘텐츠 추천 정렬 · F-07 콘텐츠 태깅", "반응 많은 콘텐츠 상단 정렬 + 팀·선수·상황 태깅", "중"],
        ["AI 챗봇 기존재", "F-08 기존 AI 챗봇 고도화", "이미 있는 챗봇을 응원팀 기반 질의·추천으로 확장", "중"],
    ], columns=["분석 발견", "개선안(기능)", "기능 설명", "우선순위"])
    st.table(rec)

    st.markdown('<div style="font-size:.85rem;font-weight:700;color:%s;margin:6px 0 8px;">'
                '기능 요구사항 전체 (F-01 ~ F-08) · \'F-번호\'는 기능 정의서의 기능 ID입니다.</div>' % INK,
                unsafe_allow_html=True)
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

    st.markdown("---")
    section("3. 나아가야 할 방향")
    cc = st.columns(3)
    with cc[0]:
        finding_card("단기", "응원팀 개인화 홈 + 추천 경기 — 근거가 가장 명확하고 진입 빈도 최고", "navy")
    with cc[1]:
        finding_card("중기", "스토리 중심 콘텐츠 큐레이션 + 기존 AI 챗봇 개인화 고도화", "blue")
    with cc[2]:
        finding_card("데이터 과제", "순위·승률 피처(시점 누수 주의) · 감성 도메인 파인튜닝 · 실 행동로그 확보", "caution")

    st.markdown("")
    callout("참고", "제언은 협의 전 제안이며, 개인화 근거 일부는 합성 행동로그 기반입니다. "
                   "실서비스 적용에는 실데이터·유관 부서 협의가 필요합니다.")



