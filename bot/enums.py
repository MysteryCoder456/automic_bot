import enum


class TriggerType(enum.Enum):
    Message = "message"
    ReactionAdd = "reaction_add"
    ReactionRemove = "reaction_remove"
    MemberJoin = "member_join"
    MemberLeave = "member_leave"


class ActionType(enum.Enum):
    MessageSend = "message_send"
    MessageDelete = "message_delete"
    ReactionAdd = "reaction_add"
    ReactionRemove = "reaction_remove"
