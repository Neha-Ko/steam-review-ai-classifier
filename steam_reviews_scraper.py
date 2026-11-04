"""
Steam review scraper for the "Is the AI penalty real?" project.

Uses Steam's official review API, IUserReviewsService/GetAppReviews
(the old store.steampowered.com/appreviews endpoint was retired by Valve
on Oct 22, 2026). No API key is needed.

Setup:
    pip install requests pandas

Usage:
    # 1. Test on one game
    python steam_reviews_scraper.py --appids 2404880 --max-per-game 20 --out test.csv

    # 2. Check review counts for every game (no review text downloaded)
    python steam_reviews_scraper.py --appid-file games_final.csv --summary

    # 3. Full scrape
    python steam_reviews_scraper.py --appid-file games_final.csv --max-per-game 100 --out reviews_raw.csv

By default it pulls English, negative reviews created between 2024-01-01 and
2025-12-31, newest first, from all purchase types (Steam and non-Steam keys).
Change these with --review-type, --language, --start and --end.

games_final.csv needs an "appid" column. Any other columns (e.g. "group" with
values "disclosed"/"control") are carried through to the output.
"""

import argparse
import json
import time
from datetime import datetime, timezone

import pandas as pd
import requests

ENDPOINT = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/"
HEADERS = {"User-Agent": "steam-reviews-class-project/1.0 (python-requests)"}

# Enum values from Valve's IUserReviewsService documentation
FILTER_RECENT = 1                                           # newest first
REVIEW_TYPE = {"all": 0, "positive": 1, "negative": 2}
PURCHASE_TYPE_ALL = 1                                       # Steam + non-Steam purchases


def to_unix(date_str, end_of_day=False):
    """'2024-01-01' -> Unix timestamp (UTC)."""
    d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if end_of_day:
        d = d.replace(hour=23, minute=59, second=59)
    return int(d.timestamp())


def call_api(query, retries=4):
    """Call GetAppReviews with an input_json query; return the 'response' object."""
    last = ""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(ENDPOINT, params={"input_json": json.dumps(query)},
                                headers=HEADERS, timeout=30)
        except requests.RequestException as err:
            last = f"network error: {err}"
        else:
            if resp.status_code == 429:
                last = "HTTP 429 (rate limited by Steam)"
                time.sleep(15 * attempt)  # wait longer when rate limited
                continue
            if resp.history and not resp.url.startswith(ENDPOINT):
                last = f"redirected to {resp.url} (endpoint may have changed)"
            elif resp.status_code != 200:
                last = f"HTTP {resp.status_code}: {resp.text[:200]!r}"
            else:
                try:
                    return resp.json().get("response", {})
                except ValueError:
                    last = f"HTTP 200 but not JSON: {resp.text[:200]!r}"
        time.sleep(3 * attempt)
    raise RuntimeError(last)


def base_query(appid, review_type, language, start, end):
    q = {
        "appid": int(appid),
        "filter": FILTER_RECENT,
        "review_type": REVIEW_TYPE[review_type],
        "purchase_type": PURCHASE_TYPE_ALL,
        "languages": [language],
        "filter_offtopic_activity": False,  # keep "review bomb" reviews; they may be about AI
    }
    if start and end:
        q["date_range_start"] = to_unix(start)
        q["date_range_end"] = to_unix(end, end_of_day=True)
    return q


def fetch_reviews(appid, max_reviews=100, review_type="negative", language="english",
                  start="2024-01-01", end="2025-12-31", pause=1.0):
    """Return up to max_reviews reviews for one game as a list of dicts."""
    reviews, seen_ids, seen_cursors = [], set(), set()
    cursor = "*"

    while len(reviews) < max_reviews:
        q = base_query(appid, review_type, language, start, end)
        q.update({"cursor": cursor, "num_per_page": 100})
        try:
            data = call_api(q)
        except RuntimeError as err:
            print(f"  app {appid}: request failed ({err}), stopping this game")
            break

        batch = data.get("reviews", [])
        if not batch:
            break  # no more reviews in this date range

        for r in batch:
            rid = r.get("recommendationid")
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            author = r.get("author", {})
            reviews.append({
                "appid": int(appid),
                "recommendationid": rid,
                "review": r.get("review", ""),
                "voted_up": r.get("voted_up"),
                "votes_up": r.get("votes_up"),
                "votes_funny": r.get("votes_funny"),
                "weighted_vote_score": r.get("weighted_vote_score"),
                "timestamp_created": r.get("timestamp_created"),
                "language": r.get("language"),
                "steam_purchase": r.get("steam_purchase"),
                "received_for_free": r.get("received_for_free"),
                "written_during_early_access": r.get("written_during_early_access"),
                "refunded": r.get("refunded"),
                "author_playtime_forever_min": author.get("playtime_forever"),
                "author_playtime_at_review_min": author.get("playtime_at_review"),
                "author_num_reviews": author.get("num_reviews"),
            })
            if len(reviews) >= max_reviews:
                break

        cursor = data.get("cursor")
        if not cursor or cursor in seen_cursors:
            break
        seen_cursors.add(cursor)
        time.sleep(pause)  # be polite to Steam's servers

    return reviews


