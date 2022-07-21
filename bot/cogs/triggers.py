import discord
from discord.ext import commands
from sqlalchemy.future import select

from bot import TESTING_GUILDS
from bot.db import async_session, models
from bot.enums import TriggerType


class Triggers(commands.Cog):
    """Add or modify action triggers"""

    trigger_group = discord.SlashCommandGroup(
        name="trigger",
        description="Add or modify action triggers",
        guild_ids=TESTING_GUILDS,
    )
    trigger_add_group = trigger_group.create_subgroup(
        name="add", description="Add action triggers", guild_ids=TESTING_GUILDS
    )
    theme = discord.Color.dark_blue()

    @trigger_add_group.command(name="message")
    async def add_message_trigger(
        self,
        ctx: discord.ApplicationContext,
        match_statement: str,
        channel: discord.TextChannel,
    ):
        """Add a trigger that executes when a new message matches the match statement. Regex can also be used."""

        async with async_session() as session:
            new_trigger = models.Trigger(
                guild_id=ctx.guild_id,
                type=TriggerType.Message,
                activation_params={
                    "match_statement": match_statement,
                    "channel_id": channel.id,
                },
            )
            session.add(new_trigger)
            await session.commit()

        embed = discord.Embed(
            title="New Trigger",
            description="A new trigger has been created!",
            color=self.theme,
        )
        embed.add_field(name="Trigger ID", value=str(new_trigger.id))
        embed.add_field(name="Trigger Type", value=TriggerType.Message.name)

        await ctx.respond(embed=embed)

    @trigger_group.command(name="remove")
    async def remove_trigger(
        self, ctx: discord.ApplicationContext, trigger_id: int
    ):
        """Permanently remove a trigger and all associated actions"""

        async with async_session() as session:
            query = (
                select(models.Trigger)
                .where(models.Trigger.id == trigger_id)
                .where(models.Trigger.guild_id == ctx.guild_id)
            )
            result = await session.execute(query)

            if trigger := result.scalar():
                embed = discord.Embed(
                    title="Removed Trigger",
                    description="An existing trigger has been permanently removed, along with all actions associated with it!",
                    color=self.theme,
                )
                embed.add_field(name="Trigger ID", value=str(trigger.id))
                embed.add_field(name="Trigger Type", value=trigger.type.name)

                await session.delete(trigger)
                await session.commit()

                await ctx.respond(embed=embed)

            else:
                await ctx.respond(
                    f"Couldn't find any triggers with ID `{trigger_id}` in this server!"
                )


def setup(bot: commands.Bot):
    bot.add_cog(Triggers())
