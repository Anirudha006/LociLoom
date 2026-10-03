"""
LociLoom UI Helper (core/ui_helper.py)
Re-exports and extends UI components from core/ui.py for backwards compatibility across all pages.
"""
from core.ui import (
    load_css,
    inject_theme_css,
    setup_page,
    render_sidebar,
    render_disclaimer,
    get_or_init_anon_id,
    init_accessibility_state,
    format_loci_id,
    get_animated_login_map_html,
    get_animated_sample_map_html,
    page_header,
    card,
    info_banner,
    footer,
    CSS_PATH,
    t,
    sign_out_user
)

__all__ = [
    "load_css",
    "inject_theme_css",
    "setup_page",
    "render_sidebar",
    "render_disclaimer",
    "get_or_init_anon_id",
    "init_accessibility_state",
    "format_loci_id",
    "get_animated_login_map_html",
    "get_animated_sample_map_html",
    "page_header",
    "card",
    "info_banner",
    "footer",
    "CSS_PATH",
    "t",
    "sign_out_user"
]
