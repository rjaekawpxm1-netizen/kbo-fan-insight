"""대시보드·분석 공용 데이터 로더 (streamlit 비의존 → 단독 테스트 가능)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402


def _latest(folder: Path, pattern: str):
    files = sorted(folder.glob(pattern))
    return files[-1] if files else None


def load_attendance_features():
    p = config.PROCESSED_DIR / "attendance_features.csv"
    return pd.read_csv(p, parse_dates=["date"]) if p.exists() else None


def load_sentiment():
    p = config.PROCESSED_DIR / "sentiment_labeled.csv"
    return pd.read_csv(p) if p.exists() else None


def load_comments():
    f = _latest(config.RAW_DIR / "youtube", "comments_*.csv")
    return pd.read_csv(f) if f else None


def load_keyword_overall():
    p = config.PROCESSED_DIR / "keyword_overall.csv"
    return pd.read_csv(p) if p.exists() else None


def load_keyword_by_team():
    p = config.PROCESSED_DIR / "keyword_by_team.csv"
    return pd.read_csv(p) if p.exists() else None


def load_fan_report():
    import json
    p = config.PROCESSED_DIR / "fan_report.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def load_model():
    p = config.MODELS_DIR / "attendance_xgb.pkl"
    if not p.exists():
        return None
    import joblib
    return joblib.load(p)