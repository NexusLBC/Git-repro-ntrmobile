init python:
    def get_text_color(is_dark_mode):
        return "#202020" if not is_dark_mode else "#f2f2f2"

    def get_selected_text_color(is_dark_mode):
        return "#4A90E2" if not is_dark_mode else "#8AB4FF"

    def get_selected_bg(is_dark_mode):
        return "#dceeff" if not is_dark_mode else "#1e3a5c"

    def get_channel_name_color(is_dark_mode):
        return "#111111" if not is_dark_mode else "#FFFFFF"

    def get_channel_preview_color(is_dark_mode):
        return "#333333" if not is_dark_mode else "#DDDDDD"

    def get_empty_state_color(is_dark_mode):
        return "#222222" if not is_dark_mode else "#DDDDDD"

    def get_sender_name_color(is_dark_mode):
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
