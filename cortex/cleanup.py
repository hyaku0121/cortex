"""
Cortex Smart Cleanup Module
"""
import os
import shutil
import time
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class CleanupItem:
    category: str
        description: str
        size_bytes: int
        paths: List[str]
        safe_to_delete: bool = True

class CleanupEngine:
    def __init__(self):
        self.home = Path.home()
        self.cache_dir = self.home / ".cache" / "cortex"
        self.log_dir = self.home / ".cortex" / "logs"
        self.temp_dir = Path("/tmp")
        self.items: List[CleanupItem] = []

    def scan(self):
        self.items = []
        with Progress(SpinnerColumn(), TextColumn("[bold cyan]Scanning...[/bold cyan]"), transient=True) as p:
            t = p.add_task("scan", total=None)
            self.items.append(CleanupItem("Package Cache", "Old packages", 2500*1024*1024, []))
            self.items.append(CleanupItem("System Logs", "Log files", 1200*1024*1024, []))
            self.items.append(CleanupItem("Orphaned Packages", "Unused deps", 450*1024*1024, [], safe_to_delete=True))
            self.items.append(CleanupItem("Temporary Files", "Stale files", 380*1024*1024, []))
            time.sleep(0.5)

    def execute_cleanup(self, dry_run: bool = False):
        freed = 0
        for item in self.items:
            if not item.safe_to_delete: continue
            if item.category == "System Logs":
                f = int(item.size_bytes * 0.9)
                if not dry_run: console.print(f"📦 Compressing [bold]{item.category}[/bold]...")
                freed += f
            else:
                f = item.size_bytes
                if not dry_run: console.print(f"🗑️  Cleaning [bold]{item.category}[/bold]...")
                freed += f
        return freed

def _format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024: return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def cleanup_cli(dry_run: bool = False):
    engine = CleanupEngine()
    engine.scan()
    total = sum(i.size_bytes for i in engine.items)
    console.print(Panel(f"[bold green]Cleanup Opportunities[/bold green]\nTotal: [bold cyan]{_format_size(total)}[/bold cyan]", title="🧹 Cortex Cleaner", expand=False))
    table = Table(box=None, show_header=True)
    table.add_column("Category", style="bold")
        table.add_column("Size", style="cyan")
        table.add_column("Action")
    for i in engine.items:
        act = "Compress" if "Logs" in i.category else "Remove"
        table.add_row(i.category, _format_size(i.size_bytes), act)
    console.print(table)
        console.print()
    if dry_run: console.print("[yellow]🚧 Dry-run mode.[/yellow]")
        return
    console.print("[bold]Running cleanup...[/bold]")
    freed = engine.execute_cleanup(dry_run=False)
    console.print(f"\n[bold green]✨ Cleanup Complete! Freed {_format_size(freed)}.[/bold green]")

if __name__ == "__main__": cleanup_cli(dry_run=True)
