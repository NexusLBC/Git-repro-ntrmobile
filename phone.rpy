# Phone main interface

default current_background = Image("gui/root_screen.png")
default dark_mode = False
default current_app = "home"
default phone_nav_stack = []
default lock_done = False
default phone_intro_done = False
default phone_mode = False
default phone_choice_armed = False
default phone_chat_auto_advance = False
default phone_chat_auto_delay = 0.8
default phone_last_revealed_sender = {}
default phone_animated_global_ids = {}
default eta_bar_hidden = False
default phone_navbar_hidden = False
default phone_deleted_messages = {}
define eta_bar_height = 70
define deleted_message_placeholder = _("Message supprimé")
define deleted_message_rehide_delay = 4.0


init python:
    import os
    import re

    def phone_try_autosave():
        try:
            renpy.force_autosave()
        except Exception as e:
            renpy.log("Autosave skipped: %r" % e)

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

    # Mapping of app identifiers to their corresponding screens.
    phone_screen_routes = {
        "messenger": "app_messenger",
        "gallery": "app_gallery",
        "saves": "app_saves",
        "settings": "app_settings",
    }

    #------------------------ Style, Couleurs --------------------------------

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
        "preview_no_message": "Empty chat...",
        "channels_title": "Messages",
        "history_timestamp_prefix": "Time:",
        "phone_player_name": "Me",
        "group_added": "{adder} added {participant} to the group.",
        "group_joined": "{participant} joined the group.",
        "group_left": "{participant} left the group.",
        # UI Configurations
        "message_font_size": 30,
        "choice_font_size": 24,
        "timestamp_font_size": 20,
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
        global phone_animated_global_ids
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
            phone_animated_global_ids[channel_id] = []

    # add messages to a channel in the phone (kind 0 = normal message, kind 1 = timestamp, kind 2 = photo, kind 3 = has emojis, kind 4 = deleted message)
        # add messages to a channel in the phone
    # kind 0 = normal message, 1 = timestamp, 2 = photo, 3 = texte avec emojis, 4 = deleted/revealed message
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
        original_deleted_text = message_text

        if message_kind == 4:
            register_deleted_message(channel_name, msg_id, original_deleted_text)
            message_text = store.deleted_message_placeholder
            summary_alt = store.deleted_message_placeholder

        # Quand on révèle un message, on force le refresh UI
        renpy.restart_interaction()

        channel_latest_global_id[channel_name] = max(
            channel_latest_global_id.get(channel_name, 0), current_global_id
        )

        channel_last_message_id[channel_name] = max(
            channel_last_message_id.get(channel_name, 0), msg_id
        )

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

        if message_kind == 2:
            image_id = os.path.splitext(os.path.basename(message_text))[0]
            if image_id and image_id not in gallery_unlocked:
                gallery_unlocked.append(image_id)

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
            narrator.add_history(
                kind="adv",
                who=sender,
                what=store.deleted_message_placeholder,
            )

        renpy.checkpoint()

        phone_try_autosave()

        # Pause éventuelle après le message
        if do_pause and phone_config["pause"]["do_pause"]:
            if phone_config["pause"]["pause_time"]:
                renpy.pause(phone_config["pause"]["pause_length"])
            else:
                renpy.pause()

    def phone_reveal_next(channel_name):
        if channel_name not in store.phone_pending:
            return
        if not store.phone_pending[channel_name]:
            return

        msg = store.phone_pending[channel_name].pop(0)
        _deliver_phone_message(msg, channel_name)

        _, sender, _, message_kind, *_ = msg

        if message_kind != 1:
            store.phone_last_revealed_sender[channel_name] = sender


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
            and next_sender == store.phone_last_revealed_sender.get(channel_name, None)
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
        phone_animated_global_ids = {}
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
            last_message_tuple = None
            if channel_notifs.get(channel_name, False):
                for candidate in reversed(phone_channels[channel_name]):
                    if candidate[3] != 1 and candidate[1] != phone_config["phone_player_name"]:
                        last_message_tuple = candidate
                        break
            if last_message_tuple is None:
                for candidate in reversed(phone_channels[channel_name]):
                    if candidate[3] != 1:
                        last_message_tuple = candidate
                        break
            if last_message_tuple:
                summary_alt = None
                if len(last_message_tuple) > 5:
                    summary_alt = last_message_tuple[5]
                if summary_alt and summary_alt != "none":
                    return summary_alt
                sender = last_message_tuple[1]
                message_text = last_message_tuple[2]
                message_kind = last_message_tuple[3]
                preview_text = message_text
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

    def register_deleted_message(channel_name, msg_id, original_text):
        store.phone_deleted_messages[(channel_name, msg_id)] = {
            "original": original_text,
            "revealed": False,
        }

    def _update_deleted_message_text(channel_name, msg_id, new_text):
        if channel_name not in store.phone_channels:
            return

        for index, data in enumerate(store.phone_channels[channel_name]):
            if data[0] == msg_id:
                updated = list(data)
                updated[2] = new_text
                updated[5] = new_text
                store.phone_channels[channel_name][index] = tuple(updated)
                break

        renpy.restart_interaction()

    def reveal_deleted_message(channel_name, msg_id):
        state = store.phone_deleted_messages.get((channel_name, msg_id))

        if not state:
            return

        state["revealed"] = True
        _update_deleted_message_text(channel_name, msg_id, state["original"])

    def hide_deleted_message(channel_name, msg_id):
        state = store.phone_deleted_messages.get((channel_name, msg_id))

        if not state:
            return

        state["revealed"] = False
        _update_deleted_message_text(channel_name, msg_id, store.deleted_message_placeholder)

    def toggle_deleted_message(channel_name, msg_id):
        state = store.phone_deleted_messages.get((channel_name, msg_id))

        if not state:
            return

        if state.get("revealed", False):
            hide_deleted_message(channel_name, msg_id)
        else:
            reveal_deleted_message(channel_name, msg_id)

