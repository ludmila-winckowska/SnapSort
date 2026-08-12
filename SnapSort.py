import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS


def organize_folder(source_folder, log_func=print):
    # Reject an empty or invalid source path.
    if not source_folder or not os.path.isdir(source_folder):
        raise ValueError("Please select an existing folder.")

    problem_folder = os.path.join(source_folder, "__problem_files__")
    os.makedirs(problem_folder, exist_ok=True)

    # Walk top-down so the problem directory can be excluded from the traversal.
    for root, dirs, files in os.walk(source_folder):
        # Pruning here also prevents existing subdirectories inside this folder
        # from being visited by os.walk.
        dirs[:] = [
            directory for directory in dirs
            if os.path.normcase(os.path.abspath(os.path.join(root, directory)))
            != os.path.normcase(os.path.abspath(problem_folder))
        ]

        for filename in files:
            file_path = os.path.join(root, filename)
            year_month = None

            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    # getexif() is the public Pillow API and also works for images
                    # that simply do not contain EXIF metadata, including PNG files.
                    with Image.open(file_path) as image:
                        exif_data = image.getexif()
                # Keep one unreadable image from stopping the entire sorting batch.
                except Exception as e:
                    log_func(f"Error opening {filename}: {e}")
                    problem_path = os.path.join(problem_folder, filename)
                    if os.path.exists(problem_path):
                        base, ext = os.path.splitext(filename)
                        i = 1
                        while os.path.exists(problem_path):
                            problem_path = os.path.join(problem_folder, f"{base}_{i}{ext}")
                            i += 1
                    try:
                        shutil.move(file_path, problem_path)
                    except OSError as move_error:
                        log_func(f"Could not move {filename}: {move_error}")
                    continue

                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == "DateTimeOriginal":
                            try:
                                # EXIF dates use the fixed YYYY:MM:DD HH:MM:SS format.
                                taken_at = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                                year_month = f"{taken_at.year}-{taken_at.month:02d}"
                            except (TypeError, ValueError):
                                log_func(f"Invalid EXIF date -> {filename}")
                            break

            elif filename.lower().endswith((".mp4", ".mov", ".3gp")):
                try:
                    timestamp = os.path.getmtime(file_path)
                except OSError as e:
                    log_func(f"Could not read the file date for {filename}: {e}")
                    continue
                dt = datetime.fromtimestamp(timestamp)
                year_month = f"{dt.year}-{dt.month:02d}"

            else:
                problem_path = os.path.join(problem_folder, filename)
                if os.path.exists(problem_path):
                    base, ext = os.path.splitext(filename)
                    i = 1
                    while os.path.exists(problem_path):
                        problem_path = os.path.join(problem_folder, f"{base}_{i}{ext}")
                        i += 1
                try:
                    shutil.move(file_path, problem_path)
                    log_func(f"Unknown format -> {filename}")
                except OSError as e:
                    log_func(f"Could not move {filename}: {e}")
                continue

            # Fall back to the file system modification date.
            if year_month is None:
                try:
                    timestamp = os.path.getmtime(file_path)
                except OSError as e:
                    log_func(f"Could not read the file date for {filename}: {e}")
                    continue
                dt = datetime.fromtimestamp(timestamp)
                year_month = f"{dt.year}-{dt.month:02d}"

            year_folder = os.path.join(source_folder, year_month)
            os.makedirs(year_folder, exist_ok=True)

            new_path = os.path.join(year_folder, filename)

            # A repeated run must leave a file that is already in the correct
            # month folder untouched instead of renaming it as a duplicate.
            if os.path.normcase(os.path.abspath(file_path)) == os.path.normcase(os.path.abspath(new_path)):
                continue

            # Prevent an existing destination file from being overwritten.
            if os.path.exists(new_path):
                base, ext = os.path.splitext(filename)
                i = 1
                while True:
                    candidate = os.path.join(year_folder, f"{base}_{i}{ext}")
                    if not os.path.exists(candidate):
                        new_path = candidate
                        break
                    i += 1

            try:
                shutil.move(file_path, new_path)
                log_func(f"Moved: {filename} → {year_month}")
            except OSError as e:
                # A single locked or disappearing file should not stop the batch.
                log_func(f"Could not move {filename}: {e}")

    # Remove empty folders after all files have been processed.
    for root, dirs, files in os.walk(source_folder, topdown=False):
        if os.path.abspath(root) == os.path.abspath(source_folder):
            continue
        if os.path.abspath(root) == os.path.abspath(problem_folder):
            continue

        try:
            if not os.listdir(root):
                os.rmdir(root)
                log_func(f"Removed empty folder: {root}")
        except OSError as e:
            # The directory may be changed or locked while sorting is running.
            log_func(f"Could not check or remove folder {root}: {e}")


# ---------------- GUI ----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo/Video Sorter by Month")
        self.geometry("650x420")

        self.selected_folder = tk.StringVar(value="(no folder selected)")

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        tk.Button(top, text="Select Folder…", command=self.pick_folder).pack(side="left")
        tk.Label(top, textvariable=self.selected_folder, anchor="w").pack(side="left", padx=10)

        btns = tk.Frame(self)
        btns.pack(fill="x", padx=10)

        tk.Button(btns, text="Sort", command=self.run_sort).pack(side="left")
        tk.Button(btns, text="Clear Log", command=self.clear_log).pack(side="left", padx=10)

        self.log = tk.Text(self, height=18)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def pick_folder(self):
        path = filedialog.askdirectory(title="Select a folder containing photos/videos")
        if path:
            self.selected_folder.set(path)

    def log_line(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.update_idletasks()

    def clear_log(self):
        self.log.delete("1.0", "end")

    def run_sort(self):
        folder = self.selected_folder.get()
        if not folder or folder == "(no folder selected)":
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        try:
            self.log_line(f"Starting: {folder}")
            organize_folder(folder, log_func=self.log_line)
            self.log_line("Done ✅")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    App().mainloop()
