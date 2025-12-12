default currentCharacter = None

label start:
    $ reset_phone_data()
    $ phone_start()

    call Phone
    return


image emoji_sob = "phone/emoji/sob.png"
image emoji_dizzy = "phone/emoji/dizzy.png"
