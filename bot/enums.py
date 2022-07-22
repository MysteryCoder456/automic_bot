import enum


class TriggerType(enum.Enum):
    Message = "message"
    ReactionAdd = "reaction_add"
    ReactionRemove = "reaction_remove"
    MemberJoin = "member_join"
    MemberLeave = "member_leave"


class ActionType(enum.Enum):
    # Value of each variant signifies dynamic parameters
    MessageSend = {
        "member": None,
        "member_mention": None,
        "channel": None,
        "matched_string": None,
    }
    MessageDelete = {}
    ReactionAdd = {}
    ReactionRemove = {}
