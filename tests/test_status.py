from time import sleep
from threading import Event, enumerate as enumerate_threads

import rich.live as live

from rich.console import Console
from rich.spinner import Spinner
from rich.status import Status


def test_status():
    console = Console(
        color_system=None,
        width=80,
        legacy_windows=False,
        get_time=lambda: 0.0,
        force_terminal=True,
        _environ={},
    )
    status = Status("foo", console=console)
    assert status.console == console
    previous_status_renderable = status.renderable
    status.update(status="bar", spinner_style="red", speed=2.0)

    assert previous_status_renderable == status.renderable
    assert isinstance(status.renderable, Spinner)
    status.update(spinner="dots2")
    assert previous_status_renderable != status.renderable

    stop_event = Event()

    def patched_run(self) -> None:  # type: ignore[override]
        with self.live._lock:
            if not self.done.is_set():
                self.live.refresh()
        stop_event.set()
        self.done.wait()

    original_run = live._RefreshThread.run
    live._RefreshThread.run = patched_run  # type: ignore[assignment]

    console.begin_capture()
    with status:
        assert stop_event.wait(1)
    output = console.end_capture()

    live._RefreshThread.run = original_run  # restore

    assert "\u28fe bar" in output  # \u28fe is '⣾'
    assert status._live._refresh_thread is None
    assert not status._live.is_started
    assert console._live is None

    sleep(0.05)
    assert not any(
        isinstance(t, live._RefreshThread) and t.is_alive()
        for t in enumerate_threads()
    )


def test_renderable():
    console = Console(
        color_system=None, width=80, legacy_windows=False, get_time=lambda: 0.0
    )
    status = Status("foo", console=console)
    console.begin_capture()
    console.print(status)
    assert console.end_capture() == "⠋ foo\n"
