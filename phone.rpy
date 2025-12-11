# Phone main interface

default current_background = Image("gui/root_screen.png")
default dark_mode = False
default current_app = "home"
default lock_done = False
default phone_mode = False

init python:
    #Liste des applis (message, save, galerie, patreon, itch, subsstar, settings)
    app_buttons = [
        { # Messenger
            "image": "gui/buttons/messenger_%s.png",
            "action": SetVariable("current_app", "messenger"),
        },
        { # Saves
            "image": "gui/buttons/save_%s.png",
            "action": SetVariable("current_app", "saves"),
        },
        { # Gallery
            "image": "gui/buttons/gallery_%s.png",
            "action": SetVariable("current_app", "gallery"),
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
            "action": SetVariable("current_app", "succes"),
        },
        { # Settings
            "image": "gui/buttons/settings_%s.png",
            "action": SetVariable("current_app", "settings"),
        },

        # Subscribestar

    ]

    def phone_back():
        if store.current_app != "home":
            store.current_app = "home"

    def phone_home():
        store.current_app = "home"

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

    import re

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
        "message_font_size": 24,
        "choice_font_size": 24,
        "timestamp_font_size": 20,
        "auto_scroll": True,
        "show_sender_in_preview": True,
        "default_icon": "phone/icon.png",
        "user_colour": "#FFFFFF",
        "character_colour": "#000000",
        "timestamp_colour": "#000000",
        "sort_channels_by_latest": True,
        "message_padding": 0.025,
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
    phone_channels = messenger_conversations  # legacy alias to keep compatibility
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

    # ------------------------- Variables 2 ------------------------------------

    # replace inline images natively
    def replace_emojis(text):
        """ Replaces custom emoji tags like <emoji_name> with Ren'Py image tags.
            This is an internal helper function to allow for easy emoji syntax in messages.
            Args:
                text (str): The message text that might contain emoji tags.
        """
        def sub(match):
            name = match.group(1)
            return "{image=%s}" % name
        return re.sub(r"<([A-Za-z0-9_]+)>", sub, text)

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
        ensure_messenger_contact(channel_id, display_name=display_name, avatar=icon_path)
        phone_channel_data[channel_id] = {
            "display_name": display_name,
            "icon": icon_path,
            "participants": participants,
            "is_group": is_group
        }
        channel_last_message_id[channel_id] = 0
        channel_notifs[channel_id] = False
        channel_seen_latest[channel_id] = True
        channel_visible[channel_id] = True
        channel_latest_global_id[channel_id] = 0

    # add messages to a channel in the phone (kind 0 = normal message, kind 1 = timestamp, kind 2 = photo, kind 3 = has emojis)
        # add messages to a channel in the phone
    # kind 0 = normal message, 1 = timestamp, 2 = photo, 3 = texte avec emojis
    def send_phone_message(sender, message_text, channel_name,
                           message_kind=0, summary_alt="none",
                           image_x=320, image_y=320, do_pause=True):
        """
        Envoie un message dans un salon de téléphone et met à jour les infos.
        """
        global _phone_global_message_counter, current_global_id

        load_messenger_from_persistent()
        ensure_messenger_contact(channel_name)

        if message_kind != 1:
            if sender == phone_config["phone_player_name"]:
                if phone_config.get("play_sound_send", False):
                    renpy.sound.play("audio/phone/send.mp3", channel="sound")
            else:
                if phone_config.get("play_sound_receive", False):
                    renpy.sound.play("audio/phone/receive.mp3", channel="sound")

        _phone_global_message_counter += 1
        current_global_id = _phone_global_message_counter
        channel_latest_global_id[channel_name] = current_global_id

        last_id = channel_last_message_id.get(channel_name, 0)
        current_id = last_id + 1
        channel_last_message_id[channel_name] = current_id

        kind_map = {0: "text", 1: "timestamp", 2: "image", 3: "text"}
        add_messenger_message(
            channel_name,
            sender,
            message_text,
            kind=kind_map.get(message_kind, "text"),
            summary_alt=summary_alt,
            image_size=(image_x, image_y),
        )

        channel_notifs[channel_name] = True
        channel_seen_latest[channel_name] = False

        renpy.restart_interaction()

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

        save_messenger_to_persistent()
        renpy.checkpoint()

        if do_pause and phone_config["pause"]["do_pause"]:
            if phone_config["pause"]["pause_time"]:
                renpy.pause(phone_config["pause"]["pause_length"])
            else:
                renpy.pause()


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

        phone_channel_data = {}
        phone_channels = {}
        channel_last_message_id = {}
        channel_notifs = {}
        channel_seen_latest = {}
        channel_visible = {}
        channel_latest_global_id = {}
        _phone_global_message_counter = 0

        # aucun salon créé ici
        #create_phone_channel("maya_dm", "Maya", ["Maya", phone_config["phone_player_name"]], "avatars/maya_icon.png")

        renpy.restart_interaction()


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
        if channel_name in messenger_conversations:
            return messenger_preview(channel_name)
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
        global current_phone_view, channel_notifs, channel_seen_latest
        current_phone_view = channel_name
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
        global phone_channel_data, phone_channels, channel_last_message_id, channel_seen_latest, channel_notifs, channel_visible, channel_latest_global_id, current_phone_view
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
        if current_phone_view == channel_name:
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
        return any(has_notif for channel, has_notif in channel_notifs.items() if channel != current_phone_view)

# ---------- Styles du système de messagerie (sans thèmes) ----------

style phone_header_style is default:
    size 28
    xalign 0.5

style phone_channel_button_style is button:
    background None
    hover_background "#ffffff20"
    xpadding 10
    ypadding 8

style phone_channel_name_style is default:
    size 22
    bold True

style phone_channel_preview_style is default:
    size 18

style phone_message_style is default:
    size 20
    xalign 0.0

style phone_sender_name_style is default:
    size 16
    yoffset 2
    ypadding 0
    yalign 1.0

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

screen app_header(title, app_id):

    frame:
        xfill True
        ysize 150
        background app_color(app_id)

        hbox:
            xfill True
            yalign 0.5
            spacing 30
            #padding (20, 20)

            if current_app == "home": # modif current app -> chat
                textbutton "◀":
                    xminimum 80
                    action SetVariable("current_app", "messenger")

                text title:
                    xalign 0.5
                    size 40
            else:
                textbutton "◀":
                    xminimum 80
                    action SetVariable("current_app", "home")

                text title:
                    xalign 0.5
                    size 40

screen phone_navbar():

    zorder 100

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
                action Function(phone_back)

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

# ------------------------- Main Menu ------------------------------------------

label Phone:
    call screen Phonescreen
    return

screen Phonescreen():

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

    elif current_app == "messenger":
        use app_messenger

    elif current_app == "gallery":
        use app_gallery

    elif current_app == "saves":
        use app_saves

    elif current_app == "settings":
        use app_settings

    use phone_navbar

#---------------------------- Messenger ----------------------------------------

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

                    grid cols rows:
                        spacing 20

                        for img_id in gallery_all:

                            if img_id in gallery_unlocked:
                                button:
                                    xsize 250
                                    ysize 140
                                    action Show("gallery_viewer", img_id=img_id)
                                    add im.Scale("gallery/%s.png" % img_id, 250, 140)
                            else:
                                button:
                                    xsize 250
                                    ysize 150
                                    action NullAction()
                                    add im.Scale("gui/gallery_lock.png", 250, 140)

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

                null height 200

                # --- TEXTE ---

                vbox:
                    label _("Text")
                    spacing 15
                    text "Text Speed" color text_color
                    bar value Preference("text speed")

                    text "Auto-Forward Time" color text_color
                    bar value Preference("auto-forward time")

                # --- SONS ---

                null height 400

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

                null height 500

                vbox:
                    spacing 50
                    textbutton ("ancien réglages"):
                        action ShowMenu("preferences")
