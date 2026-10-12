"""Release this benchmark process's idle host memory between MathSpecs.

Never changes system caches, swap, GPU state or a research-result spool. Native
GPU workers must already have retired/exited before the caller invokes this.
"""
import ctypes
import gc
from pathlib import Path
import sys


def process_memory():
    """Current resident/swap bytes, not the nondecreasing ru_maxrss peak."""
    result = dict(status='UNAVAILABLE', rss_bytes=None, swap_bytes=None)
    try:
        fields = {}
        for line in Path('/proc/self/status').read_text().splitlines():
            key, _, value = line.partition(':')
            if key in ('VmRSS', 'VmSwap'):
                fields[key] = int(value.split()[0]) * 1024
        if 'VmRSS' in fields:
            result.update(status='MEASURED', rss_bytes=fields['VmRSS'],
                          swap_bytes=fields.get('VmSwap'))
    except (OSError, ValueError, IndexError):
        pass
    return result


def trim_allocator():
    """Optional glibc reclamation of unused heap pages, local to this process."""
    if not sys.platform.startswith('linux'):
        return 'UNAVAILABLE'
    try:
        trim = ctypes.CDLL(None).malloc_trim
        trim.argtypes = [ctypes.c_size_t]
        trim.restype = ctypes.c_int
        return 'RELEASED' if trim(0) else 'NO_RELEASABLE_PAGES'
    except (AttributeError, OSError):
        return 'UNAVAILABLE'


def release_idle_memory():
    before = process_memory()
    cleared = []
    # Clear only known, pure memoization caches, after all oracle checks. Do
    # not import a module just to clear it or touch the mathematical functions.
    oracle = sys.modules.get('science_library.f32')
    if oracle is not None:
        for name in ('rational', 'sqrt'):
            clear = getattr(getattr(oracle, name, None), 'cache_clear', None)
            if clear is not None:
                clear()
                cleared.append('science_library.f32.' + name)
    collected = gc.collect()
    allocator = trim_allocator()
    after = process_memory()
    available = before['rss_bytes'] is not None and after['rss_bytes'] is not None
    return dict(status='COMPLETED', scope='CURRENT_PROCESS_IDLE_HOST_MEMORY_ONLY',
                before=before, after=after,
                rss_released_bytes=before['rss_bytes']-after['rss_bytes'] if available else None,
                collected_objects=collected, cleared_caches=cleared,
                allocator_trim=allocator, gpu_memory='UNAVAILABLE',
                system_memory_modified=False)
