# KBO AI Fan Insight Platform

> KBO 공개 데이터(관중·유튜브 댓글)를 **수집 → 분석 → 검증 → 대시보드 → 앱 개선 제안**까지 연결한
> 데이터 분석 + 서비스 기획 프로젝트. *KBO 미디어사업 인턴 지원용.*

## 한눈에 보는 결과

| 분석 | 데이터 | 결과 |
|---|---|---|
| **관중수 예측** | 2026 시즌 329경기 (KBO 공식, 크롤링) | XGBoost **MAE 2,229명 · MAPE 16.3%**. 전체평균 대비 45%·구장별평균 대비 16% 개선. 시간순 분할·누수 검증 완료 |
| **팬 감성분석** | 하이라이트 댓글 36,361건 (YouTube API) | 범용 모델을 수기 200건으로 **검증 → 정확도 39.5%**(다수class baseline 58.5% 미달). 도메인 은어 오분류 확인 → **한계로 명시 + 파인튜닝 제안** |

> 핵심은 "분석했다"가 아니라 **"검증했고 한계를 안다"**. 두 파트 모두 baseline과 비교해 모델의 실익을 확인했다.

## 문제 정의

KBO 앱은 단순 정보 제공을 넘어 개인화·팬 유지가 중요해지고 있다. 본 프로젝트는 데이터 분석 담당자 + 서비스 기획자 관점에서, **실제 수집 가능한 공개 데이터만으로** 관중·팬 반응을 분석하고 그 결과를 앱 개선 제안으로 연결한다.

## 데이터 파이프라인

```
수집(KBO 관중 · YouTube 댓글) → 통합(CSV/SQLite) → 분석(관중수 예측 · 감성분석)
  → 인사이트 → ① 앱 개선·기능요구사항  ② Streamlit 대시보드
```

## 핵심 결과

### 1. 관중수 예측 (정량 성과)
- 요일·홈/원정·구장 기반 XGBoost 회귀, **MAE 2,229명 / MAPE 16.3%**
- 누수 방지: 시간순 분할 + 과거정보 피처는 현재 경기 제외(shift)
- "전체평균 / 구장별평균 / 모델" 3단 비교로 모델의 실익(+16%)을 정직하게 제시

### 2. 팬 감성분석 (검증·한계 인식)
- 하이라이트 댓글 36,361건 수집 → 범용 다국어 감성 모델 적용
- **수기 200건으로 검증: 정확도 39.5%**, 다수class baseline(58.5%)에 미달
- 원인: 야구 은어(사이다·개추 등)를 부정으로 오분류. positive recall 0.36
- 결론: 잘못된 수치 대신 한계로 명시, 도메인 파인튜닝을 향후 과제로 제안
- 수기 검증 표본 기준 실제 분포: **긍정 약 59% 우세**(n=200, 단일 채널·최근 6주)

## 기획 산출물 (서비스 기획 관점)
- `docs/02_benchmark.md` — 국내외 앱 벤치마킹(KBO·프로야구LIVE·오늘의야구·MLB)
- `docs/03_ai_personalization_cases.md` — AI 개인화 사례 + KBO 적용
- `docs/04_feature_requirements.md` — 기능 요구사항(F-01~F-07)
- `docs/05_insight_to_improvement.md` — 분석 발견 → 앱 개선 연결

## 기술 스택
`Python` `pandas` `BeautifulSoup` `XGBoost` `scikit-learn` `transformers` `Streamlit` `Plotly` `YouTube Data API`

## 실행
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # YOUTUBE_API_KEY 입력

python -m src.collect.kbo_attendance       # 관중 수집(키 불필요)
python -m src.preprocess.build_dataset     # 피처셋
python -m src.analysis.attendance_forecast # 학습·평가
python -m src.collect.youtube_comments     # 댓글 수집(키 필요)
python -m src.analysis.sentiment           # 감성분석+검증
streamlit run dashboard/app.py             # 대시보드
```

## 한계 · 향후 과제
- 과거 시즌·경기 결과: Schedule.aspx가 JS 렌더 → Selenium 필요(미구현). 순위·승률 피처 추가 시 관중 예측 개선 여지.
- 감성: 야구 도메인 파인튜닝 필요.
- 앱 행동로그: 비공개 → 합성 설계 샘플로만 사용(실서비스는 실데이터 필요).
- 데이터·영상은 개인 포트폴리오/학습 목적. 영상 클립 재호스팅 금지.