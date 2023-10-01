from __future__ import annotations

import contextlib
import tracemalloc

from rich.console import Console
from rich.live import Live
from rich.table import Table


class StatsDisplay(contextlib.ExitStack):
    def __init__(self, top_n: int = 10) -> None:
        super().__init__()
        self.top_n = top_n
        self.console = Console()
        self.live: Live

    def __enter__(self):
        super().__enter__()
        self.live = self.enter_context(Live(console=self.console))
        return self

    def __exit__(self, *args, **kwargs):
        return

    def _format_size(self, size: int, signed: bool) -> str:
        return tracemalloc._format_size(size, signed)  # type: ignore

    def table_for_stats(
        self, stat: list[tracemalloc.StatisticDiff], *, title: str = ""
    ) -> Table:
        table = Table(title=title or "memleek")
        table.add_column(
            "File", justify="left", style="cyan", no_wrap=False, overflow="fold"
        )
        table.add_column("Size", justify="right", style="cyan", no_wrap=True)
        table.add_column("Count", justify="right", style="cyan", no_wrap=True)

        for s in stat[: self.top_n]:
            size = self._format_size(s.size, False)
            size_diff = self._format_size(s.size_diff, True)
            size_data = f"{size} ({size_diff})"
            count_data = f"{s.count} (+{s.count_diff})"
            table.add_row(str(s.traceback), size_data, count_data)
        return table

    def show_stats(
        self, stats: list[tracemalloc.StatisticDiff], *, title: str = "Stats"
    ):
        """
        Show difference in stats from an initial
        """
        table = self.table_for_stats(stats, title=title)
        self.live.update(table, refresh=True)
