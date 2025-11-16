WEEKLY SALAAT FLYER GENERATOR
=============================

Overview
--------
This project generates a weekly Salaat Times flyer as a high-quality 1080p PNG image.
The flyer is built from a CSV file containing prayer times and is rendered using HTML/CSS.
The output PNG can be uploaded to GitHub, Google Drive, or shown on digital displays.

IMPORTANT: All flyer generation should be done on Windows for perfect font rendering,
because the CSS uses Segoe UI and Windows is the only system where spacing, kerning,
and line layout match exactly. The Raspberry Pi should NOT generate flyers — it should
only display or download PNGs.

Directory Structure
-------------------
/salaattimes
    input/
        salaat_times.csv        - source CSV with all dates and jamā‘at times
        blank_flyer.png         - background image (modern border + large cream area)
        salaatfont.ttf (optional) - if you want a custom embedded font
    output/
        salaat_week_YYYY-MM-DD_to_YYYY-MM-DD.png   - generated flyers
    generate_flyers.py          - main generator script
    README.txt                  - this file

Workflow Summary
----------------
1. Edit styles and layout in HTML/CSS inside generate_flyers.py.
2. Run generate_flyers.py on WINDOWS (important).
3. Script:
      - Loads the CSV
      - Extracts the week’s prayer times (Fri → Thu)
      - Generates an HTML file
      - Renders it with headless Chromium into a clean PNG
4. Upload PNGs to GitHub or Google Drive.
5. Raspberry Pi simply displays or downloads final PNGs—no generation occurs on Pi.

Why Windows?
------------
The CSS uses:
    system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif

On Windows → This resolves to Segoe UI → Correct spacing and perfect alignment.

On Raspberry Pi → Fonts fall back to DejaVu/Liberation → Different spacing.
Even though the HTML is identical, Chromium on Pi renders text too closely,
causing tables to look compressed.

Fonts = layout, so the Pi can NEVER match your Windows preview exactly.

Therefore:
    Windows = generate flyers
    Raspberry Pi = show flyers only

Running the Script
------------------
Open PowerShell or Command Prompt on Windows:

    cd C:\path\to\salaattimes
    python generate_flyers.py

To generate all weeks:

    python generate_flyers.py --all-weeks

Output PNGs appear in:

    salaattimes/output/

These are final-quality PNGs and should be uploaded to GitHub or Google Drive.

CSV Format
----------
The CSV must contain these jamā‘at columns:

    Fajr_jamah
    Zuhr_jamah
    Asr_jamah
    Maghrib_jamah
    Isha_jamah

The script ignores azan columns and uses only jamā‘at times.

HTML/CSS Layout
---------------
The flyer uses the blank_flyer.png as a background.
CSS positions the table inside the cream area and includes:

    - Centered title: “Bait-ul-Aafiyat Mosque”
    - Week range: “Nov 7 – Nov 13”
    - Table showing Day / Fajr / Zuhr / Asr / Maghrib / Isha
    - No spaces inside times (e.g. 6:15AM)

You may edit layout directly in the CSS block inside generate_flyers.py.

Using a Custom Font (Optional)
------------------------------
Add a .ttf font into /input and include this in CSS:

    @font-face {
        font-family: 'SalaatFont';
        src: url('salaatfont.ttf');
    }

Then use:

    font-family: 'SalaatFont', sans-serif;

This ensures Windows + Chromium render identically.

Raspberry Pi Usage
------------------
The Pi should NOT render flyers.

Instead:
    - Download PNGs from GitHub or Google Drive
    - Display them on monitors or slideshow systems

This avoids:
    - Wrong fonts
    - Rendering inconsistencies
    - Heavy CPU usage on Pi

Google Drive Upload
-------------------
If rclone is installed, you can sync output with:

    rclone copy output/ drive:TV\ Display\ Slides --progress

GitHub Upload
-------------
Simply commit the output directory:

    git add output/
    git commit -m "Add latest weekly flyer"
    git push

This makes your PNGs available for automation or preview.

Summary
-------
✔ Windows generates flawless flyers  
✔ Raspberry Pi only displays them  
✔ Consistent layout, fonts, and spacing  
✔ Easy template editing via HTML/CSS  
✔ Automatic weekly PNG creation  

This README describes the full project workflow, installation, directory layout,
generation process, and architectural choices.
