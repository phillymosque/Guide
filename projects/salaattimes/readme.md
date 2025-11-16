# Salaat Times Weekly Automation System
Bait-ul-Aafiyat Mosque – Philadelphia

This system automatically:
- Reads salaat_times.csv
- Generates weekly salaah flyers (Friday → Thursday)
- Saves all flyers into a Google Drive archive
- Uploads the current week flyer into the TV slideshow folder
- Runs automatically every Friday at 2:00 AM
- Keeps the TV display updated every minute
- Reboots daily at midnight to prevent freezes

====================================================================
DIRECTORY STRUCTURE (on Raspberry Pi)
====================================================================

/home/pi/salaattimes/
│
├── generate_flyers.py
├── sync_flyers.py
├── run_weekly_salaat.sh
│
├── input/
│     ├── blank_flyer.png
│     └── salaat_times.csv
│
└── output/
      ├── salaat_week_YYYY-MM-DD_to_YYYY-MM-DD.png
      ├── salaat_week_*.html
      └── blank_flyer.png (auto-copied)

====================================================================
REQUIRED PACKAGES
====================================================================

sudo apt update
sudo apt install -y python3 python3-pip wkhtmltopdf rclone
pip3 install pandas

====================================================================
RCLONE REMOTES REQUIRED
====================================================================

1) gdrive:
   - This is the "TV Display Slides" folder.
   - Synced to /home/pi/Pictures every minute.

2) gdrive_salaat:
   - This is the Salaat Archive folder for all flyers.

Configure both using:

    rclone config

NO client secret required — just standard Google OAuth login.

====================================================================
FULL SCRIPT: generate_flyers.py
====================================================================

#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd

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

def to_ampm(t) -> str:
    t = str(t)
    dt = datetime.strptime(t, "%H:%M:%S")
    return dt.strftime("%I:%M%p").lstrip("0")

def fmt_header_date(d: date) -> str:
    return d.strftime("%b ") + str(d.day)

def render_html_to_png(html_path: Path, png_path: Path):
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
    rows_html = []
    for _, r in week_df.sort_values("d_date").iterrows():
        day_name = r["d_date"].strftime("%a")
        rows_html.append(
            "<tr>"
            f"<td>{day_name}</td>"
            f"<td>{to_ampm(r['fajr_jamah'])}</td>"
            f"<td>{to_ampm(r['zuhr_jamah'])}</td>"
            f"<td>{to_ampm(r['asr_jamah'])}</td>"
            f"<td>{to_ampm(r['maghrib_jamah'])}</td>"
            f"<td>{to_ampm(r['isha_jamah'])}</td>"
            "</tr>"
        )

    rows_block = "\n      ".join(rows_html)
    date_range_text = f"{fmt_header_date(start)} – {fmt_header_date(end)}"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Salaat Times</title>
