from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import uvicorn

BASE_DIR = Path(__file__).resolve().parents[2]
PID_FILE = BASE_DIR / ".lectorium.pid"
LOG_FILE = BASE_DIR / ".lectorium.log"


def _read_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_host() -> str:
    return os.getenv("LECTORIUM_HOST", "127.0.0.1")


def _get_port() -> int:
    return int(os.getenv("LECTORIUM_PORT", "8000"))


def _get_reload() -> bool:
    return _read_bool(os.getenv("LECTORIUM_RELOAD", "true"))


def _is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_for_exit(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _is_running(pid):
            return True
        time.sleep(0.1)
    return not _is_running(pid)


def _load_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def run_server() -> None:
    uvicorn.run(
        "backend.app.main:app",
        host=_get_host(),
        port=_get_port(),
        reload=_get_reload(),
    )


def start_server() -> None:
    existing_pid = _load_pid()
    if existing_pid and _is_running(existing_pid):
        print(f"lectorium already running (pid {existing_pid}), restarting.")
        os.kill(existing_pid, signal.SIGTERM)
        if not _wait_for_exit(existing_pid):
            os.kill(existing_pid, signal.SIGKILL)
            _wait_for_exit(existing_pid, timeout=2.0)

    LOG_FILE.touch(exist_ok=True)
    with LOG_FILE.open("ab") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.app.main:app",
                "--host",
                _get_host(),
                "--port",
                str(_get_port()),
            ]
            + (["--reload"] if _get_reload() else []),
            stdout=log,
            stderr=log,
            start_new_session=True,
        )

    PID_FILE.write_text(str(process.pid), encoding="utf-8")
    print(f"lectorium started (pid {process.pid}).")


def stop_server() -> None:
    pid = _load_pid()
    if not pid:
        print("lectorium is not running.")
        return

    if not _is_running(pid):
        PID_FILE.unlink(missing_ok=True)
        print("lectorium is not running.")
        return

    os.kill(pid, signal.SIGTERM)
    if not _wait_for_exit(pid):
        os.kill(pid, signal.SIGKILL)
        _wait_for_exit(pid, timeout=2.0)
    PID_FILE.unlink(missing_ok=True)
    print("lectorium stopped.")


def status_server() -> None:
    pid = _load_pid()
    if pid and _is_running(pid):
        print(f"lectorium is running (pid {pid}).")
        return
    print("lectorium is not running.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="lectorium")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Run the server in the foreground")
    subparsers.add_parser("start", help="Start the server in the background")
    subparsers.add_parser("stop", help="Stop the background server")
    subparsers.add_parser("status", help="Show background server status")

    args = parser.parse_args()

    if args.command in (None, "run"):
        run_server()
        return
    if args.command == "start":
        start_server()
        return
    if args.command == "stop":
        stop_server()
        return
    if args.command == "status":
        status_server()
        return
