# SnapSort

SnapSort is a small Python desktop application for organizing photos and videos into folders by year and month.

I originally built this project as one of my first Python applications. I later revisited it to audit the file-handling logic, 
fix reliability issues, and improve the code while preserving the original architecture and behavior.

## Demo

[Watch the 30-second SnapSort demo on YouTube](https://youtu.be/6VITpNUsIZU)

## What it does

SnapSort recursively scans a selected folder and organizes supported media files into folders named in the `YYYY-MM` format.

For images:

- `.jpg`
- `.jpeg`
- `.png`

SnapSort first looks for the EXIF `DateTimeOriginal` value. If a usable EXIF date is unavailable, 
it falls back to the file system modification date.

For videos:

- `.mp4`
- `.mov`
- `.3gp`

the file system modification date is used.

Unsupported or unreadable files are moved to:

```text
__problem_files__
```

so that a single problematic file does not stop the rest of the sorting process.

## Reliability and safety behavior

The current version includes several safeguards:

- Existing destination files are never overwritten. A numeric suffix is added when necessary.
- Running SnapSort repeatedly does not rename files that are already in the correct destination folder.
- The `__problem_files__` directory is excluded from recursive processing.
- Conflicting filenames inside `__problem_files__` are handled without overwriting existing files.
- Invalid EXIF dates fall back safely instead of producing malformed destination folders.
- Errors affecting individual files are logged without stopping the entire batch.
- Image files are opened using a context manager so resources are closed correctly.
- Empty source directories are removed after processing when possible.

## Interface

SnapSort uses a simple Tkinter GUI that allows the user to:

1. Select a folder.
2. Start sorting.
3. View processing messages in a log window.
4. Clear the log.

## Requirements

- Python 3
- Pillow
- Tkinter

Install Pillow with:

```bash
python -m pip install Pillow
```

Tkinter is included with standard Python installations on Windows.

## Running the application

Clone the repository:

```bash
git clone https://github.com/ludmila-winckowska/SnapSort.git
```

Open the project directory:

```bash
cd SnapSort
```

Run:

```bash
python SnapSort.py
```

## Project history

SnapSort is intentionally kept as an evolution of my original project rather than being rewritten from scratch.

The Git history contains the earlier version of the application as well as the later reliability-focused revision.
 This preserves the development process and makes the improvements visible over time.

The revised version was reviewed and tested for:

- syntax correctness;
- image sorting;
- repeated runs;
- unreadable image handling;
- filename collisions;
- preservation of files already stored in `__problem_files__`.

## Current scope

SnapSort remains a small learning project rather than a production file-management tool.

Its current design intentionally keeps several characteristics of the original implementation, including:

- synchronous GUI processing;
- recursive directory traversal;
- file-system modification dates for videos;
- modification-date fallback for images without usable EXIF metadata;
- moving unsupported files into `__problem_files__`;
- removal of empty directories after sorting.

These choices are documented rather than hidden because the purpose of this repository is also 
to show how an early project was reviewed and improved over time.

## Technologies

- Python
- Tkinter
- Pillow
- EXIF metadata
- Git / GitHub