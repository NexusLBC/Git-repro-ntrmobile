default currentCharacter = None

label start:
    $ reset_phone_data()
    $ phone_start()
    $ create_phone_channel("maya_dm", "Maya", ["Maya", phone_config["phone_player_name"]], "avatars/maya_icon.png")
    $ create_phone_channel("elias_dm", "Elias", ["Elias", phone_config["phone_player_name"]], "avatars/elias_icon.png")

    $ advance_phone_time(12)
    $ send_phone_message("Maya", "Réveille-toi, bêta-testeur préféré. Regarde l'heure en grand, c'est classe non ?", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "Je veux ton avis avant que je balance mes stories. Promis, c'est plus doux que mon café.", "maya_dm", do_pause=False)
    $ send_phone_message(phone_config["phone_player_name"], "Toujours prêt. J'ai le pouce encore à moitié endormi mais motivé.", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "J'ai griffonné des idées pour ce soir. Style moderne, un peu teasing, zero drama.", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "J'ai glissé un message caché dans la pile, clique pour jouer les espions.", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "Je veux qu'on ait un moment rien qu'à deux avant que tout le monde arrive. Gardons ça pour nous.", "maya_dm", message_kind=4, do_pause=False)
    $ send_phone_message(phone_config["phone_player_name"], "Si tu caches déjà des choses, ça promet. Je clique quand ?", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "Attends, j'ajoute un sticker pour toi. 😏", "maya_dm", message_kind=3, summary_alt="😏", do_pause=False)
    $ send_phone_message("Maya", "Ok, go. Délai serré, énergie haute. Je veux qu'on roule ensemble aujourd'hui.", "maya_dm", do_pause=False)
    $ advance_phone_time(8)
    $ send_phone_message(phone_config["phone_player_name"], "Marché conclu. J'enchaîne les notifs comme un pro du multitask.", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "Parfait. J'ai ajouté deux aperçus dans la galerie pour te motiver.", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "Le premier est juste un mood-board, l'autre c'est moi qui teste un angle miroir.", "maya_dm", do_pause=False)
    $ send_phone_message(phone_config["phone_player_name"], "Je vais tout regarder. Tu sais que j'aime les répétitions générales.", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "Parlant de répétitions, je veux aussi voir comment tu replies en situation stress. Challenge accepté ?", "maya_dm", do_pause=False)
    $ advance_phone_time(5)
    $ send_phone_message(phone_config["phone_player_name"], "Toujours. Et si je galère, je spamme Elias pour un avis technique.", "maya_dm", do_pause=False)
    $ send_phone_message("Maya", "Haha, l'expert hardware. Va le ping, il adore quand tu débarques sans prévenir.", "maya_dm", do_pause=False)
    $ send_phone_message("Elias", "Yo, j'ai vu ton statut passer. Déjà en mode sprint matinal ?", "elias_dm", do_pause=False)
    $ send_phone_message(phone_config["phone_player_name"], "Yes. Maya me fait plancher. Besoin de toi si mon cerveau chauffe.", "elias_dm", do_pause=False)
    $ send_phone_message("Elias", "Respire. Hydrate-toi. Et si tout casse, blame le wifi. Classic.", "elias_dm", do_pause=False)
    $ send_phone_message(phone_config["phone_player_name"], "Deal. Je te dois un café si ça marche.", "elias_dm", do_pause=False)

    call Phone
    return


image emoji_sob = "phone/emoji/sob.png"
image emoji_dizzy = "phone/emoji/dizzy.png"
