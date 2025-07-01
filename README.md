# FFmpeg TTL Recorder GUI

A cross-platform graphical tool built with **Python Tkinter** and **FFmpeg**,  
designed for webcam video recording and TTL control (e.g., to trigger synchronization pulses via Arduino).

---

## Features

- ✅ Graphical interface to control serial TTL output (start + end signals)
- ✅ Video recording via FFmpeg with configurable resolution, frame rate, and duration
- ✅ Automatically detects available video devices
- ✅ Compatible with Windows webcams (via DirectShow)
- ✅ Can be packaged into a standalone `.exe` application using `pyinstaller` for easy deployment

---

## File Structure

FFmpeg-TTL-Recorder/
├── camera_ttl_gui_ffmpeg.py # Main application: Python GUI source code
├── README.md # Project documentation
└── camera_ttl_gui_ffmpeg.exe # Compiled standalone app (optional)

---

## Environment Requirements

Recommended: Python 3.8+  
Install the required Python package:

```bash
pip install pyserial
```

## Install FFmpeg

https://www.gyan.dev/ffmpeg/builds/
ffmpeg-7.1.1-full_build.zip

Extract and add the following to your system Path environment variable:
C:\ffmpeg\bin

```bash
ffmpeg -version
```

## Hardware Connection (Arduino UNO)

```cpp
void setup() {
  pinMode(8, OUTPUT);
  digitalWrite(8, LOW);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      digitalWrite(8, HIGH);
      delay(500);
      digitalWrite(8, LOW);
    }
  }
}
```


