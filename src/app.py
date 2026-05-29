#!/usr/bin/env python3
import sys
import os
import time
import signal
import argparse

PID_FILE = os.path.join(
    os.environ.get("TEMP", "/tmp"), "myapp.pid"
)

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def read_pid():
    if not os.path.exists(PID_FILE):
        return None
    with open(PID_FILE) as f:
        content = f.read().strip()
    return int(content) if content else None

def is_running(pid):
    if pid is None:
        return False
    try:
        os.kill(pid, 0)  # signal 0 = check existence
        return True
    except (OSError, ProcessLookupError):
        return False

def run_loop():
    """The actual work the daemon does."""
    write_pid()
    print(f"App started (PID {os.getpid()})")

    def handle_term(signum, frame):
        print("Shutting down...")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_term)
    signal.signal(signal.SIGINT, handle_term)

    while True:
        # Replace with real work
        time.sleep(5)

def cmd_start(args):
    pid = read_pid()
    if is_running(pid):
        print(f"Already running (PID {pid})")
        return
    run_loop()

def cmd_stop(args):
    pid = read_pid()
    if not is_running(pid):
        print("Not running")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return
    os.kill(pid, signal.SIGTERM)
    print(f"Stopped (PID {pid})")
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def cmd_status(args):
    pid = read_pid()
    if is_running(pid):
        print(f"Active (running), PID {pid}")
        sys.exit(0)
    else:
        print("Inactive (dead)")
        sys.exit(3)  # mirrors systemctl's exit code

def main():
    parser = argparse.ArgumentParser(description="MyApp service")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("start").set_defaults(func=cmd_start)
    sub.add_parser("stop").set_defaults(func=cmd_stop)
    sub.add_parser("status").set_defaults(func=cmd_status)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
