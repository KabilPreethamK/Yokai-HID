import time
import wifi
import socketpool
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

    # Wi-Fi credentials
ssid = "Your SSID"
password = "Your PASSWORD"

    # Connect to Wi-Fi
print("Connecting to Wi-Fi...")
wifi.radio.connect(ssid, password)
print("Connected! IP:", wifi.radio.ipv4_address)

    # Keyboard
keyboard = Keyboard(usb_hid.devices)

    # Setup socket server
pool = socketpool.SocketPool(wifi.radio)
server = pool.socket()
server.bind((str(wifi.radio.ipv4_address), 80))
server.listen(1)
server.settimeout(None)

NUMERIC_KEYCODES = {
    '0': Keycode.ZERO,
    '1': Keycode.ONE,
    '2': Keycode.TWO,
    '3': Keycode.THREE,
    '4': Keycode.FOUR,
    '5': Keycode.FIVE,
    '6': Keycode.SIX,
    '7': Keycode.SEVEN,
    '8': Keycode.EIGHT,
    '9': Keycode.NINE,
}

SPECIAL_CHAR_MAP = {
    ' ': Keycode.SPACE,
    '-': Keycode.MINUS,
    '=': Keycode.EQUALS,
    '[': Keycode.LEFT_BRACKET,
    ']': Keycode.RIGHT_BRACKET,
    '\\': Keycode.BACKSLASH,
    ';': Keycode.SEMICOLON,
    "'": Keycode.QUOTE,
    '`': Keycode.GRAVE_ACCENT,
    ',': Keycode.COMMA,
    '.': Keycode.PERIOD,
    '/': Keycode.FORWARD_SLASH,
    '\n': Keycode.ENTER,
    '$$': Keycode.ENTER,
    '\t': Keycode.TAB,
    '!': (Keycode.ONE, True),
    '@': (Keycode.TWO, True),
    '#': (Keycode.THREE, True),
    '$': (Keycode.FOUR, True),
    '%': (Keycode.FIVE, True),
    '^': (Keycode.SIX, True),
    '&': (Keycode.SEVEN, True),
    '*': (Keycode.EIGHT, True),
    '(': (Keycode.NINE, True),
    ')': (Keycode.ZERO, True),
    '_': (Keycode.MINUS, True),
    '+': (Keycode.EQUALS, True),
    '{': (Keycode.LEFT_BRACKET, True),
    '}': (Keycode.RIGHT_BRACKET, True),
    '|': (Keycode.BACKSLASH, True),
    ':': (Keycode.SEMICOLON, True),
    '"': (Keycode.QUOTE, True),
    '~': (Keycode.GRAVE_ACCENT, True),
    '<': (Keycode.COMMA, True),
    '>': (Keycode.PERIOD, True),
    '?': (Keycode.FORWARD_SLASH, True),
}

def type_text(text):
    for char in text:
        if char.isalpha():
            key = getattr(Keycode, char.upper())
            if char.isupper():
                keyboard.press(Keycode.SHIFT, key)
                time.sleep(0.01)
                keyboard.release(Keycode.SHIFT, key)
            else:
                keyboard.press(key)
                time.sleep(0.01)
                keyboard.release(key)
        elif char in NUMERIC_KEYCODES:
            key = NUMERIC_KEYCODES[char]
            keyboard.press(key)
            time.sleep(0.01)
            keyboard.release(key)
        elif char in SPECIAL_CHAR_MAP:
            val = SPECIAL_CHAR_MAP[char]
            if isinstance(val, tuple):
                keyboard.press(Keycode.SHIFT, val[0])
                time.sleep(0.01)
                keyboard.release(Keycode.SHIFT, val[0])
            else:
                keyboard.press(val)
                time.sleep(0.01)
                keyboard.release(val)
        else:
            print(f"[WARN] Unsupported character: {char}")
            continue

        time.sleep(0.05)
while True:
    conn, addr = server.accept()
    print("Client connected from:", addr)

    try:
        buffer = bytearray(1024)
        recv_len = conn.recv_into(buffer)
        if recv_len == 0:
            conn.close()
            continue

        request_raw = buffer[:recv_len].decode("utf-8")
        print("Request received:\n", request_raw)
        
        if "POST /" in request_raw:
                # Extract content length
            content_length = 0
            lines = request_raw.split("\r\n")
            for line in lines:
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":")[1].strip())

                # Extract the body
            if "\r\n\r\n" in request_raw:
                body = request_raw.split("\r\n\r\n", 1)[1]
                while len(body) < content_length:
                        # receive remaining data if incomplete
                    more = bytearray(1024)
                    read_len = conn.recv_into(more)
                    body += more[:read_len].decode("utf-8")

                print("Command to type:", body)
                type_text(body.strip())

                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nCommand typed."
            else:
                response = "HTTP/1.1 400 Bad Request\r\n\r\nMissing body."

        else:
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\nOnly POST is supported."

        conn.send(response.encode("utf-8"))

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()