# ---------- Styles du système de messagerie (sans thèmes) ----------

style phone_header_style is default:
    size 40
    xalign 0.5
    font "gui/HelveticaNeueLTStd-Bd.otf"

style phone_channel_button_style is button:
    background None
    hover_background "#ffffff20"
    xpadding 10
    ypadding 8

style phone_channel_name_style is default:
    size 34
    bold True
    font "gui/HelveticaNeueLTStd-Bd.otf"

style phone_channel_preview_style is default:
    size 22

style phone_message_style is default:
    size 24
    xalign 0.0

style phone_sender_name_style is default:
    size 18
    yoffset 2
    ypadding 0
    yalign 1.0
    font "gui/HelveticaNeueLTStd-Bd.otf"

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

style phone_navbar_frame is empty:
    background None
    padding (0, 0)

style phone_content_frame is empty:
    background None
    padding (0, 0)

style eta_bar_frame is empty:
    background None
    padding (12, 24)

screen app_header(title, app_id, icon_path=None):

    frame:
        xfill True
        ysize 150
        background app_color(app_id)

        $ header_title = phone_app_title(title, app_id)
        $ can_go_back = current_app != "home"
        $ header_color = get_sender_name_color(dark_mode)

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
                    style "phone_header_style"
                    xalign 0.5
                    color header_color

screen phone_navbar():

    if phone_navbar_hidden:
        null height 0
    else:

        zorder 100

        frame:
            style "phone_navbar_frame"
            align (0.5, 1.0)
            xfill True
            ysize 120
            padding (0, 20)

            $ nav_bg = get_nav_background(current_app)
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
                    action Function(phone_back)
                    sensitive not disable_phone_menu_switch

                # Bouton "Home" (menu principal du téléphone)
                imagebutton:
                    idle "gui/menu.png"
                    hover "gui/menu.png"
                    xalign 0.5
                    yalign 0.5
                    action Function(phone_home)

                # Bouton "Autre" (pour plus tard)
                imagebutton:
                    idle "gui/other.png"
                    hover "gui/other.png"
                    xalign 0.5
                    yalign 0.5
                    action NullAction()

screen eta_bar(show_time=True):
    zorder 150

    if eta_bar_hidden:
        null height 0
    else:
        $ eta_bar_background = get_eta_bar_background(dark_mode)
        $ eta_bar_text_color = "#FFFFFF"
        $ eta_bar_time = format_phone_time()

        frame:
            style "eta_bar_frame"
            background Solid(eta_bar_background)
            xfill True
            ysize eta_bar_height

            hbox:
                xfill True
                yfill True
                yalign 0.5
                spacing 16

                if show_time:
                    text eta_bar_time:
                        xalign 0.0
                        yalign 0.5
                        size 36
                        color eta_bar_text_color

                null width 0 xfill True

                hbox:
                    spacing 20
                    yalign 0.5
                    add "gui/connection.png":
                        yalign 0.5
                        at scale_to_fit(42, 42)
                    add "gui/battery.png":
                        yalign 0.5
                        at scale_to_fit(42, 42)

