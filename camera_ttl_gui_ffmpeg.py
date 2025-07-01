import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import serial
import time
import threading
from datetime import datetime

def send_ttl(port, duration_ms):
    try:
        with serial.Serial(port, 9600, timeout=1) as ser:
            time.sleep(2)  # Arduino reboot delay
            ser.write(b'1')
            time.sleep(duration_ms / 1000.0)
            ser.write(b'0')
    except Exception as e:
        print(f"TTL Error: {e}")

def refresh_devices(device_combo, status_label):
    try:
        result = subprocess.run(
            ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
            stderr=subprocess.PIPE, text=True
        )
        lines = result.stderr.splitlines()
        devices = [line.split('"')[1] for line in lines if '(video)' in line and '"' in line]
        if devices:
            device_combo['values'] = devices
            device_combo.current(0)
            status_label.config(text=f"Found {len(devices)} video device(s)")
        else:
            device_combo['values'] = ["No device found"]
            device_combo.current(0)
            status_label.config(text="No video devices detected.")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

def start_recording(entries, device_combo, fps_combo, res_combo, status_label):
    try:
        port = entries['Serial Port'].get()
        ttl_ms = int(entries['TTL Duration (ms)'].get())
        minutes = int(entries['Duration (min)'].get())
        seconds = int(entries['Duration (sec)'].get())
        duration = minutes * 60 + seconds

        device = device_combo.get()
        framerate = fps_combo.get()
        resolution = res_combo.get()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"record_{timestamp}.mp4"
        
        # Start TTL before recording
        threading.Thread(target=send_ttl, args=(port, ttl_ms), daemon=True).start()

        # Schedule TTL stop at the end
        def delayed_ttl():
            time.sleep(duration)
            send_ttl(port, ttl_ms)

        threading.Thread(target=delayed_ttl, daemon=True).start()

        # Run FFmpeg
        cmd = [
            'ffmpeg', '-y', '-f', 'dshow',
            '-framerate', framerate,
            '-video_size', resolution,
            '-rtbufsize', '512M',
            '-t', str(duration),
            '-i', f'video={device}',
            '-vcodec', 'libx264', '-preset', 'ultrafast', filename
        ]
        status_label.config(text=f"Recording to: {filename}")
        subprocess.run(cmd)
        status_label.config(text=f"Finished: {filename}")

    except Exception as e:
        status_label.config(text=f"Error: {e}")

# GUI
root = tk.Tk()
root.title("FFmpeg TTL Recorder")
root.geometry("680x560")

labels = ['Serial Port', 'TTL Duration (ms)', 'Duration (min)', 'Duration (sec)']
entries = {}
for i, label in enumerate(labels):
    tk.Label(root, text=label).place(x=30 + (i%2)*300, y=30 + (i//2)*40)
    entry = tk.Entry(root)
    entry.place(x=150 + (i%2)*300, y=30 + (i//2)*40, width=100)
    entry.insert(0, 'COM4' if 'Serial' in label else '500' if 'TTL' in label else '0' if 'min' in label else '10')
    entries[label] = entry

# Device Dropdown
tk.Label(root, text="Video Device:").place(x=30, y=130)
device_combo = ttk.Combobox(root, state="readonly", width=40)
device_combo.place(x=150, y=130)
tk.Button(root, text="Refresh", command=lambda: refresh_devices(device_combo, status_label)).place(x=500, y=130)

# Frame Rate
tk.Label(root, text="Frame Rate:").place(x=30, y=180)
fps_combo = ttk.Combobox(root, state="readonly", values=["15", "30", "60"])
fps_combo.place(x=150, y=180)
fps_combo.current(1)

# Resolution
tk.Label(root, text="Resolution:").place(x=300, y=180)
res_combo = ttk.Combobox(root, state="readonly", values=["640x480", "1280x720", "1920x1080"])
res_combo.place(x=400, y=180)
res_combo.current(1)

# Start Button
tk.Button(root, text="Start Recording", font=("Arial", 12), bg="#4CAF50", fg="white", width=18,
          command=lambda: start_recording(entries, device_combo, fps_combo, res_combo, status_label)).place(x=240, y=240)

# Status Label
status_label = tk.Label(root, text="Status: Ready", anchor="w", width=80, fg="blue")
status_label.place(x=30, y=300)

root.mainloop()
