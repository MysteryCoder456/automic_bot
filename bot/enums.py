import enum


class TriggerType(enum.Enum):
    # Value of each variant signifies dynamic parameters.
    # Each variant also contains a "trigger_type" key to
    # avoid confusing SQLAlchemy with the type of the enum.

    Message = {
        "trigger_type": "message",
        "member": None,
        "member_mention": None,
        "channel": None,
        "matched_string": None,
        "message_content": None,
    }
    ReactionAdd = {
        "trigger_type": "reaction_add",
        "member": None,
        "member_mention": None,
        "channel": None,
        "emoji": None,
    }
    ReactionRemove = {
        "trigger_type": "reaction_remove",
        "member": None,
        "member_mention": None,
        "channel": None,
        "emoji": None,
    }
    MemberJoin = {
        "trigger_type": "member_join",
    }
    MemberLeave = {
        "trigger_type": "member_leave",
    }


class ActionType(enum.Enum):
    MessageSend = "message_send"
    MessageDelete = "message_delete"
    ReactionAdd = "reaction_add"
    ReactionRemove = "reaction_remove"
