import discord
from discord.ext import commands

from bot import TESTING_GUILDS
from bot.enums import ActionType
from bot.ui import MessageSendActionModal


class Actions(commands.Cog):
    """Add or modify actions"""

    action_group = discord.SlashCommandGroup(
        name="action",
        description="Add or modify actions",
        guild_ids=TESTING_GUILDS,
    )
    theme = discord.Color.green()

    @action_group.command(name="add")
    @commands.has_guild_permissions(administrator=True)
    async def add_action(
        self, ctx: discord.ApplicationContext, action_type: ActionType
    ):
        """Add a new action"""

        match action_type:
            case ActionType.MessageSend:
                await ctx.send_modal(MessageSendActionModal())


def setup(bot: commands.Bot):
    bot.add_cog(Actions())
