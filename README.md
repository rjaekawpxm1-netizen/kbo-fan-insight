# ⚾ KBO AI Fan Insight Platform

> KBO 공개 데이터(관중·유튜브 댓글)를 **수집 → 분석 → 검증 → 대시보드 → 앱 개선 제안**까지 연결한
> 데이터 분석 + 서비스 기획 프로젝트. *KBO 미디어사업 인턴 지원용.*

- 라이브 데모: `https://<배포-URL>.streamlit.app/`
- GitHub: `https://github.com/<아이디>/kbo-fan-insight`

## 한눈에 보는 결과

| 분석 | 데이터 | 결과 |
|---|---|---|
| **관중수 예측** | 2026 시즌 329경기 (KBO 공식, 크롤링) | XGBoost **MAE 2,229명 · MAPE 16.3%**. 전체평균 대비 45%·**구장별평균 대비 16% 개선**. 시간순 분할·누수 검증 |
| **팬 감성분석** | 하이라이트 댓글 36,361건 (YouTube API) | 범용 모델 검증 **39.5%로 실패** → **Claude 어노테이터 전환, 인간 200건 대비 75.5% 일치**(긍정 F1 0.87). 2000건 라벨링 → 분포 긍정 55%/부정 24%/중립 21% |

> 핵심은 "분석했다"가 아니라 **"검증했고, 틀리면 인정하고, 더 적합한 도구로 전환했다"**. 두 분석 모두 baseline과 비교했다.

## 핵심 결과

### 1. 관중수 예측 (정량 성과)
- 요일·홈/원정·구장 기반 XGBoost, **MAE 2,229명 / MAPE 16.3%**
- 누수 방지: 시간순 분할 + 과거정보 피처는 현재 경기 제외(shift), 시즌 전체 max 같은 누수 피처 제거
- "전체평균 / 구장별평균 / 모델" 3단 비교로 실익(+16%)을 정직하게 제시. 구장이 관중을 크게 좌우함을 정량 확인

### 2. 팬 감성분석 (검증 → 도구 전환)
- 범용 다국어 모델: 수기 200건 검증 **39.5%(실패)**, 다수class baseline(58.5%) 미달 — 야구 은어(사이다·개추) 오분류
- **Claude를 어노테이터로 전환**: 같은 200건 대비 **일치율 75.5%**(긍정 F1 0.87·부정 0.79; 중립은 표본 적고 모호해 약함)
- 검증 후 Claude로 2000건 라벨링 → 신뢰 분포 **긍정 55% / 부정 24% / 중립 21%**
- 오분류 분석: 불일치의 **70%가 중립 경계**(비꼼·은어), **극성 반전은 3.5%뿐** → 방향이 아니라 세기·모호함에서 갈림
- 보조: 키워드 빈도(모델 불필요·신뢰), 팀별 LLM 정성 요약(매치업 단위 명시)

## 기획 산출물 (서비스 기획 관점)
- `docs/01_app_service_structure.md` — 실제 KBO 앱 구조 분석(개인화 부재·AI 챗봇 기존재 확인)
- `docs/02_benchmark.md` — 국내외 앱 벤치마킹
- `docs/03_ai_personalization_cases.md` — AI 개인화 사례 + KBO 적용
- `docs/04_feature_requirements.md` — 기능 요구사항(F-01~F-07)
- `docs/05_insight_to_improvement.md` — 분석 발견 → 앱 개선 연결

## 기술 스택
`Python` `pandas` `BeautifulSoup` `XGBoost` `scikit-learn` `transformers` `Claude API` `Streamlit` `Plotly` `YouTube Data API`

## 환경 · 실행
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt        # 파이프라인 전체 (대시보드만 띄울 땐 requirements.txt)
cp .env.example .env                        # YOUTUBE_API_KEY, ANTHROPIC_API_KEY 입력

python -m src.collect.kbo_attendance        # 관중 수집(키 불필요)
python -m src.preprocess.build_dataset
python -m src.analysis.attendance_forecast  # 관중 예측·평가
python -m src.collect.youtube_comments      # 댓글 수집(YouTube 키)
python -m src.analysis.keyword_freq         # 키워드 빈도
python -m src.analysis.llm_sentiment        # Claude 감성 라벨링+검증(ANTHROPIC 키)
python -m src.analysis.llm_fan_report       # 팀별 팬 반응 요약
streamlit run dashboard/app.py              # 대시보드
```

## 배포 (Streamlit Cloud)
- 런타임은 `requirements.txt`(슬림), 파이프라인은 `requirements-dev.txt`.
- 분석 결과물(`data/processed/*`, `models/*.pkl`)은 배포 화면 표시를 위해 저장소에 포함. 원시 데이터·API 키는 제외.
- share.streamlit.io → New app → repo → main → `dashboard/app.py`. (대시보드는 사전 계산 결과만 읽어 API 키 불필요)

## 한계 · 향후 과제
- 과거 시즌·경기 결과: Schedule.aspx가 JS 렌더 → Selenium 필요(미구현). 순위·승률 피처 추가 시 관중 예측 개선 여지(단 시점 누수 주의).
- 감성 중립 분류 약함(F1 0.25) + 팀별은 매치업 단위 귀속(상대팀 혼입).
- 앱 행동로그는 비공개 → 합성 설계 샘플로만 사용.
- 데이터·영상은 개인 포트폴리오/학습 목적. 영상 재호스팅 금지.