# Phone debug utilities and UI

default phone_debug_enabled = True
default phone_debug_show_overlay = True
default phone_debug_show_console = False
default phone_debug_log = []
default phone_debug_log_max = 200

init python:
    import datetime

    def _phone_debug_timestamp():
        try:
            now = datetime.datetime.now()
            return now.strftime("%H:%M:%S")
        except Exception:
            return "--:--:--"

    def phone_debug_safe_get(name, default="(missing)"):
        if hasattr(store, name):
            return getattr(store, name)
        return default

    def phone_debug_safe_len(obj):
        try:
            return len(obj)
        except Exception:
            return 0

    def phone_debug_add(msg):
        if not getattr(store, "phone_debug_enabled", False):
            return

        log_list = list(phone_debug_safe_get("phone_debug_log", []))
        timestamp = _phone_debug_timestamp()
        entry = f"[{timestamp}] {msg}"
        log_list.append(entry)

        max_size = phone_debug_safe_get("phone_debug_log_max", 200)
        if phone_debug_safe_len(log_list) > max_size:
            excess = phone_debug_safe_len(log_list) - max_size
            del log_list[0:excess]

        store.phone_debug_log = log_list

    def phone_debug_dump_state():
        state_lines = []

        keys_to_check = [
            "phone_mode",
            "lock_done",
            "phone_intro_done",
            "current_app",
            "current_phone_view",
            "phone_nav_stack",
            "phone_back_stack",
            "phone_choice_armed",
            "phone_choice_channel",
            "phone_pending",
            "phone_channels",
            "phone_channel_data",
            "channel_notifs",
            "channel_seen_latest",
            "channel_latest_global_id",
            "channel_last_message_id",
            "last_app",
            "phone_last_revealed_sender",
            "phone_chat_auto_advance",
            "phone_chat_auto_delay",
            "phone_chat_skip_enabled",
            "phone_chat_skip_batch_size",
            "dark_mode",
            "phone_viewport",
        ]

        for key in keys_to_check:
            value = phone_debug_safe_get(key, "(missing)")
            try:
                state_lines.append(f"{key}: {value}")
            except Exception:
                state_lines.append(f"{key}: (unprintable)")

        current = phone_debug_safe_get("current_app")
        pending = phone_debug_safe_get("phone_pending", {})
        if isinstance(pending, dict) and current in pending:
            state_lines.append(
                f"pending[{current}]: {phone_debug_safe_len(pending.get(current, []))}"
            )

        return "\n".join(state_lines)

    def phone_debug_clear_log():
        store.phone_debug_log = []

    def phone_debug_copy_log():
        if hasattr(renpy, "set_clipboard"):
            renpy.set_clipboard("\n".join(phone_debug_safe_get("phone_debug_log", [])))

    if "phone_debug_overlay" not in config.overlay_screens:
        config.overlay_screens.append("phone_debug_overlay")
    if "phone_debug_console" not in config.overlay_screens:
        config.overlay_screens.append("phone_debug_console")
    if "phone_debug_hotkeys" not in config.overlay_screens:
        config.overlay_screens.append("phone_debug_hotkeys")

