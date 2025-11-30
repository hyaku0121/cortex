"""
Cortex Desktop Notification Module.
"""
import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

CONFIG_FILE = Path.home() / ".cortex" / "notify_config.json"

@dataclass
class NotifyConfig:
    enabled: bool = True; dnd_enabled: bool = True; dnd_start: str = "22:00"; dnd_end: str = "08:00"

class NotificationManager:
    def __init__(self): self.config = self._load_config()
    def _load_config(self) -> NotifyConfig:
        if not CONFIG_FILE.exists(): return NotifyConfig()
        try:
            with open(CONFIG_FILE, 'r') as f: return NotifyConfig(**json.load(f))
        except (OSError, json.JSONDecodeError, TypeError): return NotifyConfig()
    def save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        try: with open(CONFIG_FILE, 'w') as f: json.dump(self.config.__dict__, f, indent=2)
        except OSError: pass
    def _is_dnd_active(self) -> bool:
        if not self.config.dnd_enabled: return False
        now = datetime.now().time()
        try:
            s = datetime.strptime(self.config.dnd_start, "%H:%M").time()
            e = datetime.strptime(self.config.dnd_end, "%H:%M").time()
        except ValueError: return False
        if s < e: return s <= now <= e
        return now >= s or now <= e
    def send(self, title: str, message: str, level: str = "normal") -> bool:
        if not self.config.enabled: return False
        if self._is_dnd_active() and level != "critical": return False
        bin_path = shutil.which('notify-send')
        if not bin_path:
            print(f"[{level.upper()}] {title}: {message}"); return True
        u = "critical" if level == "critical" else "normal"
        try:
            subprocess.run([bin_path, title, message, "-u", u, "-a", "Cortex"], check=True, capture_output=True)
            return True
        except subprocess.SubprocessError: return False

def notify_cli(title: str, message: str, configure: bool = False, dnd_toggle: bool = False):
    m = NotificationManager()
    if configure: print(f"Current Config: {m.config}"); return
    if dnd_toggle:
        m.config.dnd_enabled = not m.config.dnd_enabled
        m.save_config()
        s = "enabled" if m.config.dnd_enabled else "disabled"
        print(f"✅ Smart DND mode {s}."); return
    if m.send(title, message): print("✅ Notification sent.")
    else: print("zzz Notification suppressed.")

if __name__ == "__main__": notify_cli("Test", "Msg")
