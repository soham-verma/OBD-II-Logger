#!/usr/bin/env python3
import obd, json, time, os
from datetime import datetime, timezone

DATA_DIR     = "/home/dummy/obd_logs"
RAW_LOG_NAME = "full_obd_dump.jsonl"
POLL_INTERVAL = 1.0  # seconds

def iso_ts():
    return datetime.now(timezone.utc).isoformat()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    ensure_dir(DATA_DIR)
    log_path = os.path.join(DATA_DIR, RAW_LOG_NAME)

    # 1) connect to the adapter (auto-detect USB/Bluetooth)
    conn = obd.OBD(fast=False, timeout=1)
    if not conn.is_connected():
        print(f"{iso_ts()} No OBD adapter found, exiting.")
        return

    # 2) get list of supported commands
    # python-OBD will probe your car and populate `supported_commands`
    supported = getattr(conn, "supported_commands", None)
    if not supported:
        # fallback: attempt every command in the library
        from obd import commands as cmdmod
        supported = [getattr(cmdmod, name)
                     for name in dir(cmdmod)
                     if not name.startswith("_")
                     and isinstance(getattr(cmdmod, name), obd.OBDCommand)]
    print(f"{iso_ts()} Connected on {conn.port_name!r}")
    print(f"{iso_ts()} Supported sensors: {[c.name for c in supported]}")

    # 3) open the JSONL file
    with open(log_path, "a") as fout:
        print(f"{iso_ts()} → Logging all supported sensors to {log_path}")
        try:
            while True:
                record = {"timestamp": iso_ts()}
                for cmd in supported:
                    try:
                        resp = conn.query(cmd)
                        record[cmd.name] = (resp.value.magnitude
                                            if resp.value else None)
                    except Exception as e:
                        record[cmd.name] = None
                        # note: you could log to a separate error file here
                fout.write(json.dumps(record) + "\n")
                fout.flush()
                print(record)
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            pass
        finally:
            conn.close()
            print(f"{iso_ts()} Stopped logging.")

if __name__ == "__main__":
    main()