# ------------------------- Main Menu ------------------------------------------

label Phone:
    call screen Phonescreen
    return

screen Phonescreen():

    if lock_done and not phone_intro_done:
        python:
            initialize_phone_intro()

    use eta_bar

    if current_app =="home":

        add current_background

        vbox:
            xfill True
            yfill True
            spacing 0

            null height eta_bar_height

            grid 4 5:
                xalign 0.5
                yalign 0.5
                spacing 70

                for i in range(20):

                    if i < len(app_buttons):
                        $ app = app_buttons[i]
                        $ idle_path = app["image"] % "idle"

                        if renpy.loadable(idle_path):
                            imagebutton:
                                auto app["image"]
                                action app["action"]
                                focus_mask True
                        else:
                            button:
                                xysize (180, 180)
                                action NullAction()
                                background None

                    else:
                        null

    elif current_app == "messenger" or current_app in phone_channels:
        use app_messenger

    elif current_app in phone_screen_routes:
        use expression phone_screen_routes[current_app]

    use phone_navbar

#---------------------------- Messenger ----------------------------------------

screen app_messenger(auto_timer_enabled=phone_chat_auto_advance):
    modal True

    if current_app != "messenger":
        key "mouseup_1" action Function(phone_reveal_next, current_app)
        key "dismiss" action Function(phone_reveal_next, current_app)

    frame:
        style "phone_content_frame"
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

            null height eta_bar_height

            # Header adaptatif
            $ messenger_header_title = "Messenger"
            if current_app in phone_channels:
                $ messenger_header_title = phone_channel_data[current_app]["display_name"]
            use app_header(messenger_header_title, "messenger")

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
                        scrollbars None

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
                                    padding (18, 14)

                                    # --- DESCRIPTIONS DES CONVERSATIONS ---
                                    vbox:
                                        # icon, name, chat last message, and notification
                                        hbox:
                                            #  icon
                                            spacing 14
                                            add phone_channel_data[channel_name]["icon"]:
                                                xysize (64, 64)
                                                yalign 0.5
                                            # name and preview message
                                            vbox:
                                                $ name_color = get_sender_name_color(dark_mode)
                                                $ preview_color = get_channel_preview_color(dark_mode)

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
                        scrollbars None
                        mousewheel True
                        draggable True

                        # do this once when it opens
                        if phone_config["auto_scroll"]:
                            $ yadj.value = (yadj.range + 1000)


                        fixed:
                            xfill True
                            yfill True

                            # AUTO MODE : révèle automatiquement les messages en attente
                            if auto_timer_enabled and phone_should_auto_advance(current_app):
                                timer phone_chat_auto_delay action Function(phone_reveal_next, current_app)

                            vbox:
                                spacing 8
                                xfill True

                                if current_app in phone_channels:

                                    $ latest_channel_id = channel_last_message_id.get(current_app, 0)
                                    $ last_sender_in_chat_view = None
                                    $ mc_avatar_path = get_mc_avatar_path()
                                    $ bubble_width_limit = bubble_max_width()

                                    # display all messages
                                    for message_data in phone_channels[current_app]:
                                        $ msg_id, sender, message_text, message_kind, current_global_id, summary_alt, image_x, image_y = message_data

                                        if current_app not in phone_animated_global_ids:
                                            $ phone_animated_global_ids[current_app] = []

                                        $ should_animate = False
                                        if message_kind in (0, 2, 3, 4) and current_global_id not in phone_animated_global_ids[current_app]:
                                            $ should_animate = True
                                            $ phone_animated_global_ids[current_app].append(current_global_id)

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
                                        if is_player_message:
                                            $ header_icon = mc_avatar_path
                                            $ header_align = 1.0 - msg_align
                                        else:
                                            $ header_icon = phone_channel_data[current_app]["icon"]
                                            $ header_align = msg_align
                                        $ name_colour = get_sender_name_color(dark_mode)

                                        if message_kind in (0, 2, 3, 4) and sender != last_sender_in_chat_view:
                                            hbox:
                                                xalign header_align
                                                if is_player_message:
                                                    xanchor 1.0
                                                else:
                                                    xanchor 0.0
                                                spacing 10
                                                if not is_player_message and header_icon:
                                                    add header_icon:
                                                        xysize (56, 56)
                                                        yalign 0.5
                                                text sender:
                                                    style "phone_sender_name_style"
                                                    color name_colour
                                                    yalign 0.5
                                                if is_player_message and header_icon:
                                                    add header_icon:
                                                        xysize (56, 56)
                                                        yalign 0.5

    #                                    # displaying the sender's name for group chats
    #                                    $ is_group_chat = phone_channel_data[current_app]["is_group"]
    #                                    if is_group_chat and sender != phone_config["phone_player_name"] and sender != last_sender_in_chat_view:
    #                                        text sender:
    #                                            style "phone_sender_name_style"
    #                                            xalign msg_align
    #                                            xoffset 5

                                        # normal message : kind = 0
                                        if message_kind == 0:
                                            frame:
                                                if is_player_message:
                                                    xpos 1.0 - msg_align xanchor 1.0
                                                else:
                                                    xpos msg_align xanchor 0.0
                                                background Frame(msg_frame, 23, 23)
                                                padding (15, 10)
                                                xmaximum bubble_width_limit
                                                if should_animate:
                                                    at message_appear(anim_direction)
                                                text message_text:
                                                    color text_colour
                                                    size phone_config["message_font_size"]
                                                    layout "tex"
                                            $ last_sender_in_chat_view = sender

                                        # timestamp kind = 1
                                        elif message_kind == 1:
                                            null height 15
                                            hbox:
                                                xalign 0.5
                                                xmaximum 360
                                                text message_text:
                                                    color "#AAAAAA"
                                                    size phone_config["timestamp_font_size"]
                                            null height 15
                                            $ last_sender_in_chat_view = None

                                        # photo kind = 2
                                        elif message_kind == 2:
                                            frame:
                                                if is_player_message:
                                                    xpos 1.0 - msg_align xanchor 1.0
                                                else:
                                                    xpos msg_align xanchor 0.0
                                                background Frame(msg_frame, 23, 23)
                                                padding (10, 10)
                                                xmaximum bubble_width_limit

                                                if should_animate:
                                                    at message_appear(anim_direction)

                                                button:
                                                    xfill True
                                                    yfill True
                                                    background None
                                                    hover_background None
                                                    action ToggleScreen("chat_image_viewer", image_path=message_text)
                                                    add Image(message_text) at scale_to_fit(image_x, image_y)
                                            $ last_sender_in_chat_view = sender

                                        # texte avec emojis kind = 3
                                        elif message_kind == 3:
                                            frame:
                                                if is_player_message:
                                                    xpos 1.0 - msg_align xanchor 1.0
                                                else:
                                                    xpos msg_align xanchor 0.0
                                                background Frame(msg_frame, 23, 23)
                                                padding (15, 10)
                                                xmaximum bubble_width_limit

                                                if should_animate:
                                                    at message_appear(anim_direction)

                                                text message_text:
                                                    color text_colour
                                                    size phone_config["message_font_size"]
                                                    layout "tex"
                                            $ last_sender_in_chat_view = sender

                                        elif message_kind == 4:
                                            $ deleted_state = phone_deleted_messages.get((current_app, msg_id), {"revealed": False, "original": message_text})
                                            $ deleted_font = "gui/HelveticaNeueLTStd-It.otf" if message_text == store.deleted_message_placeholder else "gui/HelveticaNeueLTStd-Lt.otf"
                                            button:
                                                if is_player_message:
                                                    xpos 1.0 - msg_align xanchor 1.0
                                                else:
                                                    xpos msg_align xanchor 0.0
                                                background Frame(msg_frame, 23, 23)
                                                padding (15, 10)
                                                xmaximum bubble_width_limit
                                                if should_animate:
                                                    at message_appear(anim_direction)
                                                action Function(toggle_deleted_message, current_app, msg_id)
                                                text message_text:
                                                    color text_colour
                                                    size phone_config["message_font_size"]
                                                    font deleted_font
                                                    layout "tex"
                                            if deleted_state.get("revealed", False):
                                                timer deleted_message_rehide_delay action Function(hide_deleted_message, current_app, msg_id)
                                            $ last_sender_in_chat_view = sender

                                else:
                                    $ empty_color = get_empty_state_color(dark_mode)

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
                                            $ message_to_send = preview_text
                                            if actual_message is not None:
                                                $ message_to_send = actual_message
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

        null height eta_bar_height

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
                    $ thumb_width = 200
                    $ thumb_height = int(thumb_width * 16 / 9)

                    grid cols rows:
                        spacing 20

                        for img_id in gallery_all:

                            if img_id in gallery_unlocked:
                                button:
                                    xsize thumb_width
                                    ysize thumb_height
                                    action Show("gallery_viewer", img_id=img_id)
                                    add Image("images/cg/%s.png" % img_id) at scale_to_fit(thumb_width, thumb_height)
                            else:
                                button:
                                    xsize thumb_width
                                    ysize thumb_height
                                    action NullAction()
                                    add Image("gui/gallery_lock.png") at scale_to_fit(thumb_width, thumb_height)

