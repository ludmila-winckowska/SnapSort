# SnapSort

SnapSort is a simple Python GUI application 
that organizes photos and videos into 
folders by **year and month** based on file 
date information.

## Features

- Sorts photos (`.jpg`, `.jpeg`, `.png`) using **EXIF DateTimeOriginal**
- Falls back to system file modification date if EXIF is missing
- Sorts videos (`.mp4`, `.mov`, `.3gp`) using file modification date
- Moves unknown or unsupported files to `__problem_files__`
- Automatically removes empty folders after sorting
- Prevents overwriting by adding suffixes (`_1`, `_2`, etc.) if a file already exists

## How to Use

1. Launch the application.
2. Click **"Select Folder…"** and choose a folder containing photos/videos.
3. Click **"Sort"**.
4. Monitor progress in the application log window.

## Supported Formats

**Photos:** `.jpg`, `.jpeg`, `.png`  
**Videos:** `.mp4`, `.mov`, `.3gp`

## Requirements (if running from source)

- Python 3.8+
- Pillow library

Install Pillow:

```bash
pip install pillow

Run:

python PhotoVideoSorter_GUI.py

Build as .exe 
(optional)

The project can be packaged into a Windows 
executable using PyInstaller.



Important


The application moves files (it does not copy them).

It is recommended to create a backup before 
sorting important data.