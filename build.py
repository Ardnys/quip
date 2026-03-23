#!/usr/bin/env python3
"""
quip build script
-----------------
Usage:
    uv run build.py              # folder release

Output:
    dist/quip/          folder release
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
DIST = ROOT / "dist"
RELEASE_DIR = DIST / "quip"

# currently no need to add dynamic stuff to the template
BAT_TEMPLATE = """@echo off
echo Starting quip...
cd /d "%~dp0backend"

set EXTRAS=

:parse_args
if "%~1"=="--with-redaction" (
    set EXTRAS=%EXTRAS% --extra redaction
    shift
    goto parse_args
)

uv run %EXTRAS% python main.py
pause
"""

README_TEMPLATE = """quip
====

Requirements:
  - uv (install from https://docs.astral.sh/uv/getting-started/installation/)
  - VB-Cable or similar virtual audio device

To run:
  Double-click quip.bat
  It should open in your browser automatically.
  Or manually open http://127.0.0.1:9119 in your browser.
"""


def run(cmd, cwd=None):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"  ✗ Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def build_frontend():
    print("\n── Building frontend ──────────────────────────────────────")
    run(["npm", "install"], cwd=FRONTEND)
    run(["npm", "run", "build"], cwd=FRONTEND)
    dist = FRONTEND / "dist"
    if not dist.exists():
        print("  ✗ frontend/dist not found after build")
        sys.exit(1)
    print(f"  ✓ Frontend built → {dist}")
    return dist


def build_folder_release(frontend_dist: Path):
    print("\n── Building folder release ────────────────────────────────")

    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True)

    # Copy backend source
    backend_dest = RELEASE_DIR / "backend"
    shutil.copytree(
        BACKEND,
        backend_dest,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".venv", ".pytest_cache", "*.egg-info"
        ),
    )

    # Copy built frontend into backend/static/app
    # aiohttp will serve it from there
    static_dest = backend_dest / "static" / "app"
    if static_dest.exists():
        shutil.rmtree(static_dest)
    shutil.copytree(frontend_dist, static_dest)
    print("  ✓ Frontend assets → backend/static/app/")

    # Write the launcher .bat
    launcher = RELEASE_DIR / "quip.bat"
    launcher.write_text(BAT_TEMPLATE)
    print(f"  ✓ Launcher → {launcher}")

    # Write a README for the release
    readme = RELEASE_DIR / "README.txt"
    readme.write_text(README_TEMPLATE)

    size = sum(f.stat().st_size for f in RELEASE_DIR.rglob("*") if f.is_file())
    print(f"  ✓ Release folder: {RELEASE_DIR}")
    print(f"  ✓ Total size: {size / 1_048_576:.1f} MB")


def main():
    print("quip build")
    print("==========")

    frontend_dist = build_frontend()

    build_folder_release(frontend_dist)

    print("\n✓ Done.\n")


if __name__ == "__main__":
    main()
