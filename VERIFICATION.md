# 검증 리포트 (과정)

작성 목적: 보낸 코드가 실제로 실행되는지 직접 돌려보고, 발견한 문제와 수정 내역을 남긴다.

## 검증 환경
- Python 3.12 / pandas 3.0.2 / numpy / scikit-learn 1.8.0 / xgboost 3.2.0 / beautifulsoup4 + lxml
- (감성 모델 transformers/torch는 환경 제약상 미실행 → 규칙기반 폴백 경로로 검증)

## 실행·검증 항목과 결과

### 1. kbo_attendance.parse_attendance — 통과
KBO 구조를 모사한 HTML(요약행 + 데이터행 + 우천취소 + 네비게이션 테이블)로 파싱.
- 요약행("경기수…") 제외됨
- 우천취소(관중수 비숫자) 행 제외됨
- 네비게이션용 2칸 테이블 무시됨
- 결과: 3개 정상 행만 추출, 컬럼 일치.

### 2. build_dataset — 통과
합성 시즌(632경기)으로 피처 생성.
- home_prev_avg 결측 정확히 10건(팀별 첫 홈경기) → 누수 방지 shift 정상 동작 확인
- 산출: 632행 13열 저장.

### 3. attendance_forecast — 통과
시간순 분할(학습 506 / 테스트 126, 테스트=시즌 후반).
- baseline(평균) MAE 3,836 vs XGBoost MAE 2,053 → 46.5% 개선
- 범주형(home/away/stadium) XGBoost 네이티브 처리 정상
- 피처 중요도에서 home 지배(0.69) 확인 → 구장·팀 효과가 큰 도메인 특성(예상된 결과)

### 4. sentiment — 통과(수정 후)
규칙기반 폴백 경로로 합성 댓글 + 수기라벨 샘플 실행.
- URL·빈 댓글 정제 동작
- 수기 샘플 정확도 출력(classification_report) 동작
- 전체/팀별 분포 출력 동작

## 발견·수정한 버그
1. **sentiment.py 팀별 분포 crosstab 에러**
   - 증상: `cannot reindex on an axis with duplicate labels`
   - 원인: team1/team2를 concat할 때 인덱스 중복
   - 수정: concat 결과에 `.reset_index(drop=True)` 추가 → 정상 동작 확인

## 적용한 보완
1. **youtube_comments.py**: 비공개·삭제 영상에 `videoPublishedAt`이 없을 때 KeyError 방지(`.get` + skip).

## 미해결·주의(코드에 명시됨)
- youtube_comments: `forHandle` 실패 시 CHANNEL_ID 수동 입력 / 실제 제목에 맞춘 HIGHLIGHT_KEYWORDS 조정 필요
- sentiment: MODEL_NAME·LABEL_MAP은 실제 HF 체크포인트 확인 후 지정
- attendance: 과거 시즌(WebForms POST) `SEASON_EVENT_TARGET` 미확인 → 호출 시 NotImplementedError로 안전 중단
- kbo_schedule(경기 결과): Schedule.aspx가 JS 렌더라 정적 파싱 불가 → Selenium/AJAX 필요(미구현)

## 추가 검증 (대시보드)
- 환경: streamlit + plotly 설치, pandas 3.0.2
- io.py 로더: attendance/sentiment/comments/model 로드 정상
- 1_Attendance 예측 비교 로직: 저장된 모델 재로딩 → 시간순 테스트셋 예측 정상(샘플 출력 확인)
- 4개 페이지(app, Attendance, Sentiment, Content) 헤드리스 부팅 → **Traceback/Error 없음 확인**
- graceful 처리: 데이터 없는 페이지는 st.info 안내 후 st.stop (검증 시 데이터 있는 경로로 정상 렌더)
