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

