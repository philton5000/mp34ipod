#!/usr/bin/env python3
"""Surveille le script et applique commit + push automatiquement."""
import os, time, subprocess, sys
FILE = "/Users/admin/Music/Latin_Playlist/download_anti_duplicate.py"
REPO = "/Users/admin/mp34ipod"
last_mtime = os.path.getmtime(FILE)
print(f"Surveillance active sur {FILE}")
while True:
    time.sleep(5)
    current_mtime = os.path.getmtime(FILE)
    if current_mtime != last_mtime:
        last_mtime = current_mtime
        # Copier dans le repo et commit/push
        subprocess.run(["cp", FILE, f"{REPO}/download_anti_duplicate.py"])
        subprocess.run(["git", "add", "-A"], cwd=REPO)
        subprocess.run(["git", "commit", "-m", "Auto : modification script - format num - titre - artiste"], cwd=REPO)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=REPO)
        print(f"[{time.ctime()}] Changement détecté -> commit + push automatique")
