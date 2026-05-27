# Vendored Dependencies — engine/ky_mon

## kinqimen 0.0.6.6

- **Source**: https://github.com/kentang2017/kinqimen
- **PyPI**: https://pypi.org/project/kinqimen/
- **Author**: kentang2017
- **License**: MIT
- **Vendored on**: 2026-05-27 (YI-Chronos commit batch)

### Why vendored

1. Original package has bug `import config` (Python 2 style, không namespaced) → fail Python 3.x import. Vendoring cho phép patch local mà không touch upstream.
2. Original package declares `ephem` dependency mà `ephem` chưa build được trên Python 3.14 Mac M-series. Vendored copy chạy được `--no-deps`.

### Local patches applied

- `kinqimen.py` line 9: `import config` → `from . import config`
- Added `__init__.py` to expose `Qimen` class
- Removed `__pycache__/`

### Usage

```python
from engine.ky_mon.vendored.kinqimen import Qimen
qm = Qimen(year, month, day, hour, minute)
result = qm.pan(1)  # Chabu method, returns structured dict
```

Wrapped by `engine.ky_mon.cast` (TQ→Việt translation + paradigm enforcement).
