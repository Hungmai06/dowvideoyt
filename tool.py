import os
import tkinter as tk
from tkinter import filedialog

def time_to_ms(t):
    hms, ms = t.split(',')
    h, m, s = map(int, hms.split(':'))
    return (h*3600 + m*60 + s) * 1000 + int(ms)

def ms_to_time(ms):
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def clean_srt(input_file, output_file):
    subs = []

    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        blocks = f.read().strip().split("\n\n")

    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 2:
            continue

        if "-->" not in lines[1]:
            continue

        start, end = lines[1].split(" --> ")
        text = " ".join(lines[2:])

        try:
            start_ms = time_to_ms(start.strip())
            end_ms = time_to_ms(end.strip())
            subs.append([start_ms, end_ms, text])
        except:
            continue

    for i in range(1, len(subs)):
        if subs[i][0] < subs[i-1][1]:
            subs[i][0] = subs[i-1][1] + 10

    with open(output_file, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(subs, 1):
            f.write(f"{i}\n")
            f.write(f"{ms_to_time(start)} --> {ms_to_time(end)}\n")
            f.write(f"{text}\n\n")

root = tk.Tk()
root.withdraw()

input_file = filedialog.askopenfilename(
    title="Chọn file SRT",
    filetypes=[("Subtitle", "*.srt")]
)

if not input_file:
    print("Không chọn file")
    exit()

save_folder = filedialog.askdirectory(title="Chọn thư mục lưu")

if not save_folder:
    print("Không chọn thư mục")
    exit()

filename = os.path.basename(input_file)
output_file = os.path.join(save_folder, filename)

clean_srt(input_file, output_file)

print("✔ File đã tạo:", output_file)