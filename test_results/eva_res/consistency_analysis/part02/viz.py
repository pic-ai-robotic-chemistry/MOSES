from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional


def _import_vis_config_module():
    cfg_path = Path("test_results/eva_res/vis/config/vis_config.py")
    if not cfg_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("vis_config", str(cfg_path))
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def apply_vis_style():
    mod = _import_vis_config_module()
    if mod is None:
        return
    try:
        # Prefer calling the module's setup to respect its style choices
        if hasattr(mod, "setup_plot_style"):
            mod.setup_plot_style()  # type: ignore
            return
    except Exception:
        pass
    # Fallback minimal style
    try:
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import seaborn as sns
        plt.style.use('default')
        sns.set_context('talk')
        mpl.rcParams.update({'axes.grid': True, 'grid.alpha': 0.3})
    except Exception:
        return


def get_model_color_map(canonical_models: list[str], json_name_map: Dict[str, str]) -> Dict[str, str]:
    """Return canonical->color using vis_config COLOR_SCHEME['models'] if available.
    Falls back to seaborn palette if a model color is missing.
    """
    mod = _import_vis_config_module()
    color_map: Dict[str, str] = {}
    try:
        import seaborn as sns
        fallback = sns.color_palette("tab10", n_colors=len(canonical_models))
    except Exception:
        fallback = [(0.2, 0.4, 0.6)] * len(canonical_models)

    if mod and hasattr(mod, "COLOR_SCHEME"):
        cmap = getattr(mod, "COLOR_SCHEME")
        model_colors = cmap.get('models', {}) if isinstance(cmap, dict) else {}
        for i, cm in enumerate(canonical_models):
            key = json_name_map.get(cm, cm)
            color_map[cm] = model_colors.get(key, fallback[i % len(fallback)])
        return color_map

    # Fallback if config missing
    for i, cm in enumerate(canonical_models):
        color_map[cm] = fallback[i % len(fallback)]
    return color_map


def get_model_display_names(canonical_models: list[str]) -> Dict[str, str]:
    mod = _import_vis_config_module()
    display: Dict[str, str] = {}
    if mod and hasattr(mod, "MODEL_INFO"):
        mi = getattr(mod, "MODEL_INFO", {})
        dmap = mi.get('display_names', {}) if isinstance(mi, dict) else {}
        for m in canonical_models:
            display[m] = dmap.get(m, m)
    else:
        for m in canonical_models:
            display[m] = m
    return display


def get_dimension_style(internal_dims: list[str]) -> Dict[str, Dict[str, str]]:
    """Return mapping for each internal dim key to {'label': EnglishName, 'color': hex}.
    Uses vis_config DIMENSION_INFO['display_names'] (keys in Chinese) and COLOR_SCHEME['dimensions'].
    """
    # Internal -> Chinese label map (fixed mapping)
    internal_to_zh = {
        'correctness': '正确性',
        'completeness': '完备性',
        'theoretical_depth': '理论深度',
        'rigor_and_information_density': '论述严谨性与信息密度',
    }
    mod = _import_vis_config_module()
    labels_en: Dict[str, str] = {}
    colors: Dict[str, str] = {}
    if mod:
        di = getattr(mod, 'DIMENSION_INFO', {}) if hasattr(mod, 'DIMENSION_INFO') else {}
        disp = di.get('display_names', {}) if isinstance(di, dict) else {}
        cs = getattr(mod, 'COLOR_SCHEME', {}) if hasattr(mod, 'COLOR_SCHEME') else {}
        dim_colors = cs.get('dimensions', {}) if isinstance(cs, dict) else {}
        for k in internal_dims:
            zh = internal_to_zh.get(k, k)
            labels_en[k] = disp.get(zh, k)
            colors[k] = dim_colors.get(zh, '#4C78A8')
    # fallback if config missing
    for k in internal_dims:
        labels_en.setdefault(k, k)
        colors.setdefault(k, '#4C78A8')
    return {k: {'label': labels_en[k], 'color': colors[k]} for k in internal_dims}
