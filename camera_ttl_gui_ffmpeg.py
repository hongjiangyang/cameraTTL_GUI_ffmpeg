
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import serial
import time
import threading

def send_ttl(port, duration_ms):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # 等待 Arduino 重启
        ser.write(b'1')
        time.sleep(duration_ms / 1000)
        ser.write(b'0')
        ser.close()
    except Exception as e:
        print(f"TTL Error: {e}")

def list_video_devices():
    try:
        result = subprocess.run(
            ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='ignore'
        )
        output = result.stdout.splitlines()
        devices = [line for line in output if '(video)' in line and '"' in line]
        device_names = []
        for line in devices:
            start = line.find('"') + 1
            end = line.find('"', start)
            device_names.append(line[start:end])
        return device_names
    except Exception as e:
        print(f"Device list error: {e}")
        return []

def start_recording():
    port = entry_port.get()
    ttl_duration = int(entry_ttl.get())
    min_duration = int(entry_min.get())
    sec_duration = int(entry_sec.get())
    duration = min_duration * 60 + sec_duration
    framerate = int(combo_fps.get())
    resolution = combo_res.get()
    selected_device = combo_device.get()

    if not selected_device:
        messagebox.showerror("Error", "Please select a video device.")
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"record_{timestamp}.mp4"

    # 发送开始 TTL
    threading.Thread(target=send_ttl, args=(port, ttl_duration), daemon=True).start()

    cmd = [
        'ffmpeg', '-y',
        '-f', 'dshow',
        '-framerate', str(framerate),
        '-video_size', resolution,
        '-rtbufsize', '512M',
        '-t', str(duration),
        '-i', f'video={selected_device}',
        '-vcodec', 'libx264',
        '-preset', 'ultrafast',
        filename
    ]

    label_status.config(text=f"Recording to: {filename}")

    def run_ffmpeg():
        subprocess.run(cmd)
        label_status.config(text=f"Finished: {filename}")
        # 发送结束 TTL
        send_ttl(port, ttl_duration)

    threading.Thread(target=run_ffmpeg, daemon=True).start()

def refresh_devices():
    combo_device['values'] = ["Searching..."]
    combo_device.current(0)
    root.update()
    devices = list_video_devices()
    if devices:
        combo_device['values'] = devices
        combo_device.current(0)
        label_status.config(text=f"Found {len(devices)} video device(s).")
    else:
        combo_device['values'] = ["No device found"]
        combo_device.current(0)
        label_status.config(text="No video devices detected.")

root = tk.Tk()
root.title("FFmpeg TTL Recorder")
root.geometry("660x520")
root.configure(bg="#f2f2f2")

tk.Label(root, text="Serial Port:", bg="#f2f2f2").place(x=30, y=460)
entry_port = tk.Entry(root)
entry_port.insert(0, "COM4")
entry_port.place(x=130, y=460, width=100)

tk.Label(root, text="TTL Duration (ms):", bg="#f2f2f2").place(x=250, y=460)
entry_ttl = tk.Entry(root)
entry_ttl.insert(0, "500")
entry_ttl.place(x=360, y=460, width=80)

tk.Label(root, text="Duration (min):", bg="#f2f2f2").place(x=30, y=420)
entry_min = tk.Entry(root)
entry_min.insert(0, "0")
entry_min.place(x=130, y=420, width=50)

tk.Label(root, text="Duration (sec):", bg="#f2f2f2").place(x=190, y=420)
entry_sec = tk.Entry(root)
entry_sec.insert(0, "10")
entry_sec.place(x=290, y=420, width=50)

tk.Label(root, text="Video Device:", bg="#f2f2f2").place(x=30, y=380)
combo_device = ttk.Combobox(root, values=["Click Refresh"])
combo_device.place(x=130, y=380, width=300)

btn_refresh = tk.Button(root, text="Refresh", command=refresh_devices)
btn_refresh.place(x=440, y=380, width=100)

tk.Label(root, text="Frame Rate:", bg="#f2f2f2").place(x=30, y=340)
combo_fps = ttk.Combobox(root, values=["15", "30", "60"])
combo_fps.current(1)
combo_fps.place(x=130, y=340, width=100)

tk.Label(root, text="Resolution:", bg="#f2f2f2").place(x=250, y=340)
combo_res = ttk.Combobox(root, values=["640x480", "1280x720", "1920x1080"])
combo_res.current(1)
combo_res.place(x=360, y=340, width=140)

btn_record = tk.Button(root, text="Start Recording", font=("Arial", 10), command=start_recording)
btn_record.place(x=270, y=280, width=120, height=40)

label_status = tk.Label(root, text="Status: Ready", bg="#f2f2f2", anchor="w", font=("Arial", 10))
label_status.place(x=30, y=230, width=580, height=30)

root.mainloop()
