# Remote Keylogger 
Sends Keystrokes with time stamps, Active Software Windows & Installed Software with their License Info

This project consists of a remote client-server application that captures and logs keystrokes and installed software on the victim's machine and sends it to a remote server. The keylogger application runs silently in the background, ensuring no trace is left on the client machine. It is designed to automatically start when the system boots and silently transfers data to the server without user interaction.

## Features

- **Keystroke Logging**: Captures all keystrokes, including window changes, and sends them to the server in real-time.
- **Software Information**: Fetches the list of installed applications and their versions from the system registry and sends it to the server.
- **Silent Operation**: The client runs in the background, with no console window visible, ensuring that no traces are left on the client machine.
- **Autostart**: The client automatically starts when the system boots up, registered via Windows registry (startup task).
- **No Data Storage Locally**: No files are saved on the client machine to ensure no data is retained after the script finishes execution.

## How It Works

### Server Side
1. The server listens for incoming connections on a specified port.
2. Upon connection, it receives two types of data:
   - **Keystrokes**: Logs each key press and associated active window title, sending this information in real-time.
   - **Installed Software**: Sends a list of installed applications, their versions, and license info.

### Client Side
1. The client runs silently in the background and is registered to start automatically at system boot.
2. It fetches the installed software information from the Windows registry and sends it to the server.
3. It captures keystrokes in real-time, including any active window changes, and sends this information to the server.

## Setup & Usage

### Requirements
- Python 3.12
- Required Python libraries:
  - `socket`
  - `pywin32` (for `win32gui` and `winreg` modules)
  - `pynput` (for capturing keystrokes)
  - `ctypes` (for hiding the console window)
  - `time`
  - `threading`

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/str1k3r0p/Keylogger.git
   cd Keylogger
   ```

2. Install the necessary Python packages:

   ```bash
   pip install pynput pywin32 pyinstaller
   ```

### Running the Server

Run the server on a machine to receive the data from the client.

```bash
python server.py
```

The server will start listening on port `5001` for incoming client connections.

### Running the Client

1. Modify/Change the `SERVER_HOST` in the client script (`client.py`) to the IP address of the machine running the server.
2. To create an executable from the client script using `PyInstaller`, run:

   ```bash
   pyinstaller --onefile --noconsole --windowed keylogger.py
   ```

3. Once compiled, you can place the executable on any machine where you want the client to run. The client will automatically start on system boot and run silently in the background.

### Automatic Start on Boot (Windows)
- The client script will add itself to the Windows registry to ensure it runs on system startup:
  - `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`

### Data Flow
- **Software Information**: The client fetches and sends installed software data as plain text in the format:
  ```plaintext
  [SOFTWARE INFO]
  <software_name> (Version: <version>, License: <license_info>)
  ...
  [END SOFTWARE INFO]
  ```
  ![image](https://github.com/user-attachments/assets/5224013d-d170-44ae-84a1-d14cc9f889d3)


- **Keystroke Logs**: Every keystroke is logged along with the active window title and a timestamp.

    ```plaintext
  [Keylogs INFO]
  <TimeStamp> (Active Window: <Title>, Keystrokes: <Application Title>)
  ...
  [End of Keylogs]
  ```
- ![image](https://github.com/user-attachments/assets/4e6cc6a2-eb14-4dd0-bdf9-989f23d0e490)


### Security and Privacy Considerations

This project is meant for educational purposes or internal network use. Use responsibly and ensure compliance with privacy laws and regulations in your jurisdiction. Unauthorized use or distribution of this project could violate privacy rights.

## Contributing

Feel free to fork this repository, open issues, and submit pull requests. If you encounter any issues or have suggestions for improvements, please don't hesitate to open an issue.

## License

This project is licensed under the MIT License 
