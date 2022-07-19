import discord
from discord.ext import commands

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
    theme = discord.Color.dark_blue()

    @trigger_group.command(name="add")
    @commands.has_guild_permissions(administrator=True)
    async def add_trigger(
        self, ctx: discord.ApplicationContext, trigger_type: TriggerType
    ):
        """Add a new trigger"""

        async with async_session() as session:
            new_trigger = models.Trigger(
                guild_id=ctx.guild_id, type=trigger_type
            )
            session.add(new_trigger)
            await session.commit()

        embed = discord.Embed(
            title="New Trigger",
            description="A new trigger has been created!",
            color=self.theme,
        )
        embed.add_field(name="Trigger ID", value=str(new_trigger.id))
        embed.add_field(name="Trigger Type", value=trigger_type.name)

        await ctx.respond(embed=embed)

    @trigger_group.command(name="remove")
    @commands.has_guild_permissions(administrator=True)
    async def remove_trigger(
        self, ctx: discord.ApplicationContext, trigger_id: int
    ):
        """Remove an existing trigger"""

        async with async_session() as session:
            trigger = await session.get(models.Trigger, trigger_id)

            if trigger and trigger.guild_id == ctx.guild_id:
                embed = discord.Embed(
                    title="Deleted Trigger",
                    description="An existing trigger has been removed!",
                    color=self.theme,
                )
                embed.add_field(name="Trigger ID", value=str(trigger.id))
                embed.add_field(name="Trigger Type", value=trigger.type.name)

                await session.delete(trigger)
                await session.commit()

                await ctx.respond(embed=embed)

            else:
                await ctx.respond(
                    f"Unable to find a trigger with ID `{trigger_id}` in this server"
                )


def setup(bot: commands.Bot):
    bot.add_cog(Triggers())
