"""KBO 공식 유튜브(@KBO1982) 하이라이트 영상 댓글 수집.

3단 구조:
  ① 채널 업로드 목록에서 최근 영상 수집 (search.list 대신 playlistItems → 쿼터 절약)
  ② 숏츠/비하이라이트 제외 + 제목에서 등장 팀 파싱
  ③ 영상별 top-level 댓글 수집

출력: data/raw/youtube/comments_YYYYMMDD.csv

설계 메모:
- 댓글은 영상이 아니라 텍스트라 공식 API 사용은 무방(영상 클립 재호스팅만 금지).
- 제목의 "A vs B" 순서를 홈/원정으로 단정하지 않음 → team1/team2로만 저장, 홈/원정은 관중 데이터 조인 시 판정.
- 쿼터: playlistItems/videos/commentThreads 각 1 unit. search.list(100 unit)는 쓰지 않음.

실행: 프로젝트 루트에서 (.env에 YOUTUBE_API_KEY 필요)
    python -m src.collect.youtube_comments
"""

import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config  # noqa: E402

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

HANDLE = "KBO1982"               # @KBO1982
CHANNEL_ID = ""                  # forHandle 실패 시 UC... 직접 입력(개발자도구 확인)
RECENT_WEEKS = 6
MIN_DURATION_SEC = 90            # 숏츠/초단편 제외 기준
MAX_COMMENTS_PER_VIDEO = 200
COMMENT_ORDER = "relevance"      # "relevance" 또는 "time"
HIGHLIGHT_KEYWORDS = ["하이라이트", "highlight"]
DELAY_SEC = 0.3


def get_youtube():
    if not API_KEY:
        raise RuntimeError(".env에 YOUTUBE_API_KEY가 없습니다.")
    return build("youtube", "v3", developerKey=API_KEY)


def get_uploads_playlist(yt) -> str:
    """채널의 '업로드' 재생목록 ID를 가져온다."""
    if CHANNEL_ID:
        resp = yt.channels().list(part="contentDetails", id=CHANNEL_ID).execute()
    else:
        resp = yt.channels().list(part="contentDetails", forHandle=HANDLE).execute()
    items = resp.get("items", [])
    if not items:
        raise RuntimeError("채널을 찾지 못했습니다. HANDLE 또는 CHANNEL_ID를 확인하세요.")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def _iso_dur_sec(dur: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def list_recent_video_ids(yt, uploads_id: str, cutoff: datetime) -> list[dict]:
    """업로드 목록을 역순으로 페이징해 cutoff 이후 영상만 수집."""
    out, token = [], None
    while True:
        resp = yt.playlistItems().list(
            part="contentDetails,snippet", playlistId=uploads_id,
            maxResults=50, pageToken=token,
        ).execute()
        stop = False
        for it in resp.get("items", []):
            pub_raw = it["contentDetails"].get("videoPublishedAt")
            if not pub_raw:  # 비공개·삭제된 항목은 게시일이 없음
                continue
            published = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            if published < cutoff:
                stop = True
                break
            out.append({
                "video_id": it["contentDetails"]["videoId"],
                "title": it["snippet"]["title"],
                "published": published,
            })
        token = resp.get("nextPageToken")
        time.sleep(DELAY_SEC)
        if stop or not token:
            break
    return out


def filter_highlights(yt, videos: list[dict]) -> list[dict]:
    """길이(숏츠 제외) + 제목 키워드(하이라이트)로 거른다."""
    kept = []
    for i in range(0, len(videos), 50):
        chunk = videos[i:i + 50]
        ids = ",".join(v["video_id"] for v in chunk)
        resp = yt.videos().list(part="contentDetails", id=ids).execute()
        dur = {it["id"]: _iso_dur_sec(it["contentDetails"]["duration"])
               for it in resp.get("items", [])}
        for v in chunk:
            title_l = v["title"].lower()
            is_highlight = any(k.lower() in title_l for k in HIGHLIGHT_KEYWORDS)
            if dur.get(v["video_id"], 0) >= MIN_DURATION_SEC and is_highlight:
                kept.append(v)
        time.sleep(DELAY_SEC)
    return kept


def parse_teams(title: str) -> list[str]:
    """제목에 등장하는 팀명을 순서대로 반환(홈/원정 단정 안 함)."""
    found = [t for t in config.TEAMS if t in title]
    return found[:2]  # 정확히 2개 매칭된 경우만 의미


def fetch_comments(yt, video_id: str, cap: int) -> list[dict]:
    rows, token = [], None
    while len(rows) < cap:
        try:
            resp = yt.commentThreads().list(
                part="snippet", videoId=video_id, maxResults=100,
                order=COMMENT_ORDER, textFormat="plainText", pageToken=token,
            ).execute()
        except HttpError as e:
            if e.resp.status == 403:  # 댓글 비활성화 등
                print(f"  [skip] {video_id} 댓글 수집 불가 ({e.resp.status})")
            else:
                print(f"  [error] {video_id}: {e}")
            break
        for it in resp.get("items", []):
            sn = it["snippet"]["topLevelComment"]["snippet"]
            rows.append({
                "text": sn.get("textOriginal", ""),
                "like_count": sn.get("likeCount", 0),
                "comment_date": sn.get("publishedAt", "")[:10],
            })
            if len(rows) >= cap:
                break
        token = resp.get("nextPageToken")
        time.sleep(DELAY_SEC)
        if not token:
            break
    return rows


def main() -> None:
    yt = get_youtube()
    cutoff = datetime.now(timezone.utc) - timedelta(weeks=RECENT_WEEKS)

    uploads = get_uploads_playlist(yt)
    videos = list_recent_video_ids(yt, uploads, cutoff)
    print(f"[영상] 최근 {RECENT_WEEKS}주 업로드 {len(videos)}개")

    highlights = filter_highlights(yt, videos)
    print(f"[필터] 하이라이트(롱폼) {len(highlights)}개")

    records, skipped = [], 0
    for v in highlights:
        teams = parse_teams(v["title"])
        if len(teams) != 2:  # 팀 2개 매칭 안 되면 귀속 불가 → 제외
            skipped += 1
            continue
        for c in fetch_comments(yt, v["video_id"], MAX_COMMENTS_PER_VIDEO):
            records.append({
                "video_id": v["video_id"],
                "title": v["title"],
                "video_date": v["published"].date().isoformat(),
                "team1": teams[0],
                "team2": teams[1],
                **c,
            })
    print(f"[수집] 댓글 {len(records)}개 (팀 매칭 실패로 제외된 영상 {skipped}개)")

    df = pd.DataFrame(records)
    if df.empty:
        print("[경고] 수집된 댓글이 없습니다. 기간·키워드·채널을 확인하세요.")
        return

    out_dir = config.RAW_DIR / "youtube"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"comments_{datetime.now():%Y%m%d}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[저장] {out_path}")


if __name__ == "__main__":
    main()
