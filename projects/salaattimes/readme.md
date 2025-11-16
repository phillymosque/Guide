# Salaat Times Weekly Automation System
Bait-ul-Aafiyat Mosque – Philadelphia

This system automatically:

- Processes `salaat_times.csv`
- Generates weekly salaah flyers for **Friday → Thursday**
- Saves *all* weekly flyers to a Google Drive archive
- Uploads the **current week flyer** to the TV slideshow folder
- Updates automatically every **Friday at 2:00 AM**
- TV slideshow updates every minute via rclone
- Device reboots every night at 12:00 AM for stability

====================================================================
DIRECTORY STRUCTURE (Raspberry Pi)
====================================================================

/home/pi/salaattimes/
│
├── generate_flyers.py         ← main generator script
├── sync_flyers.py             ← sync script (archive + current week)
├── run_weekly_salaat.sh       ← weekly wrapper
│
├── input/
│     ├── blank_flyer.png
│     └── salaat_times.csv
│
└── output/
      ├── salaat_week_YYYY-MM-DD_to_YYYY-MM-DD.png
      ├── salaat_week_*.html
      └── blank_flyer.png

====================================================================
REQUIRED PACKAGES
====================================================================

sudo apt update
sudo apt install -y python3 python3-pip wkhtmltopdf rclone
pip3 install pandas

====================================================================
RCLONE REMOTES REQUIRED
====================================================================

Two remotes must be configured via:

    rclone config

1) **gdrive**
   - Points to the **TV Display Slides** folder  
   - Synced into `/home/pi/Pictures` for the TV display

2) **gdrive_salaat**
   - Points to the **Salaat Archive folder**  
   - Stores *all* weekly PNG flyers

Google OAuth login → no client secret needed.

====================================================================
MAIN SCRIPT LOCATIONS
====================================================================

The two large scripts are stored here:

- `/home/pi/salaattimes/generate_flyers.py`
- `/home/pi/salaattimes/sync_flyers.py`

(See files in repository — not inlined here.)

====================================================================
WEEKLY WRAPPER SCRIPT
====================================================================

**/home/pi/salaattimes/run_weekly_salaat.sh**

```

#!/bin/bash
set -e
cd /home/pi/salaattimes

export RCLONE_CONFIG="/home/pi/.config/rclone/rclone.conf"

python3 generate_flyers.py --all-weeks
python3 sync_flyers.py

```

Make executable:

```

chmod +x /home/pi/salaattimes/run_weekly_salaat.sh

```

====================================================================
CRONJOBS
====================================================================

Edit crontab:

```

crontab -e

```

Add:

```

# Sync TV slideshow every minute

*/1 * * * * /usr/bin/rclone sync gdrive: /home/pi/Pictures/ --delete-during >> /home/pi/rclone.log 2>&1

# Salaat weekly update every Friday at 2:00 AM

0 2 * * 5 /home/pi/salaattimes/run_weekly_salaat.sh >> /home/pi/salaattimes/weekly_salaat.log 2>&1

```

====================================================================
DAILY MIDNIGHT REBOOT (systemd)
====================================================================

`/etc/systemd/system/daily-reboot.service`

```

[Unit]
Description=Daily automatic reboot

[Service]
Type=oneshot
ExecStart=/sbin/reboot

```

`/etc/systemd/system/daily-reboot.timer`

```

[Unit]
Description=Run daily-reboot.service at midnight

[Timer]
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target

```

Enable:

```

sudo systemctl daemon-reload
sudo systemctl enable --now daily-reboot.timer

```

====================================================================
TV SLIDESHOW AUTO-REFRESH LOOP
====================================================================

`/home/pi/feh-refresh-loop.sh`

```

#!/bin/bash
export DISPLAY=:0.0
export XAUTHORITY=/home/pi/.Xauthority
LOGFILE="/home/pi/feh-refresh.log"

while true; do
pkill feh
sleep 1
nohup /usr/bin/feh --fullscreen --hide-pointer --slideshow-delay 10 
--auto-rotate --zoom max --scale-down /home/pi/Pictures 
> /dev/null 2>&1 &
sleep 1800
done

```

Autostart:

`/etc/xdg/lxsession/LXDE-pi/autostart`

```

@bash /home/pi/feh-refresh-loop.sh

```

====================================================================
HIGH-LEVEL FLOW
====================================================================

1. **Every Friday 2 AM**
   - `generate_flyers.py` produces new PNGs for all weeks
   - `sync_flyers.py`:
     - Uploads **all PNGs** to the archive folder (`gdrive_salaat`)
     - Uploads **this week’s flyer** to the slideshow folder (`gdrive`)
     - Keeps all other slideshow content untouched

2. **Every minute**
   - rclone syncs `gdrive:` → `/home/pi/Pictures`
   - TV updates automatically

3. **Every midnight**
   - Pi reboots cleanly  
   - Slideshow restart guaranteed

====================================================================
END OF README
====================================================================
