default currentCharacter = None

label start:
    # Auto-reprise si un autosave existe
    if renpy.can_load("auto-1"):
        $ phone_loaded_from_save = True
        $ renpy.load("auto-1")

    if not phone_loaded_from_save:
        $ reset_phone_data()
        $ phone_start()

        jump CH1_init         # Character + #Chapter + #Scene

    else:
        $ phone_loaded_from_save = False

    call Phone
    return
