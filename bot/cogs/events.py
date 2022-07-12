import enum
import discord
from discord.ext import commands

from bot import TESTING_GUILDS


class TriggerType(enum.Enum):
    Message = "message"
    Reaction = "reaction"


class Triggers(commands.Cog):
    """Add or modify action triggers"""

    trigger_group = discord.SlashCommandGroup(
        name="trigger",
        description="Add or modify action triggers",
        guild_ids=TESTING_GUILDS,
    )

    @trigger_group.command(name="add")
    async def add_trigger(
        self, ctx: discord.ApplicationContext, trigger_type: TriggerType
    ):
        """Add a new trigger"""

        await ctx.respond("Coming soon...")


def setup(bot: commands.Bot):
    bot.add_cog(Triggers())
