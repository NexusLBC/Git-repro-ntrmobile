label start_chapter_1:
    # Création channels
    $ phone_dm("maya_dm", "Maya", "avatars/maya_icon.png", start_hidden=False, start_locked=False)
    $ phone_dm("elias_dm", "Elias", "avatars/elias_icon.png", start_hidden=True, start_locked=True)

    # On rend Maya active au début (mais on ne l'ouvre pas)
    $ pswitch("maya_dm", open_chat=False, ensure_visible=True)
    $ current_app = "home"
    $ phone_nav_stack = []

    # Définition de la scène "ch1_maya"
    $ phone_story_define("ch1_maya", [

        pmsg("maya_dm", "Maya", "Réveille-toi, bêta-testeur préféré. Regarde l'heure en grand, c'est classe non ?"),
        pmsg("maya_dm", "Maya", "Je veux ton avis avant que je balance mes stories. Promis, c'est plus doux que mon café."),
        pmsg("maya_dm", phone_config["phone_player_name"], "Toujours prêt. J'ai le pouce encore à moitié endormi mais motivé."),
        pmsg("maya_dm", "Maya", "J'ai griffonné des idées pour ce soir. Style moderne, un peu teasing, zero drama."),
        pmsg("maya_dm", "Maya", "J'ai glissé un message caché dans la pile, clique pour jouer les espions."),
        pmsg("maya_dm", "Maya", "Je veux qu'on ait un moment rien qu'à deux avant que tout le monde arrive. Gardons ça pour nous.", kind=4),
        pmsg("maya_dm", phone_config["phone_player_name"], "Si tu caches déjà des choses, ça promet. Je clique quand ?"),
        pmsg("maya_dm", "Maya", "Attends, j'ajoute un sticker pour toi. <emoji_dizzy>"),
        pmsg("maya_dm", "Maya", "Ok, go. Délai serré, énergie haute. Je veux qu'on roule ensemble aujourd'hui."),
        pact(advance_phone_time, 8),
        pmsg("maya_dm", phone_config["phone_player_name"], "Marché conclu. J'enchaîne les notifs comme un pro du multitask."),
        pmsg("maya_dm", "Maya", "Parfait. J'ai ajouté deux aperçus dans la galerie pour te motiver."),
        pmsg("maya_dm", "Maya", "Le premier est juste un mood-board, l'autre c'est moi qui teste un angle miroir."),
        pmsg("maya_dm", phone_config["phone_player_name"], "Je vais tout regarder. Tu sais que j'aime les répétitions générales."),
        pmsg("maya_dm", "Maya", "Parlant de répétitions, je veux aussi voir comment tu replies en situation stress. Challenge accepté ?"),
        pact(advance_phone_time, 5),
        pmsg("maya_dm", phone_config["phone_player_name"], "Toujours. Et si je galère, je spamme Elias pour un avis technique."),

        # >>> MOMENT CLÉ : Maya mentionne Elias -> on dévoile et on switch
        pmsg("maya_dm", "Maya", "Haha, l'expert hardware. Va le ping, il adore quand tu débarques sans prévenir."),

        pact(pshow, "elias_dm"),
        pact(punlock, "elias_dm"),
        pact(pswitch, "elias_dm", True, True),

        # Elias enchaîne (bind sur elias_dm)
        pact(phone_story_define, "ch1_elias", [
            pmsg("elias_dm", "Elias", "Yo, j'ai vu ton statut passer. Déjà en mode sprint matinal ?"),
            pmsg("elias_dm", phone_config["phone_player_name"], "Yes. Maya me fait plancher. Besoin de toi si mon cerveau chauffe."),
            pmsg("elias_dm", "Elias", "Respire. Hydrate-toi. Et si tout casse, blame le wifi. Classic."),
            pmsg("elias_dm", phone_config["phone_player_name"], "Deal. Je te dois un café si ça marche."),
            # à la fin, tu peux reswitch si tu veux :
            # pact(plock, "elias_dm"), pact(punlock, "maya_dm"), pact(pswitch, "maya_dm", True, True),
        ]),
        pact(phone_story_bind_channel, "elias_dm", "ch1_elias"),
        pact(phone_story_start, "ch1_elias"),

    ])

    $ phone_story_bind_channel("maya_dm", "ch1_maya")
    $ phone_story_start("ch1_maya")

    # On reste dans le téléphone (pas de jump)
    call Phone
    return
