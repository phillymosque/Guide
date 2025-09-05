# 📺 Auto-Updating TV Display Slideshow

This setup automatically displays photos on a TV connected to a Raspberry Pi. It continuously syncs from a shared Google Drive folder and updates the screen content every few minutes.

---

## 🗂️ Google Drive Folder

All slideshow content is managed through this shared Google Drive folder:

**Folder Link:** [TV Display Slides](https://drive.google.com/drive/u/2/folders/1kaEBIHKSJzDsT7oU51lDW922jzYBacAr)

---

## ⚙️ Components

- **Device**: Raspberry Pi  
- **Slideshow Viewer**: `feh`  
- **Drive Sync Tool**: `rclone`  
- **Startup Mechanism**: LXDE desktop session autostart file, which launches a persistent looping script once the GUI session is fully initialized

---

## 🔁 Sync Behavior

- New photos added to the Drive folder appear on the TV within minutes  
- Photos removed from Drive are also removed from the screen  
- The system runs a **persistent loop** that:  
  - Syncs from Google Drive  
  - Refreshes the slideshow  
  - Waits 5 minutes and repeats

---

## 📜 `feh-refresh-loop.sh`

Located at: `/home/pi/feh-refresh-loop.sh`

```bash
#!/bin/bash
export DISPLAY=:0.0
export XAUTHORITY=/home/pi/.Xauthority

LOGFILE="/home/pi/feh-refresh.log"

while true; do
    echo "[$(date)] Killing feh..." >> "$LOGFILE"
    pkill feh
    sleep 1

    echo "[$(date)] Starting feh slideshow..." >> "$LOGFILE"
    nohup /usr/bin/feh --fullscreen --hide-pointer --slideshow-delay 10 --force-aliasing --auto-rotate --zoom max --scale-down /home/pi/Pictures > /dev/null 2>&1 &

    sleep 1800
done
```

---

## 🚀 Startup on Boot

The slideshow script is launched automatically at boot using the LXDE session-level autostart file:

**Path:** `/etc/xdg/lxsession/LXDE-pi/autostart`

```text
@bash /home/pi/feh-refresh-loop.sh
```

This method ensures the script runs **after the desktop environment is fully initialized**, allowing `feh` to access the GUI reliably.

---

## ✅ Access Permissions

The following individuals currently have permission to upload or manage slideshow content:

- **Sadr Sahib**
- **General Secretary**
- **Vice President**

More users can be added with approval.

---

## 🧼 Logs

- `/home/pi/feh-refresh.log` – Slideshow loop activity  
- Optionally, rclone sync logs can be added if `rclone` output is logged in future

---

This system provides a reliable, self-updating visual display with no need for manual maintenance or periodic restarts. It is designed to run indefinitely until shutdown or power loss, and it will **automatically resume on reboot**.

# 🕛 Daily Reboot Timer (Systemd)

A **systemd service + timer pair** was created to automatically reboot the Raspberry Pi every night at **12:00 AM**. This ensures the slideshow system starts fresh daily and reduces the chance of `feh` or `rclone` hanging indefinitely.  

## Files  
### /etc/systemd/system/daily-reboot.service  
[Unit]  
Description=Daily automatic reboot  

[Service]  
Type=oneshot  
ExecStart=/sbin/reboot  

### /etc/systemd/system/daily-reboot.timer  
[Unit]  
Description=Run daily-reboot.service at midnight  

[Timer]  
OnCalendar=*-*-* 00:00:00  
Persistent=true  

[Install]  
WantedBy=timers.target  

## Behavior  
- The timer triggers `daily-reboot.service` every day at **00:00:00**.  
- `Persistent=true` ensures the reboot still happens if the Pi was offline at midnight (it runs on next boot).  
- Verified with:  
  `systemctl list-timers daily-reboot.timer`  

## Manual Testing  
To trigger the service immediately:  
`sudo systemctl start daily-reboot.service`  

After the first scheduled reboot, confirmation can be checked with:  
`journalctl -u daily-reboot.service --since "yesterday"`  


# Google Drive PDF → JPG Converter for TV Display Slides

This setup automatically converts any PDF uploaded to the **TV Display Slides** Google Drive folder into JPG images, places the JPGs back in the same folder, and archives the original PDF into a `Converted/` subfolder. It runs entirely on the Raspberry Pi, using `rclone` and `pdftoppm`.

---

## How It Works

1. **rclone remote (`gdrive`)**  
   - Configured with scope = `drive` (full access).  
   - Locked to the **TV Display Slides** folder via `root_folder_id = 1kaEBIHKSJzDsT7oU51lDW922jzYBacAr`.  
   - So `gdrive:` points directly to this folder.

2. **Script: `/home/pi/gdrive-pdf-to-jpg.sh`**
   - Lists all PDFs under `gdrive:`.
   - Downloads each PDF to a temp folder.
   - Converts to JPG(s) with `pdftoppm` (naming: `file-1.jpg`, `file-2.jpg`, etc).
   - Uploads JPGs to the same folder where the PDF was found (skips if JPGs already exist).
   - Moves the original PDF into `gdrive:/Converted/...` (mirrors the same subfolder structure).
   - Logs activity to `/home/pi/gdrive-pdf-to-jpg.log`.

3. **Systemd Service/Timer**
   - `gdrive-pdf-to-jpg.service`: runs the script once.
   - `gdrive-pdf-to-jpg.timer`: schedules the service.
     - Runs **30 seconds after boot**.
     - Then **every 15 minutes** continuously.
     - With `Persistent=true`, so missed runs during downtime execute on next boot.

---

## Script

```
#!/usr/bin/env bash
set -euo pipefail

# ===== CONFIG =====
# Your gdrive remote is locked to the "TV Display Slides" folder via root_folder_id.
# So gdrive: means "that folder", no extra path needed.
REMOTE_RO="gdrive:"              # read (same remote, scoped to folder ID)
REMOTE_RW="gdrive:"              # write (same remote)
ARCHIVE_PREFIX="Converted"       # PDFs moved here on Drive
JPEG_QUALITY="85"                # 1..100
CONCURRENCY="4"                  # parallel uploads

LOG="/home/pi/gdrive-pdf-to-jpg.log"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

exec >>"$LOG" 2>&1
echo "[$(date -Is)] === RUN START ==="

# Ensure archive root exists (no-op if already there)
rclone mkdir "$REMOTE_RW/$ARCHIVE_PREFIX" >/dev/null 2>&1 || true

# List PDFs (case-insensitive) recursively under the Drive root
mapfile -t pdfs < <(rclone lsf -R --files-only --include "{*.pdf,*.PDF}" "$REMOTE_RO" || true)

if [ ${#pdfs[@]} -eq 0 ]; then
  echo "[$(date -Is)] No PDFs found. Done."
  echo "[$(date -Is)] === RUN END ==="
  exit 0
fi

echo "[$(date -Is)] Found ${#pdfs[@]} PDF(s)."

for relpath in "${pdfs[@]}"; do
  # Skip anything already archived
  if [[ "$relpath" == "$ARCHIVE_PREFIX/"* ]]; then
    continue
  fi

  echo "[$(date -Is)] Processing: $relpath"

  workdir="$TMPDIR/work/$(dirname "$relpath")"
  mkdir -p "$workdir"

  filename="$(basename "$relpath")"
  stem="${filename%.*}"
  local_pdf="$workdir/$filename"

  # Quick skip: if first page JPG already exists in the target folder, assume converted
  if rclone lsf "$REMOTE_RO/$(dirname "$relpath")" --include "${stem}-1.jpg" | grep -q .; then
    echo "[$(date -Is)] Skipping (already converted): $relpath"
    continue
  fi

  # 1) Download PDF
  if ! rclone copyto "$REMOTE_RO/$relpath" "$local_pdf" -P; then
    echo "[$(date -Is)] WARN: download failed: $relpath"
    continue
  fi

  # 2) Convert to JPG(s)
  # Produces: stem-1.jpg, stem-2.jpg, ...
  if ! pdftoppm "$local_pdf" "$workdir/$stem" -jpeg -jpegopt quality=$JPEG_QUALITY; then
    echo "[$(date -Is)] WARN: conversion failed: $relpath"
    continue
  fi

  # 3) Upload JPG(s) to the SAME Drive folder; skip ones that already exist
  if ! rclone copy "$workdir" "$REMOTE_RW/$(dirname "$relpath")" \
        --include "${stem}-*.jpg" -P --transfers "$CONCURRENCY" --ignore-existing; then
    echo "[$(date -Is)] WARN: JPG upload failed: $relpath"
    continue
  fi

  # 4) Move original PDF to Converted/<same relative path>
  dest="$REMOTE_RW/$ARCHIVE_PREFIX/$relpath"
  destdir="$(dirname "$dest")"
  rclone mkdir "$destdir" >/dev/null 2>&1 || true

  if ! rclone moveto "$REMOTE_RW/$relpath" "$dest"; then
    echo "[$(date -Is)] WARN: archive move failed (PDF left in place): $relpath"
  else
    echo "[$(date -Is)] Archived to: $ARCHIVE_PREFIX/$relpath"
  fi
done

echo "[$(date -Is)] === RUN END ==="

```

## Installation

```bash
# Install required packages
sudo apt update
sudo apt install -y rclone poppler-utils

# Copy script
sudo nano /home/pi/gdrive-pdf-to-jpg.sh
# (paste the script, save)

# Make executable
chmod +x /home/pi/gdrive-pdf-to-jpg.sh


Systemd Unit Files

/etc/systemd/system/gdrive-pdf-to-jpg.service

[Unit]
Description=Convert Drive PDFs to JPGs and archive originals
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=pi
ExecStart=/home/pi/gdrive-pdf-to-jpg.sh


/etc/systemd/system/gdrive-pdf-to-jpg.timer

[Unit]
Description=Run Drive PDF->JPG every 15 minutes

[Timer]
OnBootSec=30s
OnUnitActiveSec=15min
Persistent=true

[Install]
WantedBy=timers.target

Enable and Start
sudo systemctl daemon-reload
sudo systemctl enable --now gdrive-pdf-to-jpg.timer

Monitoring

Check scheduled runs:

systemctl list-timers | grep gdrive-pdf-to-jpg


View logs:

journalctl -u gdrive-pdf-to-jpg.service -n 50 --no-pager


Tail script log:

tail -f /home/pi/gdrive-pdf-to-jpg.log

Behavior Summary

On boot: runs once after 30s.

Every 15 minutes: checks for new PDFs.

PDFs are converted to JPG(s) in place.

Originals are archived under Converted/.

JPGs never get reprocessed.

Feh slideshow loop remains unaffected (this runs separately).


Would you like me to also generate the `.service` and `.timer` files as standalone t

✅ This guarantees the Pi reboots every midnight, keeping the display system stable, reliable, and self-healing.

