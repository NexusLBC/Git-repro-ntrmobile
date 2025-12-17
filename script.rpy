default currentCharacter = None

label start:
    $ reset_phone_data()
    $ phone_start()
    $ create_phone_channel("maya_dm", "Maya", ["Maya", phone_config["phone_player_name"]], "avatars/maya_icon.png")
    $ create_phone_channel("elias_dm", "Elias", ["Elias", phone_config["phone_player_name"]], "avatars/elias_icon.png")

    # Tu peux envoyer des messages de base si tu veux que la conv ne soit pas vide
    #$ send_phone_message("sender", "message_text", "channel_name", message_kind=0, do_pause=False)
    $ send_phone_message("Maya", "Test test", "maya_dm", do_pause=False)
    jump maya_scene_1

    # Puis ton label Phone (lockscreen -> home -> etc.)

    call Phone
    return


image emoji_sob = "phone/emoji/sob.png"
image emoji_dizzy = "phone/emoji/dizzy.png"
image emoji_eyes = "phone/emoji/eyes.png"
