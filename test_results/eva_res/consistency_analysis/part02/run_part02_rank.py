from __future__ import annotations

import logging
from pathlib import Path

from ..log_setup import setup_logger  # type: ignore
from ..constants import OUT_DIR  # type: ignore
from .rank_consistency import compute_rank_consistency
from .plot_part02 import generate_part02_plots
from .human_internal import compute_human_internal_icc


def main():
    out_dir = Path(OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(__name__, logfile=out_dir / "part02_rank.log")
    logger.info("Starting Part 2: model ranking consistency…")
    detail, summary = compute_rank_consistency(out_dir)
    logger.info("Part 2 written: %s", detail)
    logger.info("Part 2 summary: %s", summary)
    # Human internal consistency (2.2)
    human_icc = compute_human_internal_icc(out_dir)
    logger.info("Part 2 human internal ICC written: %s", human_icc)
    # Plots (2.1)
    generate_part02_plots(out_dir)
    logger.info("Part 2 plots saved under: %s", out_dir / "plots")
    logger.info("Done Part 2.")


if __name__ == "__main__":
    main()
