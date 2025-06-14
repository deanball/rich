"""Utilities to integrate Rich with the click framework."""

from __future__ import annotations

from typing import Optional, Any

import click
from rich.console import Console


_DEF_CONSOLE: Console | None = None


def install(console: Optional[Console] = None) -> Console:
    """Patch ``click.echo`` so that it writes with Rich ``Console``.

    Args:
        console: Optional console instance to use, otherwise a new one is
            created.

    Returns:
        The :class:`~rich.console.Console` used for output.
    """
    global _DEF_CONSOLE
    _DEF_CONSOLE = console or Console()

    def _rich_echo(
        message: Any | None = None,
        file: Any | None = None,
        nl: bool = True,
        err: bool = False,
        color: Any | None = None,
    ) -> None:
        if message is not None:
            _DEF_CONSOLE.print(message)
        if nl:
            _DEF_CONSOLE.print()

    click.echo = _rich_echo  # type: ignore[assignment]
    return _DEF_CONSOLE


class RichGroup(click.Group):
    """Subclass of ``click.Group`` that renders help with Rich."""

    def get_help(self, ctx: click.Context) -> str:  # pragma: no cover - thin wrapper
        console = _DEF_CONSOLE or Console()
        with console.capture() as capture:
            console.print(super().get_help(ctx))
        return capture.get()
