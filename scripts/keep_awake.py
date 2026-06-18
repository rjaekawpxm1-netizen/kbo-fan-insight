"""Streamlit Community Cloud 앱이 잠들지 않게 깨우는 스크립트.

단순 HTTP GET은 정적 HTML 껍데기만 받아 앱이 안 깨어난다.
실제 헤드리스 브라우저로 페이지를 열고, '잠자는 앱'이면 깨우기 버튼을 클릭한다.

GitHub Actions에서 주기 실행(.github/workflows/keep_awake.yml).
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ← 배포된 본인 앱 URL로 교체
URL = "https://kbo-fan-insight-mqdexgqbyhvppdmorvuruw.streamlit.app/"


def main() -> None:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    driver = webdriver.Chrome(options=opts)  # selenium 4.6+ 가 드라이버 자동 관리
    try:
        driver.get(URL)
        time.sleep(8)  # JS 로딩 대기
        # '잠자는 앱' 화면이면 깨우기 버튼 클릭
        buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(., 'get this app back up') or contains(., 'back up') "
            "or contains(., '앱을 다시')]",
        )
        if buttons:
            buttons[0].click()
            print("WAKE: 깨우기 버튼 클릭함")
            time.sleep(25)  # 재기동 대기
        else:
            print("OK: 이미 깨어 있음")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()