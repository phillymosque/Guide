# Voicebox Automation Report

## 1. What We Made
- Configured **Voicebox** (Raspberry Pi OS Lite) as an **audio announcement device**.  
- Added ability to play scheduled audio loops through the headphone jack.  
- Built a **weekly Jumu’ah (Friday) announcement loop**:
  - Plays `testsampes.mp3` on repeat between **12:30 PM and 2:00 PM** every Friday.  
  - Includes a **15 second pause** between plays.  
  - Automatically stops at 2:00 PM using `RuntimeMaxSec`.  
- Added a **weekly reboot task**:
  - Reboots the Pi every Thursday at **11:00 PM** to ensure stability.  
- Confirmed system timezone is set to **America/New_York** with DST handling.  

## 2. Program and Hardware Used
- **Hardware:**
  - Raspberry Pi 3 A+ running **Raspberry Pi OS Lite**.  
  - Headphones connected to **card 0 (bcm2835 Headphones)** for audio output.  

- **Programs Installed:**
  - `alsa-utils` → provides `aplay` and audio mixer controls.  
  - `mpg123` → lightweight MP3 playback tool.  
  - `systemd` → for services and timers (default in Raspberry Pi OS Lite).  

## 3. Files Created
### Audio Script
`/home/voicebox/announcements/friday_loop.sh`
```bash
#!/bin/bash
FILE="/home/voicebox/announcements/testsample.mp3"

while true; do
    mpg123 -q "$FILE"
    sleep 15
done
```

### Service Units
`/etc/systemd/system/friday_loop.service`
```ini
[Unit]
Description=Friday Announcement Loop
After=network.target sound.target

[Service]
User=voicebox
WorkingDirectory=/home/voicebox/announcements
ExecStart=/bin/bash /home/voicebox/announcements/friday_loop.sh
Restart=no
RuntimeMaxSec=1h30min
```

`/etc/systemd/system/reboot-weekly.service`
```ini
[Unit]
Description=Weekly scheduled reboot (Thu 23:00)

[Service]
Type=oneshot
ExecStart=/usr/sbin/shutdown -r now
```

### Timer Units
`/etc/systemd/system/friday_loop.timer`
```ini
[Unit]
Description=Run Friday Announcement Loop

[Timer]
OnCalendar=Fri 12:30
Persistent=false
AccuracySec=1min

[Install]
WantedBy=timers.target
```

`/etc/systemd/system/reboot-weekly.timer`
```ini
[Unit]
Description=Timer for weekly reboot (Thu 23:00)

[Timer]
OnCalendar=Thu 23:00
AccuracySec=1min

[Install]
WantedBy=timers.target
```

## 4. Services and Timers
### Active Units
```text
friday_loop.service   (static)   — triggered by friday_loop.timer
friday_loop.timer     (enabled)  — runs every Fri at 12:30 PM
reboot-weekly.service (static)   — triggered by reboot-weekly.timer
reboot-weekly.timer   (enabled)  — runs every Thu at 11:00 PM
```

## 5. Reboot Info
- Weekly reboot scheduled for **Thursdays at 23:00 (11:00 PM)**.  
- Verified with:
  ```bash
  systemctl list-timers --all | grep reboot-weekly
  ```
- Ensures a clean restart before Jumu’ah service.  

## 6. Timezone & DST
- Device timezone: **America/New_York (EDT/EST)**  
- DST transitions are automatic.  
- Verified with:
  ```bash
  timedatectl
  ```
  Example:
  ```
  Local time: Sun 2025-09-28 21:07:03 EDT
  Time zone: America/New_York (EDT, -0400)
  System clock synchronized: yes
  NTP service: active
  ```

✅ **Summary**:  
Voicebox is fully configured to **loop announcements on Fridays** during Jumu’ah time with automatic **weekly reboots**, and all services/timers are persistent across reboots with proper DST handling.  


## 7. Device Access Information
```text
Hostname: voicebox
Password: soma1234
Default Wi-Fi Connection: preconfigured (home network), with auto-connect priority set lower than "PhillyMosque Admin"
```

## 8. Manual Audio Playback
- Default announcements directory:  
  `/home/voicebox/announcements/`  

- Play MP3 manually:  
  ```bash
  mpg123 /home/voicebox/announcements/testsample.mp3
  ```

- Play WAV manually:  
  ```bash
  aplay /home/voicebox/announcements/yourfile.wav
  ```

- Stop playback (if running):  
  ```bash
  pkill -f mpg123
  pkill -f aplay
  ```