screen gallery_viewer(img_id):
    modal True
    zorder 300

    on "show" action [SetVariable("eta_bar_hidden", True), SetVariable("phone_navbar_hidden", True)]
    on "hide" action [SetVariable("eta_bar_hidden", False), SetVariable("phone_navbar_hidden", False)]

    $ viewer_image_path = "images/cg/%s.png" % img_id
    $ viewer_displayable = viewer_image_path
    if not renpy.loadable(viewer_image_path):
        $ viewer_displayable = Solid("#111111")

    $ viewer_width = config.screen_width
    $ viewer_height = config.screen_height

    add Solid("#000000e6")

    button:
        xfill True
        yfill True
        background None
        action Hide("gallery_viewer")
        add viewer_displayable at scale_to_fit(viewer_width, viewer_height)

screen chat_image_viewer(image_path):
    modal True
    zorder 300

    on "show" action [SetVariable("eta_bar_hidden", True), SetVariable("phone_navbar_hidden", True)]
    on "hide" action [SetVariable("eta_bar_hidden", False), SetVariable("phone_navbar_hidden", False)]

    $ viewer_displayable = image_path
    if not renpy.loadable(image_path):
        $ viewer_displayable = Solid("#111111")

    $ viewer_width = config.screen_width
    $ viewer_height = config.screen_height

    add Solid("#000000e6")

    button:
        xfill True
        yfill True
        background None
        action Hide("chat_image_viewer")
        add viewer_displayable at scale_to_fit(viewer_width, viewer_height)

