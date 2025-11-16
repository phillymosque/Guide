#!/usr/bin/env python3
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
import sys

# ---------------------------------------------------------------------
# Paths (relative to this script)
# ---------------------------------------------------------------------
BASE       = Path(__file__).resolve().parent
OUTPUT_DIR = BASE / "output"

if not OUTPUT_DIR.exists():
    sys.stderr.write("Output directory not found: %s\n" % OUTPUT_DIR)
    sys.exit(1)

# ---------------------------------------------------------------------
# Rclone remotes / folders
# ---------------------------------------------------------------------
# gdrive:        -> TV Display Slides (current-week folder, what feh uses)
# gdrive_salaat: -> All Weeks Salaat Flyers (archive folder)
REMOTE_CURRENT   = "gdrive:"         # TV display folder
REMOTE_ALL_WEEKS = "gdrive_salaat:"  # archive of all flyers

# ---------------------------------------------------------------------
# Helper: find current week PNG (based on filename dates)
# ---------------------------------------------------------------------
FNAME_RE = re.compile(
    r"^salaat_week_(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})\.png$"
)

def find_current_week_png():
    candidates = []

    for p in OUTPUT_DIR.glob("salaat_week_*.png"):
        m = FNAME_RE.match(p.name)
        if not m:
            continue

        start_s, end_s = m.groups()
        start_d = datetime.strptime(start_s, "%Y-%m-%d").date()
        end_d   = datetime.strptime(end_s, "%Y-%m-%d").date()
        candidates.append((start_d, end_d, p))

    if not candidates:
        return None

    today = date.today()

    # Prefer week that actually contains "today"
    containing = [(s, e, p) for (s, e, p) in candidates if s <= today <= e]
    if containing:
        containing.sort(key=lambda x: x[0], reverse=True)
        return containing[0][2]

    # Otherwise: latest week that starts before today
    past = [(s, e, p) for (s, e, p) in candidates if s <= today]
    if past:
        past.sort(key=lambda x: x[0], reverse=True)
        return past[0][2]

    # Fallback: earliest one
    candidates.sort(key=lambda x: x[0])
    return candidates[0][2]

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    # 1) Copy ALL PNGs to ALL-WEEKS archive folder (append-only, no deletes)
    print("Syncing ALL PNGs to ALL-WEEKS archive (gdrive_salaat:)...")
    cmd_all = [
        "rclone", "copy",
        str(OUTPUT_DIR),
        REMOTE_ALL_WEEKS,
        "--include", "*.png",
        "--checksum",
        "--progress",
    ]
    subprocess.run(cmd_all, check=True)
    print("All weeks synced to archive.")

    # 2) Figure out which PNG is the CURRENT week
    current_png = find_current_week_png()
    if not current_png:
        sys.stderr.write("No salaat_week_*.png found in output.\n")
        sys.exit(1)

    print("Current week PNG:", current_png.name)

    # 3) Upload CURRENT week flyer under a fixed name to the TV folder
    print("Uploading CURRENT week flyer to gdrive: as salaat_week_current.png ...")
    dest_path = REMOTE_CURRENT + "salaat_week_current.png"
    cmd_copy_cur = [
        "rclone", "copyto",
        str(current_png),
        dest_path,
        "--progress",
    ]
    subprocess.run(cmd_copy_cur, check=True)

    print("Done. Current week flyer updated (old files left untouched).")

if __name__ == "__main__":
    main()
