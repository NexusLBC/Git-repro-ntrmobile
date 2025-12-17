label maya_scene_1:
    $ send_phone_message("Maya", "Tu veux que je t'envoie une image ?", "maya_dm")

    $ present_phone_choices(
        [
            ("Oui, envoie !", "Oui, envoie !", Call("maya_envoie_image")),
            ("Pas maintenant", "Pas maintenant, je suis occupé.", Call("maya_refuse_image")),
        ],
        "maya_dm"
    )
    return
