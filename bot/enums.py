import enum


class TriggerType(enum.Enum):
    Message = "message"
    ReactionAdd = "reaction_add"
    ReactionRemove = "reaction_remove"
    MemberJoin = "member_join"
    MemberLeave = "member_leave"
