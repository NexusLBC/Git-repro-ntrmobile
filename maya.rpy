default messenger_contacts = {}
default messenger_conversations = {}
default messenger_loaded_counts = {}
default messenger_view = "list"
default messenger_current_conversation = None

init python:
    MESSENGER_PAGE_SIZE = 20

    def load_messenger_from_persistent():
        data = getattr(persistent, "messenger_state", None)
        if data:
            store.messenger_contacts = data.get("contacts", {})
            store.messenger_conversations = data.get("conversations", {})
            store.messenger_loaded_counts = data.get("loaded_counts", {})
            store.messenger_view = data.get("view", "list")
            store.messenger_current_conversation = data.get("current_conversation")

    def save_messenger_to_persistent():
        persistent.messenger_state = {
            "contacts": store.messenger_contacts,
            "conversations": store.messenger_conversations,
            "loaded_counts": store.messenger_loaded_counts,
            "view": store.messenger_view,
            "current_conversation": store.messenger_current_conversation,
        }
        renpy.save_persistent()

    def ensure_messenger_contact(contact_id, display_name=None, avatar=None):
        if contact_id not in store.messenger_contacts:
            store.messenger_contacts[contact_id] = {
                "id": contact_id,
                "name": display_name or contact_id,
                "avatar": avatar or "gui/buttons/messenger_idle.png",
            }
        if contact_id not in store.messenger_conversations:
            store.messenger_conversations[contact_id] = []
        if contact_id not in store.messenger_loaded_counts:
            store.messenger_loaded_counts[contact_id] = MESSENGER_PAGE_SIZE

    def add_messenger_message(contact_id, sender, message_text, kind="text", summary_alt="none", image_size=(320, 320)):
        load_messenger_from_persistent()
        ensure_messenger_contact(contact_id)
        conversation = store.messenger_conversations[contact_id]
        message_id = len(conversation) + 1
        conversation.append(
            {
                "id": message_id,
                "sender": sender,
                "text": message_text,
                "kind": kind,
                "summary_alt": summary_alt,
                "image_size": image_size,
            }
        )
        store.messenger_loaded_counts[contact_id] = min(
            len(conversation), store.messenger_loaded_counts.get(contact_id, MESSENGER_PAGE_SIZE)
        )
        save_messenger_to_persistent()

    def messenger_preview(contact_id):
        messages = store.messenger_conversations.get(contact_id, [])
        for entry in reversed(messages):
            if entry.get("kind") != "timestamp":
                preview = entry.get("summary_alt")
                if preview and preview != "none":
                    return preview
                text = entry.get("text", "")
                max_len = phone_config.get("preview_max_length", 35)
                return text if len(text) <= max_len else text[: max_len - 3] + "..."
        return phone_config.get("preview_no_message", "Empty chat...")

    def set_messenger_conversation(contact_id):
        load_messenger_from_persistent()
        ensure_messenger_contact(contact_id)
        store.messenger_current_conversation = contact_id
        store.messenger_view = "conversation"
        store.messenger_loaded_counts[contact_id] = min(
            len(store.messenger_conversations.get(contact_id, [])),
            max(store.messenger_loaded_counts.get(contact_id, MESSENGER_PAGE_SIZE), MESSENGER_PAGE_SIZE),
        )
        save_messenger_to_persistent()

    def messenger_back_to_list():
        store.messenger_view = "list"
        store.messenger_current_conversation = None
        save_messenger_to_persistent()

    def messenger_visible_messages(contact_id):
        conversation = store.messenger_conversations.get(contact_id, [])
        loaded = store.messenger_loaded_counts.get(contact_id, MESSENGER_PAGE_SIZE)
        return conversation[-loaded:]

    def messenger_load_more(contact_id):
        conversation = store.messenger_conversations.get(contact_id, [])
        current_loaded = store.messenger_loaded_counts.get(contact_id, MESSENGER_PAGE_SIZE)
        store.messenger_loaded_counts[contact_id] = min(len(conversation), current_loaded + MESSENGER_PAGE_SIZE)
        save_messenger_to_persistent()
        renpy.restart_interaction()

label maya_scene_1:
    $ ensure_messenger_contact("maya_dm", display_name="Maya", avatar="gui/buttons/messenger_idle.png")
    $ send_phone_message("Maya", "Tu veux que je t'envoie une image ?", "maya_dm")

    $ present_phone_choices(
        [
            ("Oui, envoie !", "Oui, envoie !", Call("maya_envoie_image")),
            ("Pas maintenant", "Pas maintenant, je suis occupé.", Call("maya_refuse_image")),
        ],
        "maya_dm",
    )
    return