<style>
  body {{
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #333;
    height: 100vh;
  }}
  .flyer {{
    position: relative;
    width: 768px;
    height: 1152px;
    background-image: url('blank_flyer.png');
    background-size: cover;
    background-position: center;
    font-family: system-ui, sans-serif;
  }}
  .content {{
    position: absolute;
    left: 10.5%;
    top: 20%;
    width: 80%;
    height: 95%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .title {{
    font-size: 36px;
    font-weight: 700;
    color: #2f4f2f;
    text-align: center;
  }}
  .range {{
    font-size: 44px;
    color: #2f4f2f;
    margin-bottom: 1px;
    text-align: center;
  }}
  table {{
    width: 80%;
    border-collapse: collapse;
    font-size: 22px;
    color: #2f4f2f;
  }}
  th, td {{
    padding: 18px 0;
    border-bottom: 10px solid rgba(0,0,0,0.15);
    text-align: center;
  }}
  th {{ font-weight: 1000; }}
</style>
</head>
<body>
<div class="flyer">
  <div class="content">
    <div class="title">Bait-ul-Aafiyat Mosque</div>
    <div class="range">{date_range_text}</div>
    <table>
      <tr>
        <th>Day</th>
        <th>Fajr</th>
        <th>Zuhr</th>
        <th>Asr</th>
        <th>Maghrib</th>
        <th>Isha</th>
      </tr>
      {rows_block}
    </table>
  </div>
</div>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-weeks", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv(CSV_FILE, parse_dates=["d_date"])
    df["d_date"] = df["d_date"].dt.date

    needed = ["d_date","fajr_jamah","zuhr_jamah","asr_jamah","maghrib_jamah","isha_jamah"]
    df = df[needed]

    min_date = min(df["d_date"])
    max_date = max(df["d_date"])
    today = date.today()

    def friday_starts():
        cur = min_date
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
        past = [d for d in df["d_date"] if d <= today]
        if past:
            fridays = [d for d in past if d.weekday() == 4]
            start = max(fridays) if fridays else max(past)
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

====================================================================
FULL SCRIPT: sync_flyers.py
====================================================================

#!/usr/bin/env python3
import subprocess
from pathlib import Path

BASE       = Path(__file__).resolve().parent
OUTPUT_DIR = BASE / "output"

ARCHIVE_REMOTE = "gdrive_salaat:"
CURRENT_REMOTE = "gdrive:Weekly Salaat Times"

if not OUTPUT_DIR.exists():
    raise SystemExit("Output folder missing")

def find_current_week_png():
    pngs = sorted(OUTPUT_DIR.glob("salaat_week_*.png"))
    if not pngs:
        return None
    return pngs[-1]

def sync_all_weeks():
    print("Syncing ALL PNGs to ALL-WEEKS archive (gdrive_salaat:)...")
    cmd = [
        "rclone","copy",
        str(OUTPUT_DIR),
        ARCHIVE_REMOTE,
        "--include","*.png",
        "--checksum","--progress"
    ]
    subprocess.run(cmd, check=True)
    print("All weeks synced.")

def upload_current_week():
    current = find_current_week_png()
    if not current:
        print("No PNG found.")
        return
    print(f"Current week PNG: {current.name}")

    dest = f"{CURRENT_REMOTE}/{current.name}"

    cmd = [
        "rclone","copyto",
        str(current),
        dest,
        "--progress"
    ]
    subprocess.run(cmd, check=True)
    print("Uploaded current week to slideshow folder.")

def main():
    sync_all_weeks()
    upload_current_week()

if __name__ == "__main__":
    main()

====================================================================
FULL SCRIPT: run_weekly_salaat.sh
====================================================================

#!/bin/bash
set -e
cd /home/pi/salaattimes

export RCLONE_CONFIG="/home/pi/.config/rclone/rclone.conf"

python3 generate_flyers.py --all-weeks
python3 sync_flyers.py

====================================================================
CRONJOBS
====================================================================

crontab -e

# Sync TV slideshow every minute
*/1 * * * * /usr/bin/rclone sync gdrive: /home/pi/Pictures/ --delete-during >> /home/pi/rclone.log 2>&1

# Weekly Salaat update every Friday at 2:00 AM
0 2 * * 5 /home/pi/salaattimes/run_weekly_salaat.sh >> /home/pi/salaattimes/weekly_salaat.log 2>&1

====================================================================
DAILY MIDNIGHT REBOOT (systemd)
====================================================================

/etc/systemd/system/daily-reboot.service
----------------------------------------
[Unit]
Description=Daily automatic reboot

[Service]
Type=oneshot
ExecStart=/sbin/reboot

/etc/systemd/system/daily-reboot.timer
--------------------------------------
[Unit]
Description=Run daily-reboot.service at midnight

[Timer]
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target

Enable:
sudo systemctl daemon-reload
sudo systemctl enable --now daily-reboot.timer

====================================================================
TV SLIDESHOW AUTO-REFRESH (from earlier setup)
====================================================================

/home/pi/feh-refresh-loop.sh
----------------------------
#!/bin/bash
export DISPLAY=:0.0
export XAUTHORITY=/home/pi/.Xauthority
LOGFILE="/home/pi/feh-refresh.log"

while true; do
    pkill feh
    sleep 1
    nohup /usr/bin/feh --fullscreen --hide-pointer --slideshow-delay 10 \
        --auto-rotate --zoom max --scale-down /home/pi/Pictures \
        > /dev/null 2>&1 &
    sleep 1800
done

Autostart:
  /etc/xdg/lxsession/LXDE-pi/autostart
  @bash /home/pi/feh-refresh-loop.sh

====================================================================
END OF README
====================================================================
