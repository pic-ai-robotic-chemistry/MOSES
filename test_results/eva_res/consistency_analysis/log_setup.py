from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def _ensure_handler(logger: logging.Logger, handler: logging.Handler) -> None:
    # Avoid duplicate handlers if called multiple times
    for h in logger.handlers:
        if (
            isinstance(h, handler.__class__)
            and getattr(h, "baseFilename", None) == getattr(handler, "baseFilename", None)
        ):
            return
    logger.addHandler(handler)


def setup_root_logger(level: int = logging.INFO, logfile: Optional[Path] = None) -> logging.Logger:
    """Configure the root logger so that all module loggers propagate here.

    Returns the root logger. Safe to call multiple times.
    """
    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(fmt)
    _ensure_handler(root, sh)

    if logfile is not None:
        logfile.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(str(logfile), encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(fmt)
        _ensure_handler(root, fh)

    return root


def setup_logger(name: str, level: int = logging.INFO, logfile: Optional[Path] = None) -> logging.Logger:
    """Configure a named logger and also ensure root has handlers.

    This makes logs from sibling modules (e.g., loaders) visible too.
    """
    root = setup_root_logger(level=level, logfile=logfile)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Use root handlers (propagate=True by default)
    return logger