screen phone_debug_overlay():
    zorder 999
    if phone_debug_enabled and phone_debug_show_overlay and phone_mode:
        frame:
            background "#000000AA"
            xalign 0.0
            yalign 0.0
            xminimum 420
            padding (10, 10)

            vbox:
                spacing 6

                hbox:
                    spacing 10
                    text "DEBUG" size 24 color "#FFFFFF" bold True
                    textbutton "DBG" action ToggleVariable("phone_debug_show_console") style "text_button"

                $ nav_stack = phone_debug_safe_get("phone_nav_stack", [])
                $ back_stack = phone_debug_safe_get("phone_back_stack", [])
                $ pending = phone_debug_safe_get("phone_pending", {})
                $ current = phone_debug_safe_get("current_app")
                $ current_view = phone_debug_safe_get("current_phone_view")
                $ channel_notifs = phone_debug_safe_get("channel_notifs", {})
                $ channel_seen_latest = phone_debug_safe_get("channel_seen_latest", {})
                $ channel_latest_global_id = phone_debug_safe_get("channel_latest_global_id", {})
                $ last_app = phone_debug_safe_get("last_app")
                $ open_channel = phone_debug_safe_get("open_channel", None)
                $ channel_data = phone_debug_safe_get("phone_channel_data", {})
                $ dark_mode_state = phone_debug_safe_get("dark_mode")
                $ auto_adv = phone_debug_safe_get("phone_chat_auto_advance")
                $ auto_delay = phone_debug_safe_get("phone_chat_auto_delay")
                $ skip_enabled = phone_debug_safe_get("phone_chat_skip_enabled")
                $ skip_batch = phone_debug_safe_get("phone_chat_skip_batch_size")
                $ viewport_adj = phone_debug_safe_get("phone_viewport", None)
                $ pending_current = phone_debug_safe_len(pending.get(current, [])) if isinstance(pending, dict) else 0
                $ channels_for_current = channel_data.get(current, {}) if isinstance(channel_data, dict) else {}
                $ notif_count = phone_debug_safe_len([k for k, v in channel_notifs.items() if v]) if isinstance(channel_notifs, dict) else 0

                text f"phone_mode: {phone_mode}"
                text f"lock_done: {phone_debug_safe_get('lock_done')}"
                text f"current_app: {current}"
                text f"current_phone_view: {current_view}"
                text f"last_app: {last_app}"
                text f"nav_stack: {nav_stack}"
                text f"back_stack: {back_stack}"
                text f"open_channel: {open_channel}"
                text f"pending({current}): {pending_current}"
                text f"channels seen latest: {channel_seen_latest.get(current, '(n/a)') if isinstance(channel_seen_latest, dict) else channel_seen_latest}"
                text f"latest_global_id({current}): {channel_latest_global_id.get(current, '(n/a)') if isinstance(channel_latest_global_id, dict) else channel_latest_global_id}"
                text f"notifs: {notif_count}"
                if isinstance(channel_notifs, dict):
                    text "notif channels: " + ", ".join([ch for ch, flagged in channel_notifs.items() if flagged])
                text f"messages revealed({current}): {phone_debug_safe_len(phone_debug_safe_get('phone_channels', {}).get(current, []))}"
                text f"channel_seen_latest[{current}]: {channel_seen_latest.get(current, '(n/a)') if isinstance(channel_seen_latest, dict) else channel_seen_latest}"
                text f"dark_mode: {dark_mode_state}"
                text f"auto_advance: {auto_adv} / delay: {auto_delay}"
                text f"skip_enabled: {skip_enabled} / batch: {skip_batch}"
                if viewport_adj:
                    text f"viewport y: {getattr(viewport_adj, 'value', '(n/a)')}"
                if isinstance(channels_for_current, dict):
                    text "channels: " + ", ".join(channels_for_current.keys())

screen phone_debug_console():
    modal True
    zorder 1000
    if phone_debug_enabled and phone_debug_show_console:
        frame:
            background "#111111DD"
            xalign 0.5
            yalign 0.5
            xsize 900
            ysize 600
            padding 20

            vbox:
                spacing 10
                text "Phone Debug Console" size 30 color "#FFFFFF" bold True

                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    xfill True
                    ymaximum 420

                    vbox:
                        spacing 5
                        for entry in phone_debug_log:
                            text entry size 18 color "#C0C0C0"

                hbox:
                    spacing 15
                    textbutton "Clear log" action Function(phone_debug_clear_log)
                    textbutton "Copy" action Function(phone_debug_copy_log)
                    textbutton "Toggle overlay" action ToggleVariable("phone_debug_show_overlay")
                    textbutton "Close" action ToggleVariable("phone_debug_show_console")

screen phone_debug_hotkeys():
    if phone_debug_enabled:
        key "K_F1" action ToggleVariable("phone_debug_show_overlay")
        key "K_F2" action ToggleVariable("phone_debug_show_console")
        key "K_F3" action Function(phone_debug_add, phone_debug_dump_state())