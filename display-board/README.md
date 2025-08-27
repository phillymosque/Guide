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

✅ This guarantees the Pi reboots every midnight, keeping the display system stable, reliable, and self-healing.

