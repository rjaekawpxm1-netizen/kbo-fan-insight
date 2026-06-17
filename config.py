from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = DATA_DIR / "kbo_insight.db"

KBO_ATTENDANCE_URL = "https://www.koreabaseball.com/Record/Crowd/GraphDaily.aspx"
TEAMS = ["LG", "KT", "삼성", "KIA", "두산", "한화", "NC", "SSG", "키움", "롯데"]
