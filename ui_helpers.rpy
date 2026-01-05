init python:
    from renpy.display.im import MatrixColor

    app_colors_light = {
        "messenger": "#b4b8df",
        "gallery":  "#D97B2B",
        "settings": "#4A90E2",
        "saves":    "#6A9C3B",
    }

    app_colors_dark = {
        "messenger": "#4c4f70",
        "gallery":  "#9A4F1A",
        "settings": "#1F3A5F",
        "saves":    "#3F5F24",
    }

    def _resolve_dark_mode(is_dark_mode):
        if is_dark_mode is None:
            try:
                return bool(store.dark_mode)
            except Exception:
                return False
        return bool(is_dark_mode)

    def app_color(app_id, is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        if is_dark_mode:
            return app_colors_dark.get(app_id, "#4c4f70")
        return app_colors_light.get(app_id, "#b4b8df")

    def app_body_bg(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        if is_dark_mode:
            return "#2b2b33"
        return "#e8e7e3"

    def get_text_color(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#202020" if not is_dark_mode else "#f2f2f2"

    def get_selected_text_color(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#4A90E2" if not is_dark_mode else "#8AB4FF"

    def get_selected_bg(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#dceeff" if not is_dark_mode else "#1e3a5c"

    def get_channel_name_color(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#111111" if not is_dark_mode else "#FFFFFF"

    def get_channel_preview_color(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#333333" if not is_dark_mode else "#DDDDDD"

    def get_empty_state_color(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#222222" if not is_dark_mode else "#DDDDDD"

    def get_sender_name_color(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#000000" if not is_dark_mode else "#FFFFFF"

    def get_eta_bar_background(is_dark_mode):
        return "#000000"

    def get_nav_background(current_app):
        if current_app == "home":
            return "#00000080"
        return "#000000"

    def get_mc_avatar_path():
        if renpy.loadable("avatars/mc_icon.png"):
            return "avatars/mc_icon.png"
        return None

    def bubble_max_width():
        return int(config.screen_width * 0.7)

    def invert_if_dark(img_path, is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        if not is_dark_mode:
            return img_path

        # Inversion RGB
        inv = [
            -1, 0, 0, 0, 255,
            0,-1, 0, 0, 255,
            0, 0, -1, 0, 255,
            0, 0, 0, 1, 0
        ]
        return MatrixColor(img_path, inv)

    # -----------------------------------------------------------------------
    # UI — MSG BAR (assets / tailles / couleurs)
    # -----------------------------------------------------------------------

    # Hauteur de la barre "msg_bar" en pixels
    MSG_BAR_H = 140

    # Couleurs de fond fixes
    def msg_bar_bg(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        return "#101014" if is_dark_mode else "#d9d9df"

    # Assets
    def msg_bar_field_png(is_dark_mode=None):
        return "gui/msg_bar_field.png"

    def msg_bar_buttons_png(is_dark_mode=None):
        is_dark_mode = _resolve_dark_mode(is_dark_mode)
        if renpy.loadable("gui/msg_bar_buttons_dark.png") and renpy.loadable("gui/msg_bar_buttons_light.png"):
            return "gui/msg_bar_buttons_dark.png" if is_dark_mode else "gui/msg_bar_buttons_light.png"
        return "gui/msg_bar_buttons.png"
