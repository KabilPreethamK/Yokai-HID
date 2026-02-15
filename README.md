# 👹 Yokai-HID
### Advanced Remote Code Execution with Raspberry Pi Pico W

![Project Status](https://img.shields.io/badge/Status-Prototype-orange)
![Hardware](https://img.shields.io/badge/Hardware-Raspberry_Pi_Pico_W-red)
![Firmware](https://img.shields.io/badge/Firmware-CircuitPython_9.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> **"What if you could walk into a system with nothing but a USB drive and inject your AI assistant into a device?"**

**Yokai-HID** is a stealthy, low-cost (~$5), Wi-Fi-enabled Human Interface Device (HID) implant. Powered by a Raspberry Pi Pico W and CircuitPython, it allows Red Teamers and Penetration Testers to execute remote keystroke injection via simple HTTP requests over a local network.

Unlike traditional "Rubber Ducky" tools that run static scripts, **Yokai-HID** listens for dynamic commands, enabling real-time interaction, reconnaissance, and payload delivery in air-gapped or restricted environments.

Part of the **Open Network Intelligence (ONI)** initiative by [oni.ogrelix.org](https://oni.ogrelix.org).

---

## ⚠️ Disclaimer
**This tool is created for educational purposes and authorized security testing only.**
Usage of Yokai-HID for attacking targets without prior mutual consent is illegal. The developer assumes no liability and is not responsible for any misuse or damage caused by this program.

---

## 🌟 Features
* **Remote Keystroke Injection:** Type commands on the target machine wirelessly via HTTP POST.
* **Stealthy:** Identifies as a standard generic USB keyboard (no drivers required).
* **Cross-Platform:** Works on Windows, macOS, Linux, and Android.
* **Live Control:** Perfect for "Walk-in" intelligence drops or automated reconnaissance.
* **Simple API:** Send text payloads using `curl`, Python, or any HTTP client.

---

## 🛠️ Hardware & Software Requirements

### Hardware
* **Raspberry Pi Pico W** (~$6)
* Micro-USB Data Cable

### Software
* **CircuitPython 9.2.7** (or newer)
* **Adafruit CircuitPython Bundle** (specifically the `adafruit_hid` library)

---

## 🚀 Installation & Setup

### 1. Flash CircuitPython
1.  Download the latest CircuitPython `.uf2` file for Raspberry Pi Pico W from [circuitpython.org](https://circuitpython.org/board/raspberry_pi_pico_w/).
2.  Hold the `BOOTSEL` button on your Pico W and plug it into your computer.
3.  Drag and drop the `.uf2` file onto the `RPI-RP2` drive. The device will reboot and reappear as `CIRCUITPY`.

### 2. Install Libraries
1.  Download the [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle).
2.  Extract the bundle and copy the **`adafruit_hid`** folder into the `lib` folder on your `CIRCUITPY` drive.
    * Structure should look like: `CIRCUITPY/lib/adafruit_hid/`

### 3. Deploy the Code
1.  Copy the script below.
2.  Open `code.py` on your `CIRCUITPY` drive using a code editor (e.g., Thonny, VS Code, or Notepad).
3.  **Update the Wi-Fi Credentials:** Change `ssid` and `password` variables to match your network (or mobile hotspot).
4.  Save the file. The Pico W will automatically reboot and connect.

```python
import time
import wifi
import socketpool
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# --- CONFIGURATION ---
ssid = "Your_SSID"
password = "Your_PASSWORD"

# --- SETUP ---
print("Connecting to Wi-Fi...")
wifi.radio.connect(ssid, password)
print("Connected! IP:", wifi.radio.ipv4_address)

keyboard = Keyboard(usb_hid.devices)
pool = socketpool.SocketPool(wifi.radio)
server = pool.socket()
server.bind((str(wifi.radio.ipv4_address), 80))
server.listen(1)
server.settimeout(None)

# --- MAPPINGS ---
NUMERIC_KEYCODES = {'0': Keycode.ZERO, '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE, '4': Keycode.FOUR, '5': Keycode.FIVE, '6': Keycode.SIX, '7': Keycode.SEVEN, '8': Keycode.EIGHT, '9': Keycode.NINE}
SPECIAL_CHAR_MAP = {' ': Keycode.SPACE, '-': Keycode.MINUS, '=': Keycode.EQUALS, '[': Keycode.LEFT_BRACKET, ']': Keycode.RIGHT_BRACKET, '\\': Keycode.BACKSLASH, ';': Keycode.SEMICOLON, "'": Keycode.QUOTE, '`': Keycode.GRAVE_ACCENT, ',': Keycode.COMMA, '.': Keycode.PERIOD, '/': Keycode.FORWARD_SLASH, '\n': Keycode.ENTER, '$$': Keycode.ENTER, '\t': Keycode.TAB, '!': (Keycode.ONE, True), '@': (Keycode.TWO, True), '#': (Keycode.THREE, True), '$': (Keycode.FOUR, True), '%': (Keycode.FIVE, True), '^': (Keycode.SIX, True), '&': (Keycode.SEVEN, True), '*': (Keycode.EIGHT, True), '(': (Keycode.NINE, True), ')': (Keycode.ZERO, True), '_': (Keycode.MINUS, True), '+': (Keycode.EQUALS, True), '{': (Keycode.LEFT_BRACKET, True), '}': (Keycode.RIGHT_BRACKET, True), '|': (Keycode.BACKSLASH, True), ':': (Keycode.SEMICOLON, True), '"': (Keycode.QUOTE, True), '~': (Keycode.GRAVE_ACCENT, True), '<': (Keycode.COMMA, True), '>': (Keycode.PERIOD, True), '?': (Keycode.FORWARD_SLASH, True)}

def type_text(text):
    for char in text:
        if char.isalpha():
            key = getattr(Keycode, char.upper())
            if char.isupper():
                keyboard.press(Keycode.SHIFT, key); time.sleep(0.01); keyboard.release(Keycode.SHIFT, key)
            else:
                keyboard.press(key); time.sleep(0.01); keyboard.release(key)
        elif char in NUMERIC_KEYCODES:
            key = NUMERIC_KEYCODES[char]
            keyboard.press(key); time.sleep(0.01); keyboard.release(key)
        elif char in SPECIAL_CHAR_MAP:
            val = SPECIAL_CHAR_MAP[char]
            if isinstance(val, tuple):
                keyboard.press(Keycode.SHIFT, val[0]); time.sleep(0.01); keyboard.release(Keycode.SHIFT, val[0])
            else:
                keyboard.press(val); time.sleep(0.01); keyboard.release(val)
        time.sleep(0.05)

while True:
    try:
        conn, addr = server.accept()
        buffer = bytearray(1024)
        recv_len = conn.recv_into(buffer)
        if recv_len > 0:
            req = buffer[:recv_len].decode("utf-8")
            if "POST /" in req and "\r\n\r\n" in req:
                body = req.split("\r\n\r\n",
