# Mehrab Mic Setup SOP – Phillymosque AV

This document explains the correct way to set up, balance, and control the mehrab microphones at Phillymosque for consistent, feedback-free speech audio.

---

## 🎙️ Hardware Overview

* Two mehrab mics are connected to a **Behringer Xenyx 802** analog mixer.
* The **Main Out L** of the analog mixer feeds into the **Ui24R**.
* Ui24R handles EQ, AUX sends, speaker routing, and feedback control.

---

## 🛠️ Analog Mixer Settings

| Control          | Setting                     | Notes                            |
| ---------------- | --------------------------- | -------------------------------- |
| GAIN (top white) | Set per mic, avoid red LEDs | Adjust mic input sensitivity     |
| HIGH EQ          | 12 o'clock                  | Flat                             |
| MID EQ           | 12 o'clock                  | Flat                             |
| LOW EQ           | 12 o'clock                  | Flat                             |
| PAN              | Center                      | Ensures balanced L/R output      |
| LEVEL            | \~2 o'clock                 | Lower slightly if mic feeds back |
| MAIN MIX         | \~2 o'clock                 | Controls final volume to Ui24R   |
| Phantom Power    | ON (if condenser mics used) | Leave OFF for dynamics           |

Main Out L (¼") → Ui24R mono channel (e.g., Ch 3). Leave Main Out R empty unless using stereo.

---

## 🎚️ Ui24R Channel Strip EQ (Mehrab Input)

| Frequency Range | Setting     | Purpose                                   |
| --------------- | ----------- | ----------------------------------------- |
| HPF             | 100 Hz      | Cuts low rumble                           |
| 180 Hz          | -3 dB       | Removes boominess                         |
| 250–400 Hz      | -2 to -4 dB | Cuts mud/reverb                           |
| 2–4 kHz         | +2 to +4 dB | Boosts speech clarity                     |
| 10–12 kHz       | +1 to +2 dB | Adds vocal air/sparkle                    |
| LPF             | OFF         | Do not block highs unless feedback occurs |

> ⚠️ Reduce boosts in 2–6 kHz range if feedback occurs.

---

## 📤 AUX Send Configuration (for Room Volume)

* Use the mic channel's **AUX send** to control volume in hall speakers.
* **DO NOT** lower mic fader to fix feedback — keep it at **0 dB (unity)**.

---

## 🔊 Output EQ (Speaker Bus / AFS²)

* Apply **AFS²** or **graphic EQ** to the **output channel** (AUX or Main Out feeding speakers).
* Only use this to eliminate **feedback**, not to fix mic tone.

---

## 🔁 Live Feedback Handling Workflow

1. **Reset** speaker graphic EQ / AFS² filters to flat.
2. **EQ** the mic channel using the table above.
3. **Send** signal to room using AUX send.
4. Test **full-volume speech** from mehrab.
5. If feedback occurs:

   * Run AFS² on the speaker output.
   * Reduce any EQ boosts on the mic (especially 2–6 kHz).
   * Manually notch problem frequencies if needed.

---

## 🕌 Room-Specific Notes (Phillymosque Mehrab)

* Mehrab is **U-shaped and reflective**, which causes reverb and boom.
* Point **shotgun mic (AT8035)** **off-axis**, 35–45° downward toward chest.
* For warmth, add a **Shure CVB boundary mic** to floor and blend in.
* Do not stack cuts/boosts across analog + Ui24R EQ — keep one stage neutral.

---

*Last updated: July 2025 – AV Secretary, Phillymosque*
