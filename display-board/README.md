# Raspberry Pi TV Slideshow Setup (Google Drive + feh)

This guide automates a Raspberry Pi to sync images from a specific Google Drive folder and display them in a fullscreen slideshow using `feh`.

---

## 🧰 Requirements

- Raspberry Pi OS with desktop environment
- `feh` installed
- `rclone` configured with Google Drive
- Valid folder ID from Google Drive (read-only access is fine)

---

## 📂 Google Drive Setup

1. Identify the Drive folder you want to sync.
2. Copy its ID from the URL. Example:
   ```
   https://drive.google.com/drive/u/0/folders/1kaEBIHKSJzDsT7oU51lDW922jzYBacAr
   Folder ID: 1kaEBIHKSJzDsT7oU51lDW922jzYBacAr
   ```

---

## 🔗 rclone Configuration

Run:

```bash
rclone config
```

- Choose `n` for new remote → Name: `gdrive`
- Storage: `drive`
- Scope: `drive.readonly`
- Leave client ID/secret blank
- When done, edit the config file:

```bash
nano ~/.config/rclone/rclone.conf
```

Add:

```ini
root_folder_id = 1kaEBIHKSJzDsT7oU51lDW922jzYBacAr
```

---

## 🔁 Sync Folder Every 5 Minutes

Edit crontab:

```bash
crontab -e
```

Add:

```bash
*/5 * * * * /usr/bin/rclone sync gdrive: /home/pi/Pictures/ --delete-during >> /home/pi/rclone.log 2>&1
```

---

## 🖼️ Slideshow Script

Create:

```bash
nano /home/pi/run-feh-slideshow.sh
```

Paste:

```bash
#!/bin/bash
export DISPLAY=:0
pkill feh
feh --fullscreen --hide-pointer --slideshow-delay 10 --force-aliasing --auto-rotate --zoom max --scale-down /home/pi/Pictures
```

Make executable:

```bash
chmod +x /home/pi/run-feh-slideshow.sh
```

---

## 🔁 Restart Slideshow Every Minute

Edit crontab:

```bash
crontab -e
```

Add:

```bash
*/1 * * * * /home/pi/run-feh-slideshow.sh >> /home/pi/slideshow.log 2>&1
```

---

## ✅ Result

- `/home/pi/Pictures/` syncs from Google Drive every 5 minutes.
- `feh` is restarted every minute to load the latest images.
- Slideshow is shown fullscreen without user interaction.

---

## 📌 Notes

- The Pi must be logged into a GUI session for `DISPLAY=:0` to work.
- Make sure the `Pictures` folder contains valid image files (e.g. `.jpg`, `.png`).
- You can modify slideshow delay by adjusting the `--slideshow-delay` flag in the script.
