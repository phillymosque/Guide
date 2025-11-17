#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Relative Paths (auto-detected based on script location)
# ---------------------------------------------------------------------
BASE       = Path(__file__).resolve().parent
INPUT_DIR  = BASE / "input"
OUTPUT_DIR = BASE / "output"
CSV_FILE   = INPUT_DIR / "salaat_times.csv"
BG_FILE    = INPUT_DIR / "blank_flyer.png"

OUTPUT_DIR.mkdir(exist_ok=True)

if not CSV_FILE.exists():
    raise SystemExit(f"CSV not found: {CSV_FILE}")
if not BG_FILE.exists():
    raise SystemExit(f"Background not found: {BG_FILE}")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def to_ampm(t) -> str:
    """Convert '06:15:00' -> '6:15AM' (no space)."""
    t = str(t)
    dt = datetime.strptime(t, "%H:%M:%S")
    return dt.strftime("%I:%M%p").lstrip("0")


def fmt_header_date(d: date) -> str:
    """Format like 'Nov 7'."""
    return d.strftime("%b ") + str(d.day)


def render_html_to_png(html_path: Path, png_path: Path):
    """Use wkhtmltoimage to render HTML -> PNG."""
    bg_dest = html_path.parent / "blank_flyer.png"
    if not bg_dest.exists():
        shutil.copy(BG_FILE, bg_dest)

    cmd = [
        "wkhtmltoimage",
        "--enable-local-file-access",
        "--width", "768",
        "--height", "1152",
        str(html_path),
        str(png_path),
    ]
    subprocess.run(cmd, check=True)


def build_html_for_week(week_df: pd.DataFrame, start: date, end: date) -> str:
    """
    Build HTML for one Friday–Thursday week, using a single set of
    jamā‘at times (assumed constant through the week).
    """
    # Take the first row of the week as the representative times
    r = week_df.sort_values("d_date").iloc[0]

    fajr_time    = to_ampm(r["fajr_jamah"])
    zuhr_time    = to_ampm(r["zuhr_jamah"])
    asr_time     = to_ampm(r["asr_jamah"])
    maghrib_time = to_ampm(r["maghrib_jamah"])
    isha_time    = to_ampm(r["isha_jamah"])

    date_range_text = f"{fmt_header_date(start)} – {fmt_header_date(end)}"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Salaat Times</title>
<style>
  body {{
    margin: 0;
    padding: 0;
    background: #333;
  }}

  .flyer {{
    position: relative;
    width: 768px;
    height: 1152px;
    margin: 0 auto;
    background-image: url('blank_flyer.png');
    background-size: cover;
    background-position: center;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}

  /* Fixed pixel layout so wkhtmltoimage matches browser */
  .content {{
    position: absolute;
    left: 120px;     /* tweak to nudge horizontally */
    top: 250px;      /* tweak to nudge vertically   */
    width: 530px;    /* total width of text/table   */
    text-align: center;
  }}

  .title {{
    font-size: 36px;
    font-weight: 700;
    color: #2f4f2f;
    margin: 0 0 6px 0;
  }}

  .range {{
    font-size: 32px;
    color: #2f4f2f;
    margin: 0 0 18px 0;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 48px;
    color: #2f4f2f;
    background: transparent;
    margin-top: 8px;
  }}

  th, td {{
    padding: 14px 0;
    border-bottom: 8px solid rgba(0,0,0,0.15);
    text-align: center;
  }}

  th {{
    font-weight: 1000;
  }}
</style>
</head>
<body>
<div class="flyer">
  <div class="content">
    <div class="title">Bait-ul-Aafiyat Mosque</div>
    <div class="range">{date_range_text}</div>
    <table>
      <tr>
        <th>Salaat</th>
        <th>Time</th>
      </tr>
      <tr><td>Fajr</td><td>{fajr_time}</td></tr>
      <tr><td>Zuhr</td><td>{zuhr_time}</td></tr>
      <tr><td>Asr</td><td>{asr_time}</td></tr>
      <tr><td>Maghrib</td><td>{maghrib_time}</td></tr>
      <tr><td>Isha</td><td>{isha_time}</td></tr>
    </table>
  </div>
</div>
</body>
</html>
"""
    return html


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all-weeks",
        action="store_true",
        help="Generate flyers for all Friday-based weeks.",
    )
    args = parser.parse_args()

    df = pd.read_csv(CSV_FILE, parse_dates=["d_date"])
    df["d_date"] = df["d_date"].dt.date

    needed_cols = [
        "d_date",
        "fajr_jamah",
        "zuhr_jamah",
        "asr_jamah",
        "maghrib_jamah",
        "isha_jamah",
    ]
    df = df[needed_cols]

    min_date = min(df["d_date"])
    max_date = max(df["d_date"])
    today = date.today()

    def friday_starts():
        cur = min_date
        # advance to first Friday
        while cur.weekday() != 4:
            cur += timedelta(days=1)
            if cur > max_date:
                return
        while cur <= max_date:
            yield cur
            cur += timedelta(days=7)

    targets = []

    if args.all_weeks:
        for start in friday_starts():
            end = min(start + timedelta(days=6), max_date)
            targets.append((start, end))
    else:
        # Current week = last Friday <= today
        past = [d for d in df["d_date"] if d <= today]
        if past:
            fridays = [d for d in past if d.weekday() == 4]
            if fridays:
                start = max(fridays)
            else:
                start = max(past)
        else:
            start = min_date
        end = min(start + timedelta(days=6), max_date)
        targets.append((start, end))

    for start, end in targets:
        week = df[(df["d_date"] >= start) & (df["d_date"] <= end)]
        if week.empty:
            continue

        base_name = f"salaat_week_{start}_to_{end}"
        html_path = OUTPUT_DIR / f"{base_name}.html"
        png_path  = OUTPUT_DIR / f"{base_name}.png"

        html = build_html_for_week(week, start, end)
        html_path.write_text(html, encoding="utf-8")
        render_html_to_png(html_path, png_path)
        print(f"Generated {png_path}")


if __name__ == "__main__":
    main()
