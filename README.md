# eWeLink Python Library and CLI Utility

A clean, reusable Python library and command-line interface (CLI) to interact with the eWeLink V2 API (coolkit.cc). Designed for easy local development and distribution on GitHub.

## Features

- **OAuth Authentication**: Full 2-step OAuth login logic.
- **Token Persistence**: Automatically saves and loads your access token to/from `.env`.
- **Device Management**: List all registered smart home devices/things.
- **Device Control**: Send state changes (`on` / `off`) to single-channel or multi-channel smart switches/plugs.
- **CLI Wrapper**: Perform actions directly from your terminal.

---

## Installation

To install the library locally in editable mode (so any changes you make in the code are immediately available in the command line tool):

```bash
pip install -e .
```

Alternatively, install dependencies directly:

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the root of your directory with the following variables:

```env
# eWeLink Application Credentials (from eWeLink Developer Console)
EWELINK_APP_ID=your_app_id
EWELINK_APP_SECRET=your_app_secret

# eWeLink User Account Details
EWELINK_EMAIL=your_email@example.com
EWELINK_PASSWORD=your_password
```

---

## CLI Usage

Once installed, you can use the `ewelink` CLI command:

### 1. Log In (Generate Access Token)
Authenticates with your credentials and writes the access token to `.env`:
```bash
ewelink login
```

### 2. List Devices
Retrieves all registered devices and prints a table of names, IDs, online status, UIID types, and switch state:
```bash
ewelink list
```

### 3. Control Devices
Turn a device on or off.
- **Single-channel device**:
  ```bash
  ewelink on <device_id>
  ewelink off <device_id>
  ```
- **Multi-channel device (specifying outlet index)**:
  ```bash
  ewelink on <device_id> --outlet 0
  ewelink off <device_id> --outlet 1
  ```

### 4. Fetch Full Device Status JSON
```bash
ewelink status <device_id>
```

---

## Library (OOP) Usage

You can import `EwelinkClient` into your own Python projects:

```python
from ewelink import EwelinkClient

# 1. Initialize Client (loads credentials from .env)
client = EwelinkClient()

# 2. Login (not needed if you already have a valid EWELINK_ACCESS_TOKEN in .env)
# client.login()

# 3. List devices
devices = client.list_devices()
for dev in devices:
    item = dev["itemData"]
    print(f"Device: {item['name']} | ID: {item['deviceid']}")

# 4. Turn a device ON
client.control_device("1000abc123", "on")

# 5. Turn a multi-channel outlet OFF (e.g., outlet index 0)
client.control_device("1000xyz789", "off", outlet=0)
```
