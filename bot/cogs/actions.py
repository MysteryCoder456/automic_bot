import discord
from discord.ext import commands
from sqlalchemy.future import select

from bot import TESTING_GUILDS
from bot.db import async_session, models
from bot.enums import ActionType


class Actions(commands.Cog):
    """Add or modify actions"""

    action_group = discord.SlashCommandGroup(
        name="action",
        description="Add or modify actions",
        guild_ids=TESTING_GUILDS,
    )
    action_add_group = action_group.create_subgroup(
        name="add", description="Add new actions", guild_ids=TESTING_GUILDS
    )
    theme = discord.Color.green()

    @action_add_group.command(name="messagesend")
    @commands.has_guild_permissions(administrator=True)
    async def add_message_send_action(
        self,
        ctx: discord.ApplicationContext,
        trigger_id: int,
        message_content: str,
        channel: discord.TextChannel,
    ):
        """Add a new MessageSend action"""

        async with async_session() as session:
            query = (
                select(models.Trigger)
                .where(models.Trigger.id == trigger_id)
                .where(models.Trigger.guild_id == ctx.guild_id)
            )
            result = await session.execute(query)
            trigger: models.Trigger | None = result.scalar()

            if not trigger:
                await ctx.respond(
                    f"Couldn't find any triggers with ID `{trigger_id}` in this server!"
                )
                return

            new_action = models.Action(
                guild_id=ctx.guild_id,
                type=ActionType.MessageSend,
                action_params={
                    "message_content": message_content,
                    "channel_id": channel.id,
                },
                trigger=trigger,
            )
            session.add(new_action)
            await session.commit()

        embed = discord.Embed(
            title="New Action",
            description="A new action has been created!",
            color=self.theme,
        )
        embed.add_field(name="Action ID", value=str(new_action.id))
        embed.add_field(name="Trigger ID", value=str(trigger_id))
        embed.add_field(name="Action Type", value=new_action.type.name)
        embed.add_field(name="Message Content", value=message_content[:100])
        embed.add_field(name="Channel", value=channel.mention)

        await ctx.respond(embed=embed)

    @action_group.command(name="remove")
    async def remove_action(
        self, ctx: discord.ApplicationContext, action_id: int
    ):
        """Permanently remove an action"""

        async with async_session() as session:
            query = (
                select(models.Action)
                .where(models.Action.id == action_id)
                .where(models.Action.guild_id == ctx.guild_id)
            )
            result = await session.execute(query)

            if action := result.scalar():
                embed = discord.Embed(
                    title="Removed Action",
                    description="An existing action has been permanently removed!",
                    color=self.theme,
                )
                embed.add_field(name="Action ID", value=str(action.id))
                embed.add_field(
                    name="Trigger ID", value=str(action.trigger_id)
                )
                embed.add_field(name="Action Type", value=action.type.name)

                await session.delete(action)
                await session.commit()

                await ctx.respond(embed=embed)

            else:
                await ctx.respond(
                    f"Couldn't find any actions with ID `{action_id}` in this server!"
                )
                return


def setup(bot: commands.Bot):
    bot.add_cog(Actions())
