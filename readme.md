````markdown
# Universal OBD-II Logger

Headless, auto-starting OBD-II data logger for Raspberry Pi (or any Linux system) using ELM327-compatible USB/Bluetooth adapters. Logs core vehicle metrics and all additional supported PID data into JSONL files.

---

## Table of Contents

1. [Full Install Process](#full-install-process)
2. [Setup and Run Instructions](#setup-and-run-instructions)
3. [Example Output](#example-output)
4. [Extending for GPS Time & Location](#extending-for-gps-time--location)
5. [Known Limitations](#known-limitations)

---

## Repository Contents

- **`obd_reader.py`**  - Logs filtered core OBD metrics (RPM, speed, throttle, coolant temp, DTCs).
- **`reader_all.py`**  - Logs all supported PIDs automatically discovered via python-OBD.
- **`obd_logger.service`** - Systemd unit file to auto-start the chosen script on boot.

---

## Full Install Process

Requires a clean Raspberry Pi OS installation with internet access and an ELM327 adapter.

1. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
````

2. **Install Python & venv**:

   ```bash
   sudo apt install -y python3 python3-venv python3-full
   ```
3. **Create project dir**:

   ```bash
   mkdir -p /home/pi/obd-logger && cd /home/pi/obd-logger
   ```
4. **Copy files** into `/home/pi/obd-logger`:

   * `obd_reader.py`
   * `reader_all.py`
   * `obd_logger.service`
5. **Setup virtualenv & install**:

   ```bash
   python3 -m venv obd-venv
   source obd-venv/bin/activate
   pip install --upgrade pip
   pip install obd
   deactivate
   ```
6. **Prepare log directory**:

   ```bash
   sudo mkdir -p /home/pi/obd_logs
   sudo chown pi:pi /home/pi/obd_logs
   ```
7. **Make scripts executable**:

   ```bash
   chmod +x obd_reader.py reader_all.py
   ```
8. **Install & enable service**:

   ```bash
   sudo cp obd_logger.service /etc/systemd/system/obd_logger.service
   sudo systemctl daemon-reload
   sudo systemctl enable obd_logger.service
   ```

---

## Setup and Run Instructions

### Manual Run

```bash
cd /home/pi/obd-logger
source obd-venv/bin/activate
./obd_reader.py    # filtered core metrics  
# or  
./reader_all.py    # full PID discovery
```

Logs are saved in `/home/pi/obd_logs/filtered_obd.jsonl` or `/home/pi/obd_logs/full_obd_dump.jsonl` respectively.

### Automatic Startup (Systemd)

1. Edit `/etc/systemd/system/obd_logger.service` to choose script:

   ```ini
   [Service]
   ExecStart=/home/pi/obd-logger/obd-venv/bin/python /home/pi/obd-logger/obd_reader.py
   # or reader_all.py
   ```
2. Start service:

   ```bash
   sudo systemctl start obd_logger.service
   ```
3. Check logs:

   ```bash
   sudo journalctl -u obd_logger.service -f
   ```
4. On reboot, service auto-starts and logs when adapter connects.

---

## Example Output

**Filtered (`filtered_obd.jsonl`):**

```json
{"timestamp":"2025-07-11T03:45:21.213Z","rpm":1783.0,"speed_kph":54.0,"throttle_pos":12.5,"coolant_temp":85.0,"dtc":["P0128","P0300"]}
```

**Full (`full_obd_dump.jsonl`):**

```json
{"timestamp":"2025-07-11T03:46:00.123Z","rpm":1800.0,"speed_kph":55.0,"maf":12.3,"intake_pressure":101.0, ... }
```

---

## Extending for GPS Time & Location

1. **Attach GPS module** and install libraries:

   ```bash
   pip install gpsd-py3
   ```
2. **Modify script** (e.g., `obd_reader.py`) to import GPS and add fields:

   ```python
   import gpsd
   gpsd.connect()
   gps = gpsd.get_current()
   rec['latitude'] = gps.lat
   rec['longitude'] = gps.lon
   rec['gps_time'] = gps.time
   ```
3. **Restart service** to include GPS data.

---

## Known Limitations

* Only ELM327-compatible adapters supported.
* Poll rate limited by adapter (\~1 Hz per PID).
* Heavy logging (all PIDs) increases CPU & I/O load.
* System time drift if NTP unavailable—GPS extension recommended.
* Bluetooth pairing not covered here.
* Some vehicles may not support all PIDs.

```
```
