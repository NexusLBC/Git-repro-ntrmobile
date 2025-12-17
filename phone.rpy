# Phone main interface

default current_background = Image("gui/root_screen.png")
default dark_mode = False
default current_app = "home"
default phone_nav_stack = []
default lock_done = False
default phone_time_minutes = 8 * 60
default phone_intro_done = False
default phone_mode = False
default phone_choice_armed = False
default phone_chat_auto_advance = False
default phone_chat_auto_delay = 0.8
default phone_chat_skip_enabled = False
default phone_chat_skip_batch_size = 2
default phone_last_revealed_sender = {}
default phone_animated_global_ids = set()
default phone_deleted_state = {}
default app_cloud_state = {"feed_items": [], "filters": [], "is_syncing": False}
default app_social_soft_state = {"grid_items": [], "active_topic": None, "is_loading": False}
default app_social_hard_state = {"grid_items": [], "active_topic": None, "is_loading": False}


init python:
    import re

    PHONE_FONT_PATH = "gui/HelveticaNeueLTStd-It.otf"

    PHONE_CHAT_AUTO_DELAY_MIN = 0.2
    PHONE_CHAT_AUTO_DELAY_MAX = 5.0
    PHONE_CHAT_AUTO_DELAY_STEP = 0.1

    PHONE_CHAT_SKIP_BATCH_MIN = 1
    PHONE_CHAT_SKIP_BATCH_MAX = 10
    PHONE_CHAT_SKIP_BATCH_DEFAULT = 2


    def clamp_phone_chat_auto_delay(value):
        try:
            clamped_value = float(value)
        except (TypeError, ValueError):
            clamped_value = 0.8

        min_delay = PHONE_CHAT_AUTO_DELAY_MIN
        max_delay = min(PHONE_CHAT_AUTO_DELAY_MAX, 3.0)
        clamped_value = max(min_delay, min(max_delay, clamped_value))
        # Align to the configured step so the UI and storage stay consistent.
        rounded_steps = round((clamped_value - PHONE_CHAT_AUTO_DELAY_MIN) / PHONE_CHAT_AUTO_DELAY_STEP)
        return PHONE_CHAT_AUTO_DELAY_MIN + rounded_steps * PHONE_CHAT_AUTO_DELAY_STEP

    def clamp_phone_chat_skip_batch(batch_size):
        try:
            batch_value = int(batch_size)
        except (TypeError, ValueError):
            return PHONE_CHAT_SKIP_BATCH_DEFAULT

        return max(PHONE_CHAT_SKIP_BATCH_MIN, min(PHONE_CHAT_SKIP_BATCH_MAX, batch_value))

    def phone_font():
        if renpy.loadable(PHONE_FONT_PATH):
            return PHONE_FONT_PATH
        return gui.text_font

    def format_time(minutes_value):
        total_minutes = int(minutes_value) % (24 * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def format_phone_time(minutes_value):
        return format_time(minutes_value)

    def set_phone_time(time_string):
        match = re.match(r"^(\d{1,2}):(\d{2})$", time_string)
        if not match:
            return

        hours, minutes = match.groups()
        hours_i = max(0, min(23, int(hours)))
        minutes_i = max(0, min(59, int(minutes)))
        store.phone_time_minutes = hours_i * 60 + minutes_i

    def advance_phone_time(minutes_delta):
        store.phone_time_minutes = (store.phone_time_minutes + int(minutes_delta)) % (24 * 60)

    # ------------------------- Navigation --------------------------------------

    def set_active_app(app_id, add_history=True, clear_stack=False):
        """Update the current phone app and optionally push the previous one."""
        previous_app = store.current_app

        if clear_stack:
            store.phone_nav_stack = []

        if (
            add_history
            and previous_app is not None
            and previous_app != "home"
            and previous_app != app_id
        ):
            store.phone_nav_stack.append(previous_app)

        store.current_app = app_id

    def open_phone_app(app_id):
        """Open a top-level phone app from the home screen or another app."""
        set_active_app(app_id, add_history=(store.current_app != "home"), clear_stack=(store.current_app == "home"))

    def open_phone_channel(channel_name):
        """Open a messenger channel while keeping navigation history."""
        store.phone_choice_armed = False
        set_active_app(channel_name, add_history=True)

        last_sender = None

        if channel_name in store.phone_channels:
            for message_data in reversed(store.phone_channels[channel_name]):
                _, sender, _, message_kind, *_ = message_data

                if message_kind != 1:
                    last_sender = sender
                    break

        store.phone_last_revealed_sender[channel_name] = last_sender

    def phone_back():
        if store.disable_phone_menu_switch:
            return

        if store.phone_nav_stack:
            store.current_app = store.phone_nav_stack.pop()
        elif store.current_app != "home":
            store.current_app = "home"

    def phone_home():
        store.phone_nav_stack = []
        store.current_app = "home"

    def load_phone_chat_settings():# Phone debug utilities and UI

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
        if not hasattr(persistent, "phone_chat_auto_delay"):
            persistent.phone_chat_auto_delay = 0.8
        if not hasattr(persistent, "phone_chat_auto_advance"):
            persistent.phone_chat_auto_advance = False

        store.phone_chat_auto_delay = clamp_phone_chat_auto_delay(persistent.phone_chat_auto_delay)
        persistent.phone_chat_auto_delay = store.phone_chat_auto_delay

        store.phone_chat_auto_advance = bool(persistent.phone_chat_auto_advance)

        if not hasattr(persistent, "phone_chat_skip_enabled"):
            persistent.phone_chat_skip_enabled = store.phone_chat_skip_enabled
        store.phone_chat_skip_enabled = persistent.phone_chat_skip_enabled

        if not hasattr(persistent, "phone_chat_skip_batch_size"):
            persistent.phone_chat_skip_batch_size = PHONE_CHAT_SKIP_BATCH_DEFAULT
        store.phone_chat_skip_batch_size = clamp_phone_chat_skip_batch(persistent.phone_chat_skip_batch_size)
        persistent.phone_chat_skip_batch_size = store.phone_chat_skip_batch_size

    def set_phone_chat_auto_advance(enabled):
        store.phone_chat_auto_advance = enabled
        persistent.phone_chat_auto_advance = enabled
        renpy.restart_interaction()

    def set_phone_chat_auto_delay(delay_seconds):
        clamped_delay = clamp_phone_chat_auto_delay(delay_seconds)
        store.phone_chat_auto_delay = clamped_delay
        persistent.phone_chat_auto_delay = clamped_delay
        renpy.restart_interaction()

    def toggle_phone_chat_auto_advance():
        set_phone_chat_auto_advance(not store.phone_chat_auto_advance)

    def set_phone_chat_skip_enabled(enabled):
        store.phone_chat_skip_enabled = enabled
        persistent.phone_chat_skip_enabled = enabled
        renpy.restart_interaction()

    def toggle_phone_chat_skip_enabled():
        set_phone_chat_skip_enabled(not store.phone_chat_skip_enabled)

    def set_phone_chat_skip_batch_size(batch_size):
        clamped_batch = clamp_phone_chat_skip_batch(batch_size)
        store.phone_chat_skip_batch_size = clamped_batch
        persistent.phone_chat_skip_batch_size = clamped_batch
        renpy.restart_interaction()

    def phone_current_reveal_batch():
        if store.phone_chat_skip_enabled:
            return store.phone_chat_skip_batch_size
        return 1

    def phone_effective_auto_delay():
        if store.phone_chat_skip_enabled:
            return max(PHONE_CHAT_AUTO_DELAY_MIN, store.phone_chat_auto_delay * 0.5)
        return store.phone_chat_auto_delay

    def phone_app_title(default_title, app_id):
        if store.current_app in store.phone_channels:
            return store.phone_channel_data[store.current_app]["display_name"]
        return default_title

    #Liste des applis (message, save, galerie, patreon, itch, subsstar, settings)
    app_buttons = [
        { # Messenger
            "image": "gui/buttons/messenger_%s.png",
            "action": Function(open_phone_app, "messenger"),
        },
        { # Saves
            "image": "gui/buttons/save_%s.png",
            "action": Function(open_phone_app, "saves"),
        },
        { # Gallery
            "image": "gui/buttons/gallery_%s.png",
            "action": Function(open_phone_app, "gallery"),
        },
        { # Cloud
            "image": "gui/buttons/cloud_%s.png",
            "action": Function(open_phone_app, "app_cloud"),
        },
        { # Social (soft)
            "image": "gui/buttons/social_soft_%s.png",
            "action": Function(open_phone_app, "app_social_soft"),
        },
        { # Social (hard)
            "image": "gui/buttons/social_hard_%s.png",
            "action": Function(open_phone_app, "app_social_hard"),
        },
        { # Patreon
            "image": "gui/buttons/patreon_%s.png",
            "action": OpenURL("https://www.patreon.com/c/Darael"),
        },
        { # Itch.io
            "image": "gui/buttons/itch_%s.png",
            "action": OpenURL("https://…"),
        },
        { # Succes
            "image": "gui/buttons/achievements_%s.png",
            "action": Function(open_phone_app, "succes"),
        },
        { # Settings
            "image": "gui/buttons/settings_%s.png",
            "action": Function(open_phone_app, "settings"),
        },

        # Subscribestar

    ]

    load_phone_chat_settings()

    # Mapping of app identifiers to their corresponding screens.
    phone_screen_routes = {
        "messenger": "app_messenger",
        "gallery": "app_gallery",
        "saves": "app_saves",
        "settings": "app_settings",
        "app_cloud": "app_cloud",
        "app_social_soft": "app_social_soft",
        "app_social_hard": "app_social_hard",
    }

    #------------------------ Style, Couleurs --------------------------------

    app_colors_light = {
        "messenger": "#b4b8df",
        "gallery":  "#D97B2B",
        "settings": "#4A90E2",
        "saves":    "#6A9C3B",
        "app_cloud": "#5AA9E6",
        "app_social_soft": "#9B59B6",
        "app_social_hard": "#E67E22",
    }

    app_colors_dark = {
        "messenger": "#4c4f70",
        "gallery":  "#9A4F1A",
        "settings": "#1F3A5F",
        "saves":    "#3F5F24",
        "app_cloud": "#2D6186",
        "app_social_soft": "#6C3483",
        "app_social_hard": "#9C5310",
    }

    def app_color(app):
        if dark_mode:
            return app_colors_dark[app]
        else:
            return app_colors_light[app]

    def app_body_bg():
        if not dark_mode:
            return "#e8e7e3"
        else:
            return "#2b2b33"

    # ------------------------- Phone Config ---------------------------------------

    # configurable variables for easy plug-and-play
    phone_config = {
        # Sound Configuration
        "play_sound_send": True,
        "play_sound_receive": True,
        "no_sound_current_chat": False, # For incoming messages, only play if not viewing the chat
        # String Configurations
        "preview_no_message": "Empty chat…",
        "channels_title": "Messages",
        "history_timestamp_prefix": "Time:",
        "phone_player_name": "Me",
        "group_added": "{adder} added {participant} to the group.",
        "group_joined": "{participant} joined the group.",
        "group_left": "{participant} left the group.",
        # UI Configurations
        "message_font_size": 30,
        "bubble_max_width": 378, # target ~70% of the in-game phone width
        "message_avatar_size": 64,
        "choice_font_size": 24,
        "timestamp_font_size": 20,
        "deleted_message_duration": 3,
        "auto_scroll": True,
        "show_sender_in_preview": True,
        "default_icon": "gui/icon.png",
        "user_colour": "#FFFFFF",
        "character_colour": "#000000",
        "timestamp_colour": "#000000",
        "sort_channels_by_latest": True,
        "message_align": 0.025,
        "preview_max_length": 25,
        "emojis": {
            "size": 32,
        },
        # Gameplay Configurations
        "pause": { # no pause = messages will not wait for user time or user input before sending the next one
            "do_pause": True, # should we wait for a click to send the next message? like traditional dialogue
            "pause_time": False, # if we want to pause, should we auto-continue after a set amount of time? if false, just wait for a click
            "pause_length": 1.0 # if using pause_time, how long do we wait?
        }
    }

    def _get_deleted_state(channel_name, global_id):
        channel_state = store.phone_deleted_state.setdefault(channel_name, {})
        if global_id not in channel_state:
            channel_state[global_id] = {"visible": True, "revealed_at": None}
        return channel_state[global_id]

    def mark_deleted_message_revealed(channel_name, global_id):
        state = _get_deleted_state(channel_name, global_id)
        state["visible"] = True
        state["revealed_at"] = renpy.get_game_runtime()

    def hide_deleted_message(channel_name, global_id):
        state = _get_deleted_state(channel_name, global_id)
        state["visible"] = False
        renpy.restart_interaction()

    def toggle_deleted_message(channel_name, global_id):
        state = _get_deleted_state(channel_name, global_id)
        state["visible"] = True
        state["revealed_at"] = renpy.get_game_runtime()
        renpy.restart_interaction()

    # ------------------------- Variables --------------------------------------

    phone_channel_data = {} # {channel_name: {"display_name": "...", "icon": "...", "participants": [], "is_group": False}}
    phone_channels = {}  # {channel_name: [(id, sender, message_string, kind, ...), ...]}
    channel_last_message_id = {} # {channel_name: last_id}
    channel_seen_latest = {} # {channel_name: seen_status} (this could be more intricate to track if EACH message was seen, but that's overkill)
    channel_notifs = {} # {channel_name: notification_status} (True/False)
    channel_visible = {} # {channel_name: visible_status} (True/False)
    current_app = "home" # where when the phone starts it should start at
    disable_phone_menu_switch = False # lock back button, basically
    phone_choice_options = [] # this will hold the currently active choices
    phone_choice_channel = None  # this holds the channel that the above choice aligns to (one at a time)
    channel_latest_global_id = {} # latest global channel id
    _phone_global_message_counter = 0  # latest global message counter
    phone_pending = {}  # {channel_name: [message_data, ...]}
    phone_intro_done = False


    # ------------------------- Variables 2 ------------------------------------

    # creates a new phone channel
    def create_phone_channel(channel_id, display_name, participants, icon_path, is_group=False):
        """ Creates a new phone channel, like a DM or a group chat.
            This function sets up the basic information for a new chat conversation.
            Args:
                channel_id (str): A unique identifier for the channel (e.g., "vanessa_dm").
                display_name (str): The name that appears at the top of the chat screen.
                participants (list): A list of strings with the names of everyone in the chat.
                icon_path (str): The file path to the icon for this channel.
                is_group (bool, optional): Set to True if this is a group chat. Defaults to False.
        """
        global phone_channel_data, phone_channels, channel_last_message_id, channel_notifs, channel_seen_latest, channel_visible
        if channel_id not in phone_channel_data:
            phone_channel_data[channel_id] = {
                "display_name": display_name,
                "icon": icon_path,
                "participants": participants,
                "is_group": is_group
            }
            phone_channels[channel_id] = []
            channel_last_message_id[channel_id] = 0
            channel_notifs[channel_id] = False
            channel_seen_latest[channel_id] = True
            channel_visible[channel_id] = True
            channel_latest_global_id[channel_id] = 0

    # add messages to a channel in the phone (kind 0 = normal message, kind 1 = timestamp, kind 2 = photo, kind 3 = has emojis,
    # kind 4 = deletable text)
        # add messages to a channel in the phone
    # kind 0 = normal message, 1 = timestamp, 2 = photo, 3 = texte avec emojis, 4 = message supprimable
    PHONE_AUTOSAVE_SLOT_ID = 1

    def send_phone_message(sender, message_text, channel_name,
        message_kind=0, summary_alt="none",
        image_x=320, image_y=320, do_pause=True):
        """
        Envoie un message dans un salon de téléphone et met à jour les infos.
        """
        global _phone_global_message_counter, current_global_id

        # Sécurité : si le salon n’existe pas
        if channel_name not in phone_channels:
            renpy.log("Tried to send message to non-existent channel: " + channel_name)
            return

        # --- Son (sauf timestamps) ---
        if message_kind != 1:
            if sender == phone_config["phone_player_name"]:
                # Son d’envoi (message du joueur)
                if phone_config.get("play_sound_send", False):
                    renpy.sound.play("audio/phone/send.mp3", channel="sound")
            else:
                # Son de réception (message d’un perso)
                if phone_config.get("play_sound_receive", False):
                    renpy.sound.play("audio/phone/receive.mp3", channel="sound")

        # --- Gestion des IDs / ordres des messages ---
        _phone_global_message_counter += 1
        current_global_id = _phone_global_message_counter
        last_id = channel_last_message_id.get(channel_name, 0)
        current_id = last_id + 1
        channel_last_message_id[channel_name] = current_id

        message_data = (
            current_id,
            sender,
            message_text,
            message_kind,
            current_global_id,
            summary_alt,
            image_x,
            image_y,
            do_pause,
        )

        # Si le chat n'est pas ouvert, on met en attente (pending)
        if store.current_app != channel_name:
            phone_queue_message(message_data, channel_name)
            renpy.restart_interaction()
            return

        _deliver_phone_message(message_data, channel_name)

    def phone_queue_message(message_data, channel_name):
        if channel_name not in store.phone_pending:
            store.phone_pending[channel_name] = []
        store.phone_pending[channel_name].append(message_data)

    def _deliver_phone_message(message_data, channel_name):
        msg_id, sender, message_text, message_kind, current_global_id, summary_alt, image_x, image_y, do_pause = message_data

        # Quand on révèle un message, on force le refresh UI
        renpy.restart_interaction()

        channel_latest_global_id[channel_name] = max(
            channel_latest_global_id.get(channel_name, 0), current_global_id
        )

        channel_last_message_id[channel_name] = max(
            channel_last_message_id.get(channel_name, 0), msg_id
        )

        if message_kind == 4:
            mark_deleted_message_revealed(channel_name, current_global_id)

        phone_channels[channel_name].append(
            (
                msg_id,
                sender,
                message_text,
                message_kind,
                current_global_id,
                summary_alt,
                image_x,
                image_y,
            )
        )

        # Notifs / “non lu” uniquement pour les messages révélés
        if sender != phone_config["phone_player_name"]:
            channel_notifs[channel_name] = True
            channel_seen_latest[channel_name] = False
        else:
            channel_notifs[channel_name] = False
            channel_seen_latest[channel_name] = True

        renpy.restart_interaction()

        # --- Historique Ren'Py (pour log / rollback) ---
        if message_kind == 0:
            narrator.add_history(kind="adv", who=sender, what=message_text)
        elif message_kind == 1:
            narrator.add_history(kind="adv",
            who=phone_config["history_timestamp_prefix"],
            what=message_text)
        elif message_kind == 2:
            narrator.add_history(kind="adv",
            who=sender,
            what="Sent a photo.")
        elif message_kind == 4:
            narrator.add_history(kind="adv", who=sender, what=message_text)

        renpy.checkpoint()

        # Pause éventuelle après le message
        if do_pause and phone_config["pause"]["do_pause"]:
            if phone_config["pause"]["pause_time"]:
                renpy.pause(phone_config["pause"]["pause_length"])
            else:
                renpy.pause()

        if config.has_autosave and not renpy.in_rollback():
            renpy.save(f"auto-{PHONE_AUTOSAVE_SLOT_ID}")

    def phone_reveal_next(channel_name):
        if channel_name not in store.phone_pending:
            return False
        if not store.phone_pending[channel_name]:
            return False

        msg = store.phone_pending[channel_name].pop(0)
        _deliver_phone_message(msg, channel_name)

        _, sender, _, message_kind, *_ = msg

        if message_kind != 1:
            store.phone_last_revealed_sender[channel_name] = sender

        return True


    def phone_reveal_messages(channel_name, count=None):
        messages_to_reveal = phone_current_reveal_batch() if count is None else count

        for _ in range(messages_to_reveal):
            if not phone_reveal_next(channel_name):
                break


    def phone_next_pending_sender(channel_name):
        pending_messages = store.phone_pending.get(channel_name, [])

        for message_data in pending_messages:
            _, sender, _, message_kind, *_ = message_data

            if message_kind != 1:
                return sender

        return None


    def phone_should_auto_advance(channel_name):
        next_sender = phone_next_pending_sender(channel_name)

        return (
            store.phone_chat_auto_advance
            and channel_name in store.phone_pending
            and store.phone_pending[channel_name]
            and next_sender is not None
            and (
                store.phone_last_revealed_sender.get(channel_name, None) is None
                or next_sender == store.phone_last_revealed_sender.get(channel_name, None)
            )
        )


    # basically clear notifs / mark as read for all
    def clear_notifications():
        """ Marks all channels as read and clears all notification dots.
            This is useful for when the story starts, to clear any pre-loaded messages,
            or if you want to programmatically mark everything as seen.
        """
        global channel_notifs, channel_seen_latest
        for channel_name in phone_channel_data.keys():
            if channel_name in channel_notifs:
                channel_notifs[channel_name] = False
            if channel_name in channel_seen_latest:
                channel_seen_latest[channel_name] = True
        renpy.restart_interaction()

    # function to reset the phone data
    def reset_phone_data():
        """
        Remet à zéro toutes les données de téléphone.
        Ne crée PAS de salons par défaut : tu les créeras toi-même
        au début du jeu (Maya, etc.).
        """
        global phone_channel_data, phone_channels
        global channel_last_message_id, channel_notifs, channel_seen_latest
        global channel_visible, channel_latest_global_id, _phone_global_message_counter
        global phone_animated_global_ids

        phone_channel_data = {}
        phone_channels = {}
        channel_last_message_id = {}
        channel_notifs = {}
        channel_seen_latest = {}
        channel_visible = {}
        channel_latest_global_id = {}
        phone_animated_global_ids = set()
        _phone_global_message_counter = 0
        store.phone_intro_done = False
        store.phone_last_revealed_sender = {}

        # aucun salon créé ici
        #create_phone_channel("maya_dm", "Maya", ["Maya", phone_config["phone_player_name"]], "avatars/maya_icon.png")

        renpy.restart_interaction()

    def initialize_phone_intro():
        """Prepare the default phone content when the phone is first unlocked."""
        global _phone_global_message_counter

        if store.phone_intro_done:
            return

        if "maya_dm" not in phone_channel_data:
            create_phone_channel("maya_dm", "Maya", ["Maya", phone_config["phone_player_name"]], "avatars/maya_icon.png")

        create_phone_channel("elias_dm", "Elias", ["Elias", phone_config["phone_player_name"]], "avatars/elias_icon.png")

        # Inject the welcome message directly so it shows as unread on first detection.
        if not phone_channels.get("maya_dm"):
            _phone_global_message_counter += 1
            current_global_id = _phone_global_message_counter

            last_id = channel_last_message_id.get("maya_dm", 0) + 1
            channel_last_message_id["maya_dm"] = last_id
            channel_latest_global_id["maya_dm"] = current_global_id
            channel_notifs["maya_dm"] = True
            channel_seen_latest["maya_dm"] = False

            phone_channels["maya_dm"].append(
                (
                    last_id,
                    "Maya",
                    "Salut, tu vois ce message ?",
                    0,
                    current_global_id,
                    "none",
                    320,
                    320,
                )
            )

            renpy.restart_interaction()

        store.phone_intro_done = True


    # pause the text messages for a certain length
    def phone_pause(length=1.0):
        """ Pauses the game for a specific amount of time within the phone.
            This is a simple wrapper around renpy.pause() for convenience, allowing for
            timed delays between messages without relying on the automatic pause config.
            Args:
                length (float, optional): The duration of the pause in seconds. Defaults to 1.0.
        """
        renpy.pause(length)

    # hide the text box stuff when the phone is up
    def phone_start():
        """ Activates phone mode, preparing the UI for the phone screen.
            This function sets a flag that can be used to hide the normal
            dialogue window, ensuring the phone UI doesn't overlap with it.
            It should be called right before showing the app_messenger screen.
        """
        global phone_mode
        phone_mode = True
        renpy.restart_interaction()

    # restore the text box stuff when the phone is down
    def phone_end():
        """ Deactivates phone mode, restoring the normal game UI.
            This function resets the flag set by phone_start(), which should
            bring back the standard dialogue window. It should be called
            right after hiding the app_messenger screen.
        """
        global phone_mode
        phone_mode = False
        renpy.restart_interaction()

    # disable switching phone screens
    def lock_phone_screen():
        """ Disables the back button on the phone screen.
            This locks the player into the current view (a specific chat)
            and prevents them from returning to the channel list. Useful for
            scripted sequences where you need the player's focus.
        """
        global disable_phone_menu_switch
        disable_phone_menu_switch = True

    # enable switching phone screens
    def unlock_phone_screen():
        """ Enables the back button on the phone screen.
            This restores the player's ability to navigate back to the channel
            list from a chat view (basically just undoing the effect of lock_phone_screen()).
        """
        global disable_phone_menu_switch
        disable_phone_menu_switch = False

    # present choices to the user in the phone
    def present_phone_choices(choices, channel_name):
        """ Presents a set of choices to the player within a phone channel.
            This function displays tappable choice bubbles for the player. The game
            will pause and wait for the player to make a selection.
            Args:
                choices (list): A list of tuples defining the choices. Each tuple is in the
                    format ("preview_text", "message_to_send", action).
                    - "preview_text": The text shown on the choice button.
                    - "message_to_send": The message text that gets sent. If None, uses preview_text.
                    - "action": A Ren'Py action (like Call() or Jump()) to run after sending. Can be None.
                channel_name (str): The unique ID of the channel where the choices will appear.
        """
        # choices should be a list of tuples, like:
        # [("Choice Text 1", Jump("response_label_1")), ("Choice Text 2", Jump("response_label_2"))]
        global phone_choice_options, phone_choice_channel
        store.phone_choice_armed = False
        phone_choice_options = choices
        phone_choice_channel = channel_name
        renpy.ui.interact()  # make the game wait for the user..

    # gets the last message to show in the phone preview
    def get_channel_preview(channel_name):
        """ Gets the preview text for a channel to display on the channel list.
            This function retrieves the last message of a channel, formats it for
            the preview (e.g., adding sender for group chats, truncating), and
            returns it. It's an internal function used by the app_messenger screen.

            Args:
                channel_name (str): The unique ID of the channel to get the preview for.
        """
        if channel_name in phone_channels and phone_channels[channel_name]:
            revealed_messages = [
                msg
                for msg in phone_channels[channel_name]
                if msg[0] <= channel_last_message_id.get(channel_name, 0)
            ]
            last_message_tuple = None
            if channel_notifs.get(channel_name, False):
                for candidate in reversed(revealed_messages):
                    if candidate[3] != 1 and candidate[1] != phone_config["phone_player_name"]:
                        last_message_tuple = candidate
                        break
            if last_message_tuple is None:
                for candidate in reversed(revealed_messages):
                    if candidate[3] != 1:
                        last_message_tuple = candidate
                        break
            if last_message_tuple:
                summary_alt = last_message_tuple[5] if len(last_message_tuple) > 5 else None
                if summary_alt and summary_alt != "none":
                    return summary_alt
                sender = last_message_tuple[1]
                message_text = last_message_tuple[2]
                message_kind = last_message_tuple[3]
                message_global_id = last_message_tuple[4]
                preview_text = message_text
                if message_kind == 4:
                    state = store.phone_deleted_state.get(channel_name, {}).get(message_global_id)
                    if state and not state.get("visible", True):
                        preview_text = "Message supprimé."
                if message_kind == 3: # has emojis, get rid of them with fire
                    preview_text = re.sub(r"<[^>]+>", "", preview_text).strip()
                # prepend sender if it's a group chat and not from the player
                is_group = phone_channel_data.get(channel_name, {}).get("is_group", False)
                if is_group and sender != phone_config["phone_player_name"]:
                    full_preview = "{}: {}".format(sender, preview_text)
                else:
                    full_preview = preview_text
                max_len = phone_config.get("preview_max_length", 35)
                if len(full_preview) > max_len:
                    # Slice it to make room for the "..."
                    return full_preview[:max_len - 3] + "..."
                else:
                    return full_preview
        return phone_config["preview_no_message"]

    # force the user to go to a certain channel (can also be channel_list)
    def switch_channel_view(channel_name):
        """ Forces the phone to open a specific channel or the channel list.
            This can be used to guide the player to a new message or event in a
            different chat without requiring them to tap on it manually.
            Args:
                channel_name (str): The unique ID of the channel to switch to. Can also be
                    "channel_list" to return to the main message list.
        """
        global current_app, channel_notifs, channel_seen_latest
        current_app = channel_name
        channel_notifs[channel_name] = False
        channel_seen_latest[channel_name] = True
        renpy.restart_interaction()

    # hide a channel without deleting the data
    def hide_phone_channel(channel_name):
        """ Hides a channel from the channel list without deleting its history.
            The channel and its messages are preserved and can be made visible again
            using show_phone_channel().
            Args:
                channel_name (str): The unique ID of the channel to hide.
        """
        global channel_visible
        if channel_name in channel_visible:
            channel_visible[channel_name] = False
            renpy.restart_interaction()

    # show a channel that was hidden
    def show_phone_channel(channel_name):
        """ Makes a previously hidden channel visible again on the channel list.
            This function reverses the effect of hide_phone_channel().
            Args:
                channel_name (str): The unique ID of the channel to show.
        """
        global channel_visible
        if channel_name in channel_visible:
            channel_visible[channel_name] = True
            renpy.restart_interaction()

    # perma hide a channel aka delete it lol
    def delete_phone_channel(channel_name):
        """ Permanently deletes a channel and all of its associated data.
            This action is irreversible and will remove the channel, its messages,
            and all related settings from the phone.
            Args:
                channel_name (str): The unique ID of the channel to delete.
        """
        global phone_channel_data, phone_channels, channel_last_message_id, channel_seen_latest, channel_notifs, channel_visible, channel_latest_global_id, current_app
        if channel_name in phone_channel_data:
            del phone_channel_data[channel_name]
        if channel_name in phone_channels:
            del phone_channels[channel_name]
        if channel_name in channel_last_message_id:
            del channel_last_message_id[channel_name]
        if channel_name in channel_seen_latest:
            del channel_seen_latest[channel_name]
        if channel_name in channel_notifs:
            del channel_notifs[channel_name]
        if channel_name in channel_visible:
            del channel_visible[channel_name]
        if channel_name in channel_latest_global_id:
            del channel_latest_global_id[channel_name]
        # make sure they aren't viewing a dead chat
        if current_app == channel_name:
            switch_channel_view("channel_list")
        renpy.restart_interaction()

    # add someone to a group
    def add_participant_to_group(channel_name, new_participant_name, added_by_name=None):
        """ Adds a participant to a group chat and posts a notification message.
            This will update the channel's participant list and send a system message
            (like "X added Y to the group") to the chat.
            Args:
                channel_name (str): The unique ID of the group channel.
                new_participant_name (str): The name of the character being added.
                added_by_name (str, optional): The name of the character who added the new
                    participant. If None, a generic "joined" message is shown. Defaults to None.
        """
        if channel_name in phone_channel_data and phone_channel_data[channel_name]["is_group"]:
            phone_channel_data[channel_name]["participants"].append(new_participant_name)
            if added_by_name:
                template = phone_config.get("group_added", "{adder} added {participant} to the group.")
                message_text = template.format(adder=added_by_name, participant=new_participant_name)
            else:
                template = phone_config.get("group_joined", "{participant} joined the group.")
                message_text = template.format(participant=new_participant_name)
            send_phone_message("", message_text, channel_name, message_kind=1, do_pause=True)

    def remove_participant_from_group(channel_name, participant_to_remove):
        """Removes a participant from a group chat and posts a notification message.
            This will update the channel's participant list and send a system message
            (like "X left the group") to the chat.
            Args:
                channel_name (str): The unique ID of the group channel.
                participant_to_remove (str): The name of the character to remove.
        """
        if channel_name in phone_channel_data and phone_channel_data[channel_name]["is_group"]:
            if participant_to_remove in phone_channel_data[channel_name]["participants"]:
                phone_channel_data[channel_name]["participants"].remove(participant_to_remove)
                template = phone_config.get("group_left", "{participant} left the group.")
                message_text = template.format(participant=participant_to_remove)
                send_phone_message("", message_text, channel_name, message_kind=1, do_pause=True)

    # see if there is any current notifications at all
    def has_any_notification():
        """Checks if any channel has an active notification."""
        return any(channel_notifs.values())

    # same as above, but ignore the active channel (for instance, used to change the back icon)
    def has_any_notification_not_active():
        """Checks if any channel OTHER than the current one has an active notification."""
        return any(has_notif for channel, has_notif in channel_notifs.items() if channel != current_app)

label set_phone_time_label(time_string):
    $ set_phone_time(time_string)
    return

label advance_phone_time_label(minutes_delta=0):
    $ advance_phone_time(minutes_delta)
    return

# ---------- Styles du système de messagerie (sans thèmes) ----------

style phone_header_style is default:
    size 28
    xalign 0.5
    font phone_font()

style phone_channel_button_style is button:
    background None
    hover_background "#ffffff20"
    xpadding 10
    ypadding 8

style phone_channel_name_style is default:
    size 34
    bold True
    font phone_font()

style phone_channel_preview_style is default:
    size 22
    font phone_font()

style phone_message_style is default:
    size 24
    xalign 0.0
    font phone_font()

style phone_sender_name_style is default:
    size 18
    yoffset 2
    ypadding 0
    yalign 1.0
    font phone_font()

style phone_nav_button is button:
    background None
    hover_background None
    focus_mask True

style phone_eta_time is default:
    font phone_font()
    size 34
    color "#FFFFFF"

style phone_eta_label is default:
    font phone_font()
    size 24
    color "#FFFFFF"

# ---------- Transforms d’animation utilisés dans le chat ----------

transform message_appear(pDirection):
    alpha 0.0
    xoffset 50 * pDirection  # offset basé sur la direction
    parallel:
        ease 0.5 alpha 1.0   # fade in
    parallel:
        easein_back 0.5 xoffset 0  # slide in
    alpha 1.0

transform timestamp_appear():
    alpha 0.0
    yoffset 50
    parallel:
        ease 0.5 alpha 1.0   # fade up
    parallel:
        easein_back 0.5 yoffset 0  # slide up

transform choice_appear(delay=0.0):
    alpha 0.0
    yoffset 50
    pause delay
    parallel:
        ease 0.5 alpha 1.0   # fade up
    parallel:
        easein_back 0.5 yoffset 0  # slide up

transform scale_to_fit(maxw, maxh):
    size (maxw, maxh)
    fit "contain"

screen app_header(title, app_id, icon_path=None):

    frame:
        xfill True
        ysize 150
        background app_color(app_id)

        $ header_title = phone_app_title(title, app_id)
        $ can_go_back = current_app != "home"

        hbox:
            xfill True
            yalign 0.5
            spacing 30
            #padding (20, 20)

            if can_go_back:
                imagebutton:
                    idle "gui/back.png"
                    hover "gui/back.png"
                    xalign 0.5
                    yalign 0.5
                    action Function(phone_back)
                    sensitive not disable_phone_menu_switch
            else:
                null width 80

            hbox:
                spacing 12
                if icon_path is not None:
                    add icon_path:
                        xysize (64, 64)
                        yalign 0.5
                text header_title:
                    xalign 0.5
                    size 40

screen phone_navbar():

    zorder 100

    if not renpy.get_screen("gallery_viewer"):

        frame:
            align (0.5, 1.0)
            xfill True
            ysize 110
            padding (0, 20)

            $ nav_bg = "#00000080" if current_app == "home" else "#000000"
            add Solid(nav_bg)


            grid 3 1:
                xfill True
                yfill False

                # Bouton "Retour"
                imagebutton:
                    idle "gui/back.png"
                    hover "gui/back.png"
                    xalign 0.5
                    yalign 0.5
                    style "phone_nav_button"
                    action Function(phone_back)
                    sensitive not disable_phone_menu_switch

                # Bouton "Home" (menu principal du téléphone)
                imagebutton:
                    idle "gui/menu.png"
                    hover "gui/menu.png"
                    xalign 0.5
                    yalign 0.5
                    style "phone_nav_button"
                    action Function(phone_home)

                # Bouton "Autre" (pour plus tard)
                imagebutton:
                    idle "gui/other.png"
                    hover "gui/other.png"
                    xalign 0.5
                    yalign 0.5
                    style "phone_nav_button"
                    action NullAction()

# ------------------------- Main Menu ------------------------------------------

label Phone:
    call screen Phonescreen
    return

screen Phonescreen():

    if lock_done and not phone_intro_done:
        python:
            initialize_phone_intro()

    if current_app =="home":

        add current_background

        grid 4 5:
            xalign 0.5
            yalign 0.5
            spacing 70

            for i in range(20):

                if i < len(app_buttons):
                    $ app = app_buttons[i]

                    imagebutton:
                        auto app["image"]
                        action app["action"]
                        focus_mask True

                else:
                    null

    elif current_app == "messenger" or current_app in phone_channels:
        use app_messenger

    elif current_app in phone_screen_routes:
        use expression phone_screen_routes[current_app]

    use eta_bar
    use phone_navbar

screen eta_bar():

    zorder 110

    if not renpy.get_screen("gallery_viewer"):

        frame:
            xfill True
            ysize 90
            padding (30, 20)
            background "#00000080"

            hbox:
                xfill True
                yalign 0.5

                text format_time(phone_time_minutes):
                    style "phone_eta_time"

                null width 20

                hbox:
                    xalign 1.0
                    spacing 20

                    if renpy.loadable("gui/phone/network.png"):
                        add "gui/phone/network.png"
                    else:
                        text "NET":
                            style "phone_eta_label"

                    if renpy.loadable("gui/phone/battery.png"):
                        add "gui/phone/battery.png"
                    else:
                        text "BAT":
                            style "phone_eta_label"

#---------------------------- Messenger ----------------------------------------

screen app_messenger(auto_timer_enabled=phone_chat_auto_advance):
    modal True

    frame:
        xfill True
        yfill True
        #background app_body_bg()

        if current_app == "messenger":
            $ header_title = "Messenger"
            $ header_icon = None
        else:
            $ header_title = phone_channel_data.get(current_app, {}).get("display_name", "Messenger")
            $ header_icon = phone_channel_data.get(current_app, {}).get("icon", None)

        vbox:
            xfill True
            yfill True

            # Header adaptatif
            use app_header(phone_channel_data[current_app]["display_name"] if current_app in phone_channels else "Messenger","messenger")

            # CORPS DE L'APP
            frame:
                background app_body_bg()
                xfill True
                yfill True
                padding (30, 30, 30, 140)  # on laisse de la place pour la nav bar en bas

                if current_app == "messenger":
                    # --- LISTE DES CONVERSATIONS ---
                    viewport:
                        draggable True
                        mousewheel True
                        xfill True
                        yfill True
                        scrollbars "none"

                        vbox:
                            spacing 15
                            xfill True

                            $ visible_channels = [ch for ch in phone_channel_data.keys() if channel_visible.get(ch, True)]
                            python:
                                if phone_config["sort_channels_by_latest"]:
                                    messenger_to_display = sorted(visible_channels, key=lambda ch_name: channel_latest_global_id.get(ch_name, 0), reverse=True)
                                else:
                                    messenger_to_display = visible_channels

                            for channel_name in messenger_to_display:
                                    button:
                                        xfill True
                                        action [
                                            SetDict(channel_notifs, channel_name, False),
                                            Function(open_phone_channel, channel_name)
                                        ]
                                        background "#0000"
                                        hover_background "#ffffff20"
                                        padding (16, 12)

                                        # --- DESCRIPTIONS DES CONVERSATIONS ---
                                        vbox:
                                            # icon, name, chat last message, and notification
                                            hbox:
                                                #  icon
                                                spacing 12
                                                if renpy.loadable("gui/phone/avatar_mask.png"):
                                                    add im.AlphaMask(
                                                        phone_channel_data[channel_name]["icon"],
                                                        "gui/phone/avatar_mask.png",
                                                    ):
                                                        xysize (64, 64)
                                                        yalign 0.5
                                                else:
                                                    add phone_channel_data[channel_name]["icon"]:
                                                        xysize (64, 64)
                                                        yalign 0.5
                                                        # TODO: circle mask once an avatar mask asset is available
                                                # name and preview message
                                                vbox:
                                                    $ name_color = "#111111" if not dark_mode else "#FFFFFF"
                                                    $ preview_color = "#333333" if not dark_mode else "#DDDDDD"

                                                text phone_channel_data[channel_name]["display_name"]:
                                                    style "phone_channel_name_style"
                                                    color name_color

                                                text get_channel_preview(channel_name):
                                                    style "phone_channel_preview_style"
                                                    color preview_color

                                            # notification dot if the channel has one
                                            if channel_notifs.get(channel_name, False):
                                                frame:
                                                    background "#ff4444"
                                                    xsize 12
                                                    ysize 12
                                                    xalign 1.0
                                                    yalign 0.5
                                                    xoffset -5
                                                    yoffset 5
                                                    padding (0, 0, 0, 0)
                                        # add a line below every channel
                                        null height 14
                                        frame:
                                            background "#ffffff40"
                                            xfill True
                                            ysize 1
                else:
                    # --- CHAT DANS UNE CONVERSATION ---
                    $ yadj = ui.adjustment()

                    viewport:
                        id "message_viewport"
                        xfill True
                        yfill True
                        yadjustment yadj
                        scrollbars "none"
                        mousewheel True
                        draggable True

                        # do this once when it opens
                        if phone_config["auto_scroll"]:
                            $ yadj.value = (yadj.range + 1000)


                        fixed:
                            xfill True
                            yfill True

                            # Zone cliquable = corps du chat (header/nav sont hors viewport)
                            button:
                                xfill True
                                yfill True
                                background None
                                hover_background None
                                action Function(phone_reveal_messages, current_app)

                            # AUTO MODE : révèle automatiquement les messages en attente
                            if auto_timer_enabled and phone_should_auto_advance(current_app):
                                timer phone_effective_auto_delay() action Function(phone_reveal_messages, current_app)

                            vbox:
                                spacing 8
                                xfill True

                                if current_app in phone_channels:

                                    $ latest_channel_id = channel_last_message_id.get(current_app, 0)
                                    $ last_sender_in_chat_view = None
                                    $ mc_avatar_path = "avatars/mc_icon.png" if renpy.loadable("avatars/mc_icon.png") else None
                                    $ bubble_max_width = phone_config.get("bubble_max_width", 378)
                                    $ avatar_side = phone_config.get("message_avatar_size", 64)
                                    $ avatar_display_size = (avatar_side, avatar_side)
                                    $ avatar_slot_width = avatar_display_size[0]

                                    # display all messages
                                    for message_data in phone_channels[current_app]:
                                        $ msg_id, sender, message_text, message_kind, current_global_id, summary_alt, image_x, image_y = message_data

                                        $ should_animate = False
                                        if message_kind in (0, 2, 3, 4) and current_global_id not in phone_animated_global_ids:
                                            $ should_animate = True
                                            $ phone_animated_global_ids.add(current_global_id)

                                            if msg_id == latest_channel_id and not channel_seen_latest[current_app]:
                                                $ channel_seen_latest[current_app] = True
                                                $ channel_notifs[current_app] = False
                                                if phone_config["auto_scroll"]:
                                                    $ yadj.value = (yadj.range + 1000)

                                        # bulle et couleur selon MC / autre
                                        $ is_player_message = sender == phone_config["phone_player_name"]
                                        if is_player_message:
                                            $ msg_frame = "gui/send_frame.png"
                                            $ text_colour = "#FFFFFF"
                                            $ anim_direction = 1
                                        else:
                                            $ msg_frame = "gui/received_frame.png"
                                            $ text_colour = "#FFFFFF"
                                            $ anim_direction = -1

                                        $ msg_align = phone_config["message_align"]
                                        $ header_icon = phone_channel_data[current_app]["icon"] if not is_player_message else mc_avatar_path
                                        $ header_align = 1.0 - msg_align if is_player_message else msg_align
                                        $ name_colour = "#053ffd" if is_player_message else ("#111111" if not dark_mode else "#FFFFFF")

                                        $ display_avatar = message_kind in (0, 2, 3, 4) and sender != last_sender_in_chat_view

                                        if display_avatar:
                                            hbox:
                                                xalign header_align
                                                if is_player_message:
                                                    xanchor 1.0
                                                else:
                                                    xanchor 0.0
                                                spacing 8

                                                if header_icon and not is_player_message:
                                                    add header_icon:
                                                        xysize avatar_display_size
                                                        yalign 0.5
                                                if is_player_message:
                                                    text sender:
                                                        style "phone_sender_name_style"
                                                        color name_colour
                                                    if header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 0.5
                                                else:
                                                    text sender:
                                                        style "phone_sender_name_style"
                                                        color name_colour
                                                if not is_player_message and not header_icon:
                                                    null width avatar_slot_width

                                        # normal message : kind = 0
                                        if message_kind == 0:
                                            hbox:
                                                spacing 12
                                                xalign (1.0 - msg_align if is_player_message else msg_align)
                                                if is_player_message:
                                                    xanchor 1.0
                                                else:
                                                    xanchor 0.0

                                                if not is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width

                                                frame:
                                                    background Frame(msg_frame, 23, 23)
                                                    padding (15, 10)
                                                    xmaximum bubble_max_width
                                                    if should_animate:
                                                        at message_appear(anim_direction)
                                                    text message_text:
                                                        color text_colour
                                                        size phone_config["message_font_size"]
                                                        layout "tex"

                                                if is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width
                                            $ last_sender_in_chat_view = sender

                                        # timestamp kind = 1
                                        elif message_kind == 1:
                                            null height 15
                                            hbox:
                                                xalign 0.5
                                                xmaximum bubble_max_width
                                                text message_text:
                                                    color "#AAAAAA"
                                                    size phone_config["timestamp_font_size"]
                                            null height 15
                                            $ last_sender_in_chat_view = None

                                        # photo kind = 2
                                        elif message_kind == 2:
                                            hbox:
                                                spacing 12
                                                xalign (1.0 - msg_align if is_player_message else msg_align)
                                                if is_player_message:
                                                    xanchor 1.0
                                                else:
                                                    xanchor 0.0

                                                if not is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width

                                                frame:
                                                    background Frame(msg_frame, 23, 23)
                                                    padding (10, 10)
                                                    xmaximum bubble_max_width

                                                    if should_animate:
                                                        at message_appear(anim_direction)

                                                    add Image(message_text) at scale_to_fit(image_x, image_y)

                                                if is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width
                                            $ last_sender_in_chat_view = sender

                                        # texte avec emojis kind = 3
                                        elif message_kind == 3:
                                            hbox:
                                                spacing 12
                                                xalign (1.0 - msg_align if is_player_message else msg_align)
                                                if is_player_message:
                                                    xanchor 1.0
                                                else:
                                                    xanchor 0.0

                                                if not is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width

                                                frame:
                                                    background Frame(msg_frame, 23, 23)
                                                    padding (15, 10)
                                                    xmaximum bubble_max_width

                                                    if should_animate:
                                                        at message_appear(anim_direction)

                                                    text message_text:
                                                        color text_colour
                                                        size phone_config["message_font_size"]
                                                        layout "tex"

                                                if is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width
                                            $ last_sender_in_chat_view = sender

                                        # message supprimable kind = 4
                                        elif message_kind == 4:
                                            $ state = _get_deleted_state(current_app, current_global_id)
                                            $ duration = phone_config.get("deleted_message_duration", 3)
                                            if state["visible"] and state["revealed_at"] is None:
                                                $ state["revealed_at"] = renpy.get_game_runtime()
                                            $ elapsed = renpy.get_game_runtime() - state["revealed_at"] if state["revealed_at"] is not None else 0
                                            if state["visible"] and state["revealed_at"] is not None and elapsed >= duration:
                                                $ hide_deleted_message(current_app, current_global_id)
                                            elif state["visible"] and state["revealed_at"] is not None:
                                                $ remaining = max(0.0, duration - elapsed)
                                                if remaining > 0:
                                                    timer remaining action Function(hide_deleted_message, current_app, current_global_id)

                                            $ display_text = message_text if state["visible"] else "Message supprimé."

                                            hbox:
                                                spacing 12
                                                xalign (1.0 - msg_align if is_player_message else msg_align)
                                                if is_player_message:
                                                    xanchor 1.0
                                                else:
                                                    xanchor 0.0

                                                if not is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width

                                                if state["visible"]:
                                                    frame:
                                                        background Frame(msg_frame, 23, 23)
                                                        padding (15, 10)
                                                        xmaximum bubble_max_width

                                                        if should_animate:
                                                            at message_appear(anim_direction)

                                                        text display_text:
                                                            color text_colour
                                                            size phone_config["message_font_size"]
                                                            layout "tex"
                                                else:
                                                    button:
                                                        background None
                                                        hover_background None
                                                        action Function(toggle_deleted_message, current_app, current_global_id)
                                                        frame:
                                                            background Frame(msg_frame, 23, 23)
                                                            padding (15, 10)
                                                            xmaximum bubble_max_width
                                                            text display_text:
                                                                color text_colour
                                                                size phone_config["message_font_size"]
                                                                layout "tex"

                                                if is_player_message:
                                                    if display_avatar and header_icon:
                                                        add header_icon:
                                                            xysize avatar_display_size
                                                            yalign 1.0
                                                    else:
                                                        null width avatar_slot_width
                                            $ last_sender_in_chat_view = sender

                                else:
                                    $ empty_color = "#222222" if not dark_mode else "#DDDDDD"

                                    text "Aucun message dans cette conversation.":
                                        size 22
                                        color empty_color


                                # if there's a choice
                                if phone_choice_options and phone_choice_channel == current_app:
                                    null height 20
                                    vbox:
                                        xalign 0.5
                                        spacing 8
                                        if not phone_choice_armed:
                                            timer 0.15 action SetVariable("phone_choice_armed", True)

                                        for i, (preview_text, actual_message, action) in enumerate(phone_choice_options):
                                            $ message_to_send = actual_message if actual_message is not None else preview_text
                                            textbutton preview_text: #at choice_appear(delay = i * 0.1):
                                                action [
                                                    SetVariable("phone_choice_armed", False),
                                                    SetVariable("phone_choice_options", []),
                                                    SetVariable("phone_choice_channel", None),
                                                    SetVariable("disable_phone_menu_switch", False),
                                                    Function(send_phone_message, sender=phone_config["phone_player_name"], message_text=message_to_send, channel_name=current_app, do_pause=False),
                                                    If(action is not None, action),
                                                    Return()
                                                ]
                                                sensitive phone_choice_armed
                                                background Frame("gui/send_frame.png", 23, 23)
                                                text_color "#FFFFFF"
                                                text_size phone_config["choice_font_size"]
                                                text_align 0.5
                                                xalign 0.5
                                                padding (15, 10)

                                # add a bit of extra padding to the bottom of the viewport
                                null height 30


#---------------------------- Gallery ----------------------------------------

default gallery_all = ["cg_1", "cg_2", "cg_3", "cg_4", "cg_5", "cg_6"]
default gallery_unlocked = []   # on ajoute les IDs quand on les débloque

# débloquer une image dans l'histoire :
#   $ gallery_unlocked.append("cg1")

screen app_gallery():
    modal True

    vbox:
        xfill True
        yfill True

        use app_header("Galerie", "gallery")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (30, 30)

            if not gallery_all:
                text "Aucune image disponible." size 26

            else:
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    xfill True
                    yfill True

                    $ cols = 3
                    $ rows = (len(gallery_all) + cols - 1) // cols
                    $ thumb_size = (180, 320)

                    grid cols rows:
                        spacing 20

                        for img_id in gallery_all:

                            if img_id in gallery_unlocked:
                                button:
                                    xysize thumb_size
                                    action Show("gallery_viewer", img_id=img_id)
                                    add Transform("gallery/%s.png" % img_id, xysize=thumb_size, fit=True):
                                        align (0.5, 0.5)
                            else:
                                button:
                                    xysize thumb_size
                                    action NullAction()
                                    add Transform("gui/gallery_lock.png", xysize=thumb_size, fit=True):
                                        align (0.5, 0.5)

screen gallery_viewer(img_id):

    modal True
    zorder 200

    key "dismiss" action Hide("gallery_viewer")

    frame:
        xfill True
        yfill True
        background "#000000"

        button:
            xfill True
            yfill True
            background None
            hover_background None
            action Hide("gallery_viewer")

            add Transform("gallery/%s.png" % img_id, xysize=(config.screen_width, config.screen_height), fit=True):
                align (0.5, 0.5)

#---------------------------- Saves ----------------------------------------

screen app_saves():
    modal True

    vbox:
        xfill True
        yfill True

        use app_header("Sauvegardes", "saves")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (30, 30)

            viewport:
                draggable True
                mousewheel True
                scrollbars "vertical"
                xfill True
                yfill True

                grid 2 6:
                    spacing 20
                    transpose True

                    use phone_save_slot(PHONE_AUTOSAVE_SLOT_ID, "Autosave", page="auto", allow_save=False)

                    for i in range(1, 11):
                        use phone_save_slot(i, "Sauvegarde [i]")

screen phone_save_slot(slot_id, title, page=None, allow_save=True):

    $ thumb_w, thumb_h = (config.thumbnail_width, config.thumbnail_height)
    $ exists = FileLoadable(slot_id, page=page)
    $ timestamp = FileTime(slot_id, format="%d/%m %H:%M", page=page) if exists else None

    frame:
        style "phone_save_slot_frame"
        xfill True

        vbox:
            spacing 10

            hbox:
                spacing 10
                xfill True
                text title:
                    style "phone_save_slot_title"
                text ("• " + ("Occupé" if exists else "Libre")):
                    style "phone_save_slot_status"
                    color ("#6AE388" if exists else "#BBBBBB")

            if exists:
                add FileScreenshot(slot_id, page=page) xysize (thumb_w, thumb_h) fit True
            else:
                frame:
                    xysize (thumb_w, thumb_h)
                    background "#FFFFFF10"
                    xalign 0.5
                    yalign 0.5
                    text "Aperçu" style "phone_save_slot_hint"

            if timestamp:
                text "Dernière sauvegarde : [timestamp]" style "phone_save_slot_time"
            else:
                text "Aucune sauvegarde dans cet emplacement" style "phone_save_slot_hint"

            hbox:
                spacing 12
                if allow_save:
                    textbutton "Sauver":
                        style "phone_save_slot_button"
                        action FileSave(slot_id, page=page)

                textbutton "Charger":
                    style "phone_save_slot_button"
                    action FileLoad(slot_id, page=page)
                    sensitive exists

style phone_save_slot_frame is frame:
    background "#FFFFFF0F"
    padding (16, 16)

style phone_save_slot_title is default:
    size 30
    color "#FFFFFF"
    font phone_font()

style phone_save_slot_status is default:
    size 22
    font phone_font()

style phone_save_slot_hint is default:
    size 22
    color "#BFBFBF"
    font phone_font()

style phone_save_slot_time is default:
    size 22
    color "#FFFFFF"
    font phone_font()

style phone_save_slot_button is phone_text_button:
    padding (16, 12)

#---------------------------- Cloud & Social Stubs ----------------------------------------

screen app_cloud():
    modal True

    vbox:
        xfill True
        yfill True

        use app_header("Cloud", "app_cloud")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (30, 30)

            vbox:
                spacing 20

                text "Cloud Workspace":
                    style "phone_channel_name_style"

                $ filter_label = ", ".join(app_cloud_state.get("filters", [])) or "None"
                text "Filters actifs : [filter_label]":
                    color ("#202020" if not dark_mode else "#f2f2f2")

                frame:
                    background "#FFFFFF10"
                    xfill True
                    ysize 420
                    padding (20, 20)

                    vbox:
                        spacing 8
                        xfill True
                        xalign 0.5
                        yalign 0.5

                        text "Espace de flux cloud en attente de contenu.":
                            color ("#202020" if not dark_mode else "#f2f2f2")
                        text "Éléments synchronisés : [len(app_cloud_state['feed_items'])]":
                            color ("#202020" if not dark_mode else "#f2f2f2")
                        # TODO: brancher le flux cloud réel lorsque les données seront injectées.

screen app_social_soft():
    modal True

    vbox:
        xfill True
        yfill True

        use app_header("Social (Soft)", "app_social_soft")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (30, 30)

            vbox:
                spacing 20

                text "Social - Soft":
                    style "phone_channel_name_style"

                text "Sujets actifs : [app_social_soft_state['active_topic'] if app_social_soft_state['active_topic'] else 'Aucun']":
                    color ("#202020" if not dark_mode else "#f2f2f2")

                frame:
                    background "#FFFFFF10"
                    xfill True
                    ysize 420
                    padding (20, 20)

                    vbox:
                        spacing 8
                        xfill True
                        xalign 0.5
                        yalign 0.5

                        text "Grille sociale (soft) en préparation.":
                            color ("#202020" if not dark_mode else "#f2f2f2")
                        text "Cartes en attente : [len(app_social_soft_state['grid_items'])]":
                            color ("#202020" if not dark_mode else "#f2f2f2")
                        # TODO: ajouter le rendu des cartes sociales lorsque les données seront disponibles.

screen app_social_hard():
    modal True

    vbox:
        xfill True
        yfill True

        use app_header("Social (Hard)", "app_social_hard")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (30, 30)

            vbox:
                spacing 20

                text "Social - Hard":
                    style "phone_channel_name_style"

                text "Filtre courant : [app_social_hard_state['active_topic'] if app_social_hard_state['active_topic'] else 'Aucun']":
                    color ("#202020" if not dark_mode else "#f2f2f2")

                frame:
                    background "#FFFFFF10"
                    xfill True
                    ysize 420
                    padding (20, 20)

                    vbox:
                        spacing 8
                        xfill True
                        xalign 0.5
                        yalign 0.5

                        text "Section de flux avancé en attente de contenu.":
                            color ("#202020" if not dark_mode else "#f2f2f2")
                        text "Éléments en file d'attente : [len(app_social_hard_state['grid_items'])]":
                            color ("#202020" if not dark_mode else "#f2f2f2")
                        # TODO: connecter les données du flux social avancé et le rendu du grid.

#---------------------------- Settings ----------------------------------------

screen app_settings():
    modal True

    vbox:
        xfill True
        yfill True

        use app_header("Réglages", "settings")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (30, 40)

            $ text_color = "#202020" if not dark_mode else "#f2f2f2"
            $ selected_text_color = "#4A90E2" if not dark_mode else "#8AB4FF"
            $ selected_bg_color   = "#dceeff" if not dark_mode else "#1e3a5c"

            # --- LIGNE DU HAUT : Display / Skip / Dark Mode ---

            hbox:
                box_wrap True

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("Display")
                        textbutton _("Window") action Preference("display", "window"):
                            text_color text_color
                            text_selected_color selected_text_color
                            background None
                            selected_background selected_bg_color
                        textbutton _("Fullscreen") action Preference("display", "fullscreen"):
                            text_color text_color
                            text_selected_color selected_text_color
                            background None
                            selected_background selected_bg_color

                vbox:
                    style_prefix "check"
                    label _("Skip")
                    textbutton _("Unseen Text") action Preference("skip", "toggle"):
                        text_color text_color
                        text_selected_color selected_text_color
                        background None
                        selected_background selected_bg_color
                    textbutton _("After Choices") action Preference("after choices", "toggle"):
                        text_color text_color
                        text_selected_color selected_text_color
                        background None
                        selected_background selected_bg_color
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle")):
                        text_color text_color
                        text_selected_color selected_text_color
                        background None
                        selected_background selected_bg_color

                vbox:
                    style_prefix "check"
                    label _("Dark Mode")
                    textbutton _("Dark Mode"):
                        action ToggleVariable("dark_mode", True, False)
                        selected dark_mode
                        text_color text_color
                        text_selected_color selected_text_color
                        background None
                        selected_background selected_bg_color

                # --- GAMEPLAY & SONS ---

                vbox:
                    style_prefix "check"

                    label _("Gameplay")
                    textbutton _("Auto-advance chat messages"):
                        action Function(toggle_phone_chat_auto_advance)
                        selected phone_chat_auto_advance
                        text_color text_color
                        text_selected_color selected_text_color
                        background None
                        selected_background selected_bg_color

                    textbutton _("Skip"):
                        action Function(toggle_phone_chat_skip_enabled)
                        selected phone_chat_skip_enabled
                        text_color text_color
                        text_selected_color selected_text_color
                        background None
                        selected_background selected_bg_color

                    text _("Messages revealed per interaction: [phone_chat_skip_batch_size]") color text_color

                    hbox:
                        spacing 15
                        bar value VariableValue(
                            "phone_chat_skip_batch_size",
                            PHONE_CHAT_SKIP_BATCH_MAX - PHONE_CHAT_SKIP_BATCH_MIN,
                            offset=PHONE_CHAT_SKIP_BATCH_MIN,
                            step=1,
                        ) changed Function(set_phone_chat_skip_batch_size)
                        text "[phone_chat_skip_batch_size]" color text_color

                    text _("Auto chat delay (seconds): [phone_chat_auto_delay:.1f]") color text_color

                    hbox:
                        spacing 15
                        bar value VariableValue(
                            "phone_chat_auto_delay",
                            PHONE_CHAT_AUTO_DELAY_MAX - PHONE_CHAT_AUTO_DELAY_MIN,
                            offset=PHONE_CHAT_AUTO_DELAY_MIN,
                            step=PHONE_CHAT_AUTO_DELAY_STEP,
                        ) changed Function(set_phone_chat_auto_delay)
                        text "{:.1f}s".format(phone_chat_auto_delay) color text_color

                    null height 30

                    if config.has_music or config.has_sound or config.has_voice:
                        label _("Sounds")
                        spacing 15

                    if config.has_music:
                        text "Music Volume" color text_color

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        text "Sound Volume" color text_color

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        text "Voice Volume" color text_color

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("Mute All"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"

                # --- ANCIEN RÉGLAGES (MENU PREFS CLASSIQUE) ---

                null height 500

                vbox:
                    spacing 50
                    textbutton ("ancien réglages"):
                        action ShowMenu("preferences")
