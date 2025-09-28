from __future__ import annotations

from pathlib import Path

from ..log_setup import setup_logger  # type: ignore
from ..constants import OUT_DIR, LLM_JSONL_PATH  # type: ignore
from ..part04.internal_stability import compute_llm_internal_icc
from ..part04.plot_part04 import generate_part04_plots
from ..part05.bias_analysis import compute_disagreement_summary, plot_disagreement_violin


def main():
    out_dir = Path(OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(__name__, logfile=out_dir / "part04_05.log")
    logger.info("Starting Part 4 & 5…")
    # Part 4
    dpath, spath = compute_llm_internal_icc(out_dir, LLM_JSONL_PATH)
    logger.info("Part 4 ICC detail: %s", dpath)
    logger.info("Part 4 ICC summary: %s", spath)
    generate_part04_plots(out_dir)
    logger.info("Part 4 plots saved under: %s", out_dir / "plots")
    # Part 5
    sump = compute_disagreement_summary(out_dir)
    logger.info("Part 5 disagreement summary: %s", sump)
    plot_disagreement_violin(out_dir)
    logger.info("Part 5 plots saved under: %s", out_dir / "plots")


if __name__ == "__main__":
    main()

