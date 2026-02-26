import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS


def organize_folder(source_folder, log_func=print):
    # --- защита от пустого/неверного пути ---
    if not source_folder or not os.path.isdir(source_folder):
        raise ValueError("Нужно выбрать существующую папку.")

    problem_folder = os.path.join(source_folder, "__problem_files__")
    os.makedirs(problem_folder, exist_ok=True)

    # --- сортировка ---
    for root, dirs, files in os.walk(source_folder):
        # (не обязательно, но полезно) не лезем внутрь problem_folder
        if os.path.abspath(root) == os.path.abspath(problem_folder):
            continue

        for filename in files:
            file_path = os.path.join(root, filename)
            year_month = None

            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    image = Image.open(file_path)
                    exif_data = image._getexif()
                    image.close()
                except Exception as e:
                    log_func(f"Ошибка при открытии {filename}: {e}")
                    shutil.move(file_path, os.path.join(problem_folder, filename))
                    continue

                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == "DateTimeOriginal":
                            year = value[:4]
                            month = value[5:7]
                            year_month = f"{year}-{month}"
                            break

            elif filename.lower().endswith((".mp4", ".mov", ".3gp")):
                timestamp = os.path.getmtime(file_path)
                dt = datetime.fromtimestamp(timestamp)
                year_month = f"{dt.year}-{dt.month:02d}"

            else:
                shutil.move(file_path, os.path.join(problem_folder, filename))
                log_func(f"Неизвестный формат -> {filename}")
                continue

            # fallback по системной дате
            if year_month is None:
                timestamp = os.path.getmtime(file_path)
                dt = datetime.fromtimestamp(timestamp)
                year_month = f"{dt.year}-{dt.month:02d}"

            year_folder = os.path.join(source_folder, year_month)
            os.makedirs(year_folder, exist_ok=True)

            new_path = os.path.join(year_folder, filename)

            # --- ЗАЩИТА ОТ ПЕРЕЗАПИСИ (минимальная вставка) ---
            if os.path.exists(new_path):
                base, ext = os.path.splitext(filename)
                i = 1
                while True:
                    candidate = os.path.join(year_folder, f"{base}_{i}{ext}")
                    if not os.path.exists(candidate):
                        new_path = candidate
                        break
                    i += 1

            shutil.move(file_path, new_path)
            log_func(f"Перемещено: {filename} → {year_month}")

    # --- удаление пустых папок (в самом конце) ---
    for root, dirs, files in os.walk(source_folder, topdown=False):
        if os.path.abspath(root) == os.path.abspath(source_folder):
            continue
        if os.path.abspath(root) == os.path.abspath(problem_folder):
            continue

        if not os.listdir(root):
            os.rmdir(root)
            log_func(f"Удалена пустая папка: {root}")


# ---------------- GUI ----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Фото/видео сортировщик по месяцам")
        self.geometry("650x420")

        self.selected_folder = tk.StringVar(value="(папка не выбрана)")

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        tk.Button(top, text="Выбрать папку…", command=self.pick_folder).pack(side="left")
        tk.Label(top, textvariable=self.selected_folder, anchor="w").pack(side="left", padx=10)

        btns = tk.Frame(self)
        btns.pack(fill="x", padx=10)

        tk.Button(btns, text="Сортировать", command=self.run_sort).pack(side="left")
        tk.Button(btns, text="Очистить лог", command=self.clear_log).pack(side="left", padx=10)

        self.log = tk.Text(self, height=18)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def pick_folder(self):
        path = filedialog.askdirectory(title="Выберите папку с фото/видео")
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
        if not folder or folder == "(папка не выбрана)":
            messagebox.showwarning("Папка не выбрана", "Сначала выбери папку.")
            return

        try:
            self.log_line(f"Старт: {folder}")
            organize_folder(folder, log_func=self.log_line)
            self.log_line("Готово ✅")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    App().mainloop()
