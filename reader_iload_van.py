#!/usr/bin/env python3
import obd, json, time, os
from datetime import datetime, timezone

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
DATA_DIR      = "/home/dummy/obd_logs"
LOGFILE       = "all_obd.jsonl"
POLL_INTERVAL = 1.0  # seconds between polls

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def iso_ts():
    """UTC iso-8601 timestamp"""
    return datetime.now(timezone.utc).isoformat()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    print(f"{iso_ts()} ensure_dir: confirmed '{path}' exists")


def safe_val(v):
    """
    Convert OBDResponse values into JSON-serializable types:
    - None stays None
    - bytearray -> UTF-8 string or list of ints
    - pint quantities -> magnitude
    - other custom objects -> str(v)
    """
    if v is None:
        return None
    if isinstance(v, bytearray):
        try:
            return v.decode('utf-8', errors='ignore')
        except Exception:
            return list(v)
    # unwrap pint quantity
    magnitude = getattr(v, 'magnitude', None)
    if magnitude is not None:
        return magnitude
    # basic types
    if isinstance(v, (int, float, str, bool, list, dict)):
        return v
    # fallback
    return str(v)

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    print(f"{iso_ts()} Starting OBD logger script")
    ensure_dir(DATA_DIR)
    logfile = os.path.join(DATA_DIR, LOGFILE)
    print(f"{iso_ts()} Log file path set to '{logfile}'")

    # 1) connect to OBD-II
    print(f"{iso_ts()} Attempting to connect to OBD adapter...")
    conn = obd.OBD(fast=False, timeout=1)
    if not conn.is_connected():
        print(f"{iso_ts()} No OBD adapter found—exiting.")
        return
    print(f"{iso_ts()} Connected on port {conn.port_name!r}")

    # 2) discover supported commands (all modes)
    supported = conn.supported_commands  # set of Command objects
    print(f"{iso_ts()} Raw supported_commands count: {len(supported)}")
    core_cmds = sorted([c for c in supported if c.mode != 22], key=lambda c: c.name)
    mfg_cmds  = sorted([c for c in supported if c.mode == 22], key=lambda c: c.name)
    commands  = core_cmds + mfg_cmds
    print(f"{iso_ts()} {len(core_cmds)} core commands, {len(mfg_cmds)} mfg commands")
    if mfg_cmds:
        print(f"{iso_ts()} Manufacturer-specific PIDs: {[c.name for c in mfg_cmds]}")

    # 3) open log file
    print(f"{iso_ts()} Opening log file for append...")
    with open(logfile, "a") as f:
        print(f"{iso_ts()} Log file opened successfully")
        try:
            while True:
                record = {"timestamp": iso_ts()}
                for cmd in commands:
                    try:
                        print(f"{iso_ts()} Querying {cmd.name} (mode {cmd.mode})...")
                        resp = conn.query(cmd)
                        if resp.is_null():
                            record[cmd.name] = None
                            print(f"{iso_ts()} {cmd.name}: no data (NULL response)")
                        else:
                            val = resp.value
                            record[cmd.name] = safe_val(val)
                            print(f"{iso_ts()} {cmd.name}: {record[cmd.name]}")
                    except Exception as e:
                        record[cmd.name] = None
                        print(f"{iso_ts()} ERROR querying {cmd.name}: {e!r}")

                # write JSON line
                line = json.dumps(record)
                f.write(line + "\n")
                f.flush()
                print(f"{iso_ts()} Wrote record to file: {line}")
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print(f"{iso_ts()} KeyboardInterrupt caught — stopping logging loop")
        finally:
            conn.close()
            print(f"{iso_ts()} Connection closed, exiting.")

if __name__ == "__main__":
    main()