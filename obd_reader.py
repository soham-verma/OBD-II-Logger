#!/usr/bin/env python3
import obd, json, time, os
from datetime import datetime, timezone

DATA_DIR      = "/home/dummy/obd_logs"
LOGFILE       = "obd_01.jsonl"
POLL_INTERVAL = 1.0  # seconds

# The exact OBDCommand objects we want:
WATCHED_CMDS = {
    "rpm":            obd.commands.RPM,
    "speed_kph":      obd.commands.SPEED,
    "throttle_pos":   obd.commands.THROTTLE_POS,
    "coolant_temp":   obd.commands.COOLANT_TEMP,
    "dtc":            obd.commands.GET_DTC,  # Optional: returns list of DTC codes
}

def iso_ts():
    return datetime.now(timezone.utc).isoformat()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    ensure_dir(DATA_DIR)
    logfile = os.path.join(DATA_DIR, LOGFILE)

    # 1) connect
    conn = obd.OBD(fast=False, timeout=1)
    if not conn.is_connected():
        print(f"{iso_ts()} No OBD adapter found—exiting.")
        return

    print(f"{iso_ts()} Connected on {conn.port_name!r}, logging to {logfile}")

    # 2) open log
    with open(logfile, "a") as f:
        try:
            while True:
                rec = {"timestamp": iso_ts()}
                # query just our watched commands
                for name, cmd in WATCHED_CMDS.items():
                    resp = conn.query(cmd)
                    if resp.is_null():
                        rec[name] = None
                    else:
                        # GET_DTC returns a list of codes; leave as-is
                        if name == "dtc":
                            rec[name] = resp.value or []
                        else:
                            rec[name] = resp.value.magnitude
                # write one JSON line
                f.write(json.dumps(rec) + "\n")
                f.flush()
                print(rec)
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            pass
        finally:
            conn.close()
            print(f"{iso_ts()} Stopped logging.")

if __name__=="__main__":
    main()
