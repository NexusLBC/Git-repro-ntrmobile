default currentCharacter = None

label start:
    $ reset_phone_data()
    $ phone_start()
    $ create_phone_channel("maya_dm", "Maya", ["Maya", phone_config["phone_player_name"]], "avatars/maya_icon.png")
    $ create_phone_channel("elias_dm", "Elias", ["Elias", phone_config["phone_player_name"]], "avatars/elias_icon.png")

    # Tu peux envoyer des messages de base si tu veux que la conv ne soit pas vide
    $ send_phone_message("Maya", "Salut, tu vois ce message ?", "maya_dm", do_pause=False)
    $ send_phone_message(phone_config["phone_player_name"], "Oui, je te lis.", "maya_dm", do_pause=False)

    # Puis ton label Phone (lockscreen -> home -> etc.)

    call Phone
    return


image emoji_sob = "phone/emoji/sob.png"
image emoji_dizzy = "phone/emoji/dizzy.png"
