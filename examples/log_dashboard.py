"""Simple real-time dashboard combining progress and log output."""

from __future__ import annotations

import random
import time
from collections import deque
from threading import Thread

from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

# store recent log messages
log_messages: deque[tuple[str, str]] = deque(maxlen=10)


def worker(name: str, task_total: int, progress: Progress) -> None:
    task_id = progress.add_task(name, total=task_total)
    for i in range(task_total):
        time.sleep(random.uniform(0.1, 0.3))
        progress.update(task_id, advance=1)
        if i % 5 == 0:
            log_messages.append((name, f"step {i}/{task_total}"))
    log_messages.append((name, "completed"))


def make_layout() -> Group:
    log_table = Table(box=None)
    log_table.add_column("Task", style="cyan", no_wrap=True)
    log_table.add_column("Message", style="magenta")
    for task, message in log_messages:
        log_table.add_row(task, message)
    return Group(
        Panel(progress, title="Progress", border_style="green"),
        Panel(log_table, title="Logs", border_style="blue"),
    )


progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:>3.0f}%"),
    TimeElapsedColumn(),
)

threads = [
    Thread(target=worker, args=(f"job {n}", 40, progress), daemon=True)
    for n in range(1, 4)
]
for thread in threads:
    thread.start()

with Live(make_layout(), refresh_per_second=10) as live:
    while any(thread.is_alive() for thread in threads):
        live.update(make_layout())
        time.sleep(0.1)
    live.update(make_layout())
