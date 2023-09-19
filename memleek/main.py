import tracemalloc

import typing as t
from rich.table import Table
from rich.console import Console


class MemoryProfiler:
    def __init__(self, filters: t.Optional[list] = None, n_stats: int = 10) -> None:
        self.snaps: list[tracemalloc.Snapshot] = []
        self.filters = filters or [
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
            tracemalloc.Filter(False, "<unknown>"),
        ]
        self.n_stats = n_stats

    def __enter__(self):
        tracemalloc.start()
        self.snap()
        return self

    def __exit__(self, *args, **kwargs):
        return

    @staticmethod
    def table_for_stats(
        stat: list[tracemalloc.StatisticDiff], *, title: str = "", num_entries: int = 10
    ) -> Table:
        table = Table(title=title or "memleek")
        table.add_column("File", justify="left", style="cyan", no_wrap=False)
        table.add_column("Size", justify="right", style="cyan", no_wrap=True)
        table.add_column("Count", justify="right", style="cyan", no_wrap=True)

        for s in stat[:num_entries]:
            size = tracemalloc._format_size(s.size, False)
            size_diff = tracemalloc._format_size(s.size_diff, True)
            size_data = f"{size} ({size_diff})"
            count_data = f"{s.count} (+{s.count_diff})"
            table.add_row(str(s.traceback), size_data, count_data)
        return table

    def snap(self):
        s = tracemalloc.take_snapshot()
        s = s.filter_traces(self.filters)
        self.snaps.append(s)

    def compare_between_snapshots(self):
        """
        See the memory difference between subsequent snapshots
        """
        curr_snap = self.snaps[0]
        for i, s in enumerate(self.snaps[1:]):
            stats = s.compare_to(curr_snap, "lineno")
            # for stat in stats[: self.n_stats]:
            #    print(stat)
            table = self.table_for_stats(
                stats,
                title=f"Stats between {i-1}th and {i}th snapshots",
                num_entries=self.n_stats,
            )
            console = Console()
            console.print(table)

            curr_snap = s

    def compare_overall(self):
        """
        See the memory difference between the first and last snapshots
        """
        orig_snap = self.snaps[0]
        final_snap = self.snaps[-1]

        stats = final_snap.compare_to(orig_snap, "lineno")
        table = self.table_for_stats(
            stats,
            title="Stats between first and last snapshot",
            num_entries=self.n_stats,
        )

        console = Console()
        console.print(table)
