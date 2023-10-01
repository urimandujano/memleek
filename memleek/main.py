from __future__ import annotations

import tracemalloc
import typing as t

from memleek.display import StatsDisplay


class MemoryProfiler:
    def __init__(
        self,
        *,
        display: StatsDisplay | None = None,
        filters: t.Optional[list[tracemalloc.Filter]] = None,
        summarize: bool = True,
    ) -> None:
        self.snaps: list[tracemalloc.Snapshot] = []
        self.display = display or StatsDisplay()
        self.filters = filters or [
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
            tracemalloc.Filter(False, "<unknown>"),
            tracemalloc.Filter(False, "*tracemalloc.py"),
            tracemalloc.Filter(False, "*/rich/*"),
        ]
        self.summarize = summarize

    def __enter__(self):
        tracemalloc.start()
        self.snap()
        with self.display:
            pass
        return self

    def __exit__(self, *args, **kwargs):
        if self.summarize:
            self.display_overall_stats()
        tracemalloc.clear_traces()

    def snap(self):
        s = tracemalloc.take_snapshot()
        s = s.filter_traces(self.filters)
        self.snaps.append(s)

    @property
    def iter_stats(self) -> t.Iterator[list[tracemalloc.StatisticDiff]]:
        """
        Generate stats for each subsequent snapshot
        """
        curr_snap = self.snaps[0]
        for s in self.snaps[1:]:
            yield s.compare_to(curr_snap, "lineno")
            curr_snap = s

    @property
    def latest_stats(self) -> list[tracemalloc.StatisticDiff]:
        """
        Generate stats for the last two snapshots
        """
        penultimate_snap = self.snaps[-2]
        latest_snap = self.snaps[-1]
        return latest_snap.compare_to(penultimate_snap, "lineno")

    @property
    def overall_stats(self) -> list[tracemalloc.StatisticDiff]:
        """
        Generate stats for the first and last snapshots
        """
        first_snap = self.snaps[0]
        final_snap = self.snaps[-1]
        return final_snap.compare_to(first_snap, "lineno")

    def display_overall_stats(self):
        self.display.show_stats(
            self.overall_stats,
            title=f"Diff from start to end for {len(self.snaps)-1} snapshots",
        )

    def display_latest_stats(self):
        self.display.show_stats(self.latest_stats, title="Diff for last two snapshots")


if __name__ == "__main__":
    with MemoryProfiler() as profiler:
        for i in range(2):
            # expensive work
            profiler.snap()
