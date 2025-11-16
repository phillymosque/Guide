# **Weekly Salaat Flyer Generator**

This project automatically generates **weekly Jamaat Salaat Time flyers** using:

* A **CSV file** of daily prayer times
* A **flyer background image** (PNG)
* A **Python generator script**
* **wkhtmltoimage** for HTML → PNG rendering
* Optional upload to **Google Drive** via rclone

Output is a set of **high-quality flyer PNGs** (current week or all weeks).

---

## **📁 Folder Structure**

```
/home/pi/salaattimes/
│
├── generate_flyers.py        # main generator script
│
├── input/
│   ├── salaat_times.csv      # source data (daily times)
│   └── blank_flyer.png       # flyer background PNG
│
└── output/                   # generated HTML + PNG per week
    ├── salaat_week_YYYY-MM-DD_to_YYYY-MM-DD.html
    └── salaat_week_YYYY-MM-DD_to_YYYY-MM-DD.png
```

* **input/** is manually updated.
* **output/** is fully auto-generated and can be safely deleted anytime.

---

## **📥 Input: CSV Format**

The CSV must contain these columns:

```
d_date
fajr_jamah
zuhr_jamah
asr_jamah
maghrib_jamah
isha_jamah
```

Example:

| d_date     | fajr_jamah | zuhr_jamah | asr_jamah | maghrib_jamah | isha_jamah |
| ---------- | ---------- | ---------- | --------- | ------------- | ---------- |
| 2025-11-07 | 06:15:00   | 13:15:00   | 16:00:00  | 16:56:00      | 19:15:00   |

Only *_jamah columns are used.

---

## **🎨 Flyer Layout**

Each flyer uses:

* Your background: **blank_flyer.png**
* A fixed canvas: **768 × 1152 px**
* A centered content area
* A week header: `Nov 7 – Nov 13`
* A table using **Fri–Thu** dates

### **CSS Notes**

* Uses your exact styling:

```css
.content {
  position: absolute;
  left: 10.5%;
  top: 20%;
  width: 80%;
  height: 95%;
}
.range {
  font-size: 44px;
}
table {
  width: 80%;
}
th, td {
  border-bottom: 10px solid rgba(0,0,0,0.15);
}
```

Times use **no space** → `6:15AM`.

---

## **🧠 Week Logic**

### **Current Week**

The script finds:

> **Most recent Friday ≤ today**
> and generates **Friday → Thursday**

Example:
If today is *Saturday Nov 15*, it selects **Nov 14 – Nov 20**.

### **All Weeks**

Every Friday in the CSV becomes a generated week.

---

## **⚙️ Installation**

### Install system dependencies:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip wkhtmltopdf rclone
```

### Install Python deps (no heavy numpy):

```bash
pip3 install pandas==1.1.5 --no-deps
pip3 install python-dateutil pytz
```

---

## **▶️ Commands**

### **Generate the current week flyer**

```bash
cd /home/pi/salaattimes
python3 generate_flyers.py
```

Outputs:

```
output/salaat_week_YYYY-MM-DD_to_YYYY-MM-DD.png
```

---

### **Generate all weeks in the CSV**

```bash
python3 generate_flyers.py --all-weeks
```

---

### **Clean output folder**

```bash
rm -rf /home/pi/salaattimes/output/*
```

---

## **☁️ Upload to Google Drive (optional)**

Assuming rclone is already configured:

```bash
rclone copy /home/pi/salaattimes/output gdrive: \
  --drive-root-folder-id 17Fw4HgfCn6UcktNR-_QHLvAKsCSOchLB \
  --progress
```

Overwrites duplicates automatically.

---

## **🖼️ How Rendering Works**

1. Script builds HTML for each week
2. Copies background image next to the HTML
3. Renders using wkhtmltoimage with local file access:

   ```bash
   wkhtmltoimage --enable-local-file-access
   ```
4. Outputs PNGs in `output/`

No browser is needed.

---

## **🔄 Customizing the Flyer**

To update:

* Background → replace `input/blank_flyer.png`
* Colors / layout → edit CSS block inside `generate_flyers.py`
* Font sizes → edit `.title`, `.range`, `table`
* Table spacing → edit `th, td` padding

Regenerate PNGs afterward.

---

## **📌 Summary**

This system:

* Reads CSV daily salaat times
* Detects current or all Friday-based weeks
* Renders modern flyers using your custom CSS
* Outputs PNGs suitable for screens, WhatsApp, or weekly announcements
* Optionally syncs to Google Drive

Everything runs fully automated on a Raspberry Pi.

---

If you want, I can also generate:

* a **GitHub Actions workflow**
* a **one-line installer script**
* a **cron job** for weekly auto-generation
