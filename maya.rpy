label maya_scene_1:
    $ send_phone_message(phone_config["phone_player_name"], "Oui, je te lis.", "maya_dm", 0, do_pause=False)
    $ send_phone_message("Maya", "Super !", "maya_dm", 0, do_pause=False)
    $ send_phone_message("Maya", "Tu veux que je t'envoie une image ? <emoji_eyes>", "maya_dm", 3, do_pause=False)

    $ present_phone_choices(
        [
            ("Oui, envoie !", "Oui, envoie !", Call("maya_envoie_image")),
            ("Pas maintenant", "Pas maintenant, je suis occupé.", Call("maya_refuse_image")),
        ],
        "maya_dm"
    )
    return