#---------------------------- Saves ----------------------------------------

screen app_saves():
    modal True
    $ FilePageName("phone")

    vbox:
        xfill True
        yfill True

        null height eta_bar_height

        use app_header("Sauvegardes", "saves")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (40, 40)

            vbox:
                spacing 15

                for i in range(1, 11):  # 10 slots
                    hbox:
                        spacing 20
                        xfill True

                        $ exists = FileLoadable(i)

                        if exists:
                            text FileTime(i, format="%d/%m %H:%M") size 22
                        else:
                            text "Emplacement [i] vide" size 22

                        null width 40

                        textbutton "Sauver ici":
                            action FileSave(i)

                        if exists:
                            textbutton "Charger":
                                action FileLoad(i)

#---------------------------- Settings ----------------------------------------

screen app_settings():
    modal True

    vbox:
        xfill True
        yfill True

        null height eta_bar_height

        use app_header("Réglages", "settings")

        frame:
            background app_body_bg()
            xfill True
            yfill True
            padding (30, 40)

            $ text_color = get_text_color(dark_mode)
            $ selected_text_color = get_selected_text_color(dark_mode)
            $ selected_bg_color   = get_selected_bg(dark_mode)

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
                    textbutton _("Start Skip Now"):
                        action Skip(fast=True, confirm=True)
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

                vbox:
                    style_prefix "check"
                    label _("Messenger")
                    textbutton _("Auto-advance chat messages"):
                        action ToggleVariable("phone_chat_auto_advance", True, False)
                        selected phone_chat_auto_advance
                        text_color text_color
                        text_selected_color selected_text_color
                        background None
                        selected_background selected_bg_color


                null height 60

                # --- SONS ---

                null height 60

                vbox:

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

                null height 120

                vbox:
                    spacing 50
                    textbutton ("ancien réglages"):
                        action ShowMenu("preferences")