def fetch_summary(appid, language="english", start="2024-01-01", end="2025-12-31"):
    """Review counts for one game (no review text). Used to pick games."""
    row = {"appid": int(appid)}
    try:
        # All-time totals (only returned when review_type = all)
        q = base_query(appid, "all", language, None, None)
        q["num_per_page"] = 1
        qs = call_api(q).get("query_summary", {})
        total, pos = qs.get("total_reviews"), qs.get("total_positive")
        row.update({
            "total_reviews_alltime": total,
            "total_negative_alltime": qs.get("total_negative"),
            "pct_positive_alltime": round(100 * pos / total, 1) if total else None,
            "review_score_desc": qs.get("review_score_desc"),
        })
        time.sleep(1.0)
        # Negative and positive reviews inside the study's date window
        # (needed for "complaints per 100 reviews")
        for kind in ("negative", "positive"):
            q = base_query(appid, kind, language, start, end)
            q["num_per_page"] = 1
            row[f"{kind}_in_window"] = call_api(q).get("total_matching")
            time.sleep(1.0)
    except RuntimeError as err:
        print(f"  app {appid}: request failed ({err})")
    return row


def main():
    parser = argparse.ArgumentParser(description="Scrape Steam reviews by app ID.")
    parser.add_argument("--appids", nargs="*", type=int, default=[],
                        help="Steam app IDs, space separated")
    parser.add_argument("--appid-file", help="CSV with an 'appid' column")
    parser.add_argument("--max-per-game", type=int, default=100)
    parser.add_argument("--review-type", default="negative", choices=list(REVIEW_TYPE))
    parser.add_argument("--language", default="english")
    parser.add_argument("--start", default="2024-01-01", help="YYYY-MM-DD")
    parser.add_argument("--end", default="2025-12-31", help="YYYY-MM-DD")
    parser.add_argument("--out", default="reviews.csv")
    parser.add_argument("--summary", action="store_true",
                        help="Only fetch review counts per game (for picking games)")
    args = parser.parse_args()

    games = pd.DataFrame({"appid": args.appids})
    if args.appid_file:
        games = pd.concat([games, pd.read_csv(args.appid_file)], ignore_index=True)
    games = games.dropna(subset=["appid"]).astype({"appid": int})
    games = games.drop_duplicates(subset="appid")
    if games.empty:
        parser.error("Give at least one app ID with --appids or --appid-file")

    if args.summary:
        rows = []
        for i, appid in enumerate(games["appid"], start=1):
            rows.append(fetch_summary(appid, args.language, args.start, args.end))
            print(f"[{i}/{len(games)}] app {appid}: "
                  f"{rows[-1].get('negative_in_window')} negative reviews in window")
            time.sleep(1.0)
        summary = games.merge(pd.DataFrame(rows), on="appid", how="left")
        out = args.out if args.out != "reviews.csv" else "games_summary.csv"
        summary.to_csv(out, index=False)
        print(f"\nSaved to {out}")
        return

    all_reviews = []
    for i, appid in enumerate(games["appid"], start=1):
        rows = fetch_reviews(appid, args.max_per_game, args.review_type,
                             args.language, args.start, args.end)
        print(f"[{i}/{len(games)}] app {appid}: {len(rows)} reviews")
        all_reviews.extend(rows)

    df = pd.DataFrame(all_reviews)
    if df.empty:
        print("No reviews collected.")
        return

    # Carry through any extra columns from the game list (e.g. disclosed/control)
    df = df.merge(games, on="appid", how="left")

    # Light cleaning only; the rest happens (documented) in the notebook
    df["review"] = df["review"].fillna("").str.strip()
    df = df[df["review"].str.len() > 0]
    df["created"] = pd.to_datetime(df["timestamp_created"], unit="s")
    df["scraped_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} reviews from {df['appid'].nunique()} games to {args.out}")


if __name__ == "__main__":
    main()
