# 📺 Auto-Updating TV Display Slideshow

This setup automatically displays photos on a screen connected to a Raspberry Pi by syncing from a specific Google Drive folder. It updates every few minutes, adding or removing photos as needed.

## 🗂️ Google Drive Folder

All slideshow content comes from this shared Google Drive folder:

**Folder Link:** [TV Display Slides](https://drive.google.com/drive/u/2/folders/1kaEBIHKSJzDsT7oU51lDW922jzYBacAr)

## ⚙️ Components

* **Device**: Raspberry Pi
* **Slideshow viewer**: `feh`
* **Drive sync tool**: `rclone`
* **Scheduler**: `cron`

## 🔁 Sync Behavior

* New photos added to the Drive folder will appear on the screen.
* Photos removed from Drive will be deleted from the slideshow.
* The sync and slideshow restart happen on a timed loop (every 5 minutes).

## 🧪 Cron Jobs

Two cron jobs are scheduled under the `pi` user:

```cron
*/1 * * * * /usr/bin/rclone sync gdrive: /home/pi/Pictures/ --delete-during >> /home/pi/rclone.log 2>&1
*/5 * * * * /home/pi/feh-refresh-loop.sh >> /home/pi/feh-refresh.log 2>&1
```

## 📜 feh-refresh-loop.sh

Located at `/home/pi/feh-refresh-loop.sh`

```bash
#!/bin/bash
export DISPLAY=:0.0
export XAUTHORITY=/home/pi/.Xauthority

# Kill existing slideshow
echo "[$(date)] Starting slideshow script" >> /home/pi/feh-refresh.log
pkill feh
sleep 1

# Start new slideshow
echo "[$(date)] Launching feh..." >> /home/pi/feh-refresh.log
nohup feh --fullscreen --hide-pointer --slideshow-delay 10 --force-aliasing --auto-rotate --zoom max --scale-down /home/pi/Pictures > /dev/null 2>&1 &
```

## ✅ Access Permissions

Currently, only the following individuals can upload/edit slideshow content:

* **Sadr Sahib**
* **General Secretary**
* **Vice President**

More people can be authorized on request with appropriate approvals.

## 🧼 Logs

* `/home/pi/rclone.log` – Drive sync logs
* `/home/pi/feh-refresh.log` – Slideshow startup logs

## 🔄 On Boot Setup

To ensure slideshow starts after reboot, consider placing a `.desktop` entry in `~/.config/autostart/` to launch `feh-refresh-loop.sh`.

---

This system keeps your display content fresh and simple for anyone to manage via Google Drive.
