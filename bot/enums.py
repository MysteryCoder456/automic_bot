import enum


class TriggerType(enum.Enum):
    # Value of each variant signifies dynamic parameters
    Message = {
        "member": None,
        "member_mention": None,
        "channel": None,
        "matched_string": None,
        "message_content": None,
    }
    ReactionAdd = {
        "member": None,
        "member_mention": None,
        "channel": None,
        "emoji": None,
    }
    ReactionRemove = {
        "member": None,
        "member_mention": None,
        "channel": None,
        "emoji": None,
    }
    MemberJoin = {}
    MemberLeave = {}


class ActionType(enum.Enum):
    MessageSend = "message_send"
    MessageDelete = "message_delete"
    ReactionAdd = "reaction_add"
    ReactionRemove = "reaction_remove"
