# Memleek

A Python in-code memory profiler built on top of `tracemalloc`

## Usage

Once installed, the profiler is used as a `contextmanager`, inside of which the
code to be profiled gets run:

```python
from memleek import MemoryProfiler

def my_sus_func():
    ...

with MemoryProfiler() as profiler:
    my_sus_func()
    profiler.snap()
```

Sample output:
```bash
                                    Diff from start to end for 2 snapshots
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ File                                                                          ┃             Size ┃    Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ /.pyenv/versions/3.8.17/lib/python3.8/sre_compile.py:780 │ 2112 B (+2112 B) │   5 (+5) │
│ /.pyenv/versions/3.8.17/lib/python3.8/sre_parse.py:529   │ 1456 B (+1456 B) │ 26 (+26) │
│ /.pyenv/versions/3.8.17/lib/python3.8/threading.py:244   │ 1248 B (+1248 B) │   4 (+4) │
└───────────────────────────────────────────────────────────────────────────────┴──────────────────┴──────────┘
```

You can also track how memory usage changes over repeated invocations:

```python
from memleek import MemoryProfiler

def my_sus_func():
    ...

with MemoryProfiler() as profiler:
    while True:
        my_sus_func()
        profiler.snap()
        profiler.display_overall_stats()
```


## Advanced usage

To control the number of stats that get displayed (aka the number of lines in
the table that gets printed to the console), create your own `StatsDisplay`
object and pass that into the `MemoryProfiler`:

```python
from memleek import MemoryProfiler, StatsDisplay # 1. Import the class

def my_sus_func():
    ...

d = StatsDisplay(top_n=3) # 2. Customize the class

with MemoryProfiler(display=d) as profiler: # 3. Use the class
    while True
        my_sus_func()
        profiler.snap()
```

The tool attempts to filter out the noisiest Python modules (those that are
consistently cluttering output to the console with data on builtins, not with
data from your code). If you want to see all of the stats on memory usage used
in your Python code, you can remove the filters like so:

```python
from memleek import MemoryProfiler

def my_sus_func():
    ...

with MemoryProfiler(filters=[]) as profiler: # 1. Use a custom, empty filters
    while True
        my_sus_func()
        profiler.snap()
```

**NOTE** Similarly, you can customize the modules that get filtered out by
creating your own instances of `tracemalloc.Filter` and passing those as
`filters` to the `MemoryProfiler` on instantiation.
