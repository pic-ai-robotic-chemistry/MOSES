from __future__ import annotations

from pathlib import Path

from ..log_setup import setup_logger  # type: ignore
from ..constants import OUT_DIR  # type: ignore
from .coach_consistency import compute_coach_kendall, compute_coach_human_internal_icc
from .plot_part03 import generate_part03_plots


def main():
    out_dir = Path(OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(__name__, logfile=out_dir / "part03_coach.log")
    logger.info("Starting Part 3: coach-view consistency…")
    kpath = compute_coach_kendall(out_dir)
    logger.info("Coach Kendall written: %s", kpath)
    hipath, hipathk = compute_coach_human_internal_icc(out_dir)
    logger.info("Coach human ICC written: %s, %s", hipath, hipathk)
    generate_part03_plots(out_dir)
    logger.info("Part 3 plots saved under: %s", out_dir / "plots")


if __name__ == "__main__":
    main()
