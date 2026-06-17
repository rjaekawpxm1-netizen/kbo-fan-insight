"""KBO 공식 '일자별 관중 현황' 크롤러.

대상: https://www.koreabaseball.com/Record/Crowd/GraphDaily.aspx
- 이 페이지는 현재 시즌 전 경기 관중 데이터를 정적 HTML 테이블로 반환한다(GET 1회로 충분).
- 수집 항목: 날짜, 요일, 홈, 방문, 구장, 관중수
- robots.txt 차단 없음. 단, 개인 포트폴리오/학습 목적으로 1회성·저빈도로만 호출한다.

과거 시즌(2024/2025)은 ASP.NET WebForms POST가 필요하다.
연도 드롭다운의 컨트롤명(__EVENTTARGET)은 추측하지 않았다 — fetch_season() 주석 참조.

실행: 프로젝트 루트에서
    python -m src.collect.kbo_attendance
"""

import re
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# 프로젝트 루트의 config.py 사용 (루트에서 -m 으로 실행한다는 전제)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}

DATE_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")
REQUEST_DELAY_SEC = 1.5  # 예의상 지연
COLUMNS = ["date", "weekday", "home", "away", "stadium", "attendance"]


def _get(url: str) -> str:
    """페이지 HTML을 가져온다. 호출 후 지연을 둔다."""
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    time.sleep(REQUEST_DELAY_SEC)
    return resp.text


def parse_attendance(html: str) -> pd.DataFrame:
    """관중 테이블을 파싱한다.

    테이블 id에 의존하지 않고, '첫 칸이 YYYY/MM/DD 형식'인 행만 데이터로 인정한다.
    상단 요약 행(경기수/평균/합계)은 날짜 패턴이 아니므로 자동 제외된다.
    """
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for tr in soup.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) < 6:
            continue
        if not DATE_RE.match(cells[0]):
            continue
        date_norm = cells[0].replace("/", "-")
        try:
            attendance = int(cells[5].replace(",", ""))
        except ValueError:
            # 관중수가 숫자가 아니면(우천취소 등) 건너뛴다
            continue
        rows.append([date_norm, cells[1], cells[2], cells[3], cells[4], attendance])

    df = pd.DataFrame(rows, columns=COLUMNS)
    if df.empty:
        raise RuntimeError(
            "관중 데이터 행을 찾지 못했습니다. 페이지 구조 변경 또는 차단 여부를 확인하세요."
        )
    df = df.drop_duplicates().reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def crawl_current_season(save: bool = True) -> pd.DataFrame:
    """현재 시즌 일자별 관중 데이터를 수집한다."""
    html = _get(config.KBO_ATTENDANCE_URL)
    df = parse_attendance(html)

    season = int(df["date"].dt.year.max())
    print(f"[수집] {season} 시즌 {len(df)}경기, 평균 {df['attendance'].mean():,.0f}명")

    if save:
        out_dir = config.RAW_DIR / "attendance"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d")
        out_path = out_dir / f"attendance_{season}_{stamp}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"[저장] {out_path}")

    return df


# 과거 시즌 수집용 컨트롤명. 실제 페이지 개발자도구(Network 탭에서 연도 변경 시
# 전송되는 __EVENTTARGET 값)를 확인해 채워야 한다. 추측값을 넣지 않았다.
SEASON_EVENT_TARGET = ""  # 예: 확인 후 입력


def fetch_season(year: int) -> pd.DataFrame:
    """과거 시즌(2024/2025 등) 수집 — WebForms POST 방식.

    동작 원리: GET으로 __VIEWSTATE 등 hidden 필드를 받아, 연도 변경 이벤트를 POST한다.
    SEASON_EVENT_TARGET가 비어 있으면(미확인) 잘못된 데이터를 받지 않도록 중단한다.
    현재 시즌은 crawl_current_season()으로 충분하다.
    """
    if not SEASON_EVENT_TARGET:
        raise NotImplementedError(
            "과거 시즌 수집은 연도 드롭다운의 __EVENTTARGET 확인이 필요합니다. "
            "개발자도구 Network 탭에서 값을 확인해 SEASON_EVENT_TARGET에 입력하세요."
        )

    url = config.KBO_ATTENDANCE_URL
    html = _get(url)
    soup = BeautifulSoup(html, "lxml")

    def hidden(name: str) -> str:
        tag = soup.find("input", {"name": name})
        return tag["value"] if tag and tag.has_attr("value") else ""

    payload = {
        "__EVENTTARGET": SEASON_EVENT_TARGET,
        "__EVENTARGUMENT": str(year),
        "__VIEWSTATE": hidden("__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": hidden("__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": hidden("__EVENTVALIDATION"),
    }
    resp = requests.post(url, headers=HEADERS, data=payload, timeout=10)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    time.sleep(REQUEST_DELAY_SEC)
    return parse_attendance(resp.text)


def main() -> None:
    crawl_current_season(save=True)


if __name__ == "__main__":
    main()
