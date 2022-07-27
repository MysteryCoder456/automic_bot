import asyncio
from math import ceil, floor
import discord
from discord.ext import commands, pages
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from bot import TESTING_GUILDS, trigger_id_autocomplete
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

    def base_response_embed(self, trigger: models.Trigger) -> discord.Embed:
        return (
            discord.Embed(
                title="New Trigger",
                description="A new trigger has been created!",
                color=self.theme,
            )
            .add_field(name="Trigger ID", value=str(trigger.id))
            .add_field(name="Trigger Type", value=trigger.type.name)
        )

    @trigger_add_group.command(name="message")
    @commands.has_guild_permissions(administrator=True)
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

        embed = self.base_response_embed(new_trigger)
        embed.add_field(name="Match Statement", value=match_statement)
        embed.add_field(name="Channel", value=channel.mention)

        await ctx.respond(embed=embed)

    @trigger_add_group.command(name="reactionadd")
    @commands.has_guild_permissions(administrator=True)
    async def add_reaction_add_trigger(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel,
        message_id: str,
        emoji: discord.PartialEmoji | None,
    ):
        """Add a trigger that executes when someone reacts to a message. Looks for all emojis by default."""

        if not message_id.isnumeric():
            await ctx.respond(
                "Please enter a valid message ID!", ephemeral=True
            )
            return

        msg_id = int(message_id)

        try:
            # Make sure that the provided message is accessible
            msg = await channel.fetch_message(msg_id)
        except discord.NotFound:
            await ctx.respond(
                f"Unable to find a message with ID `{msg_id}` in {channel.mention}!"
            )
            return
        except discord.Forbidden:
            await ctx.respond(
                f"I don't have permission to access that message in {channel.mention}!"
            )
            return
        except discord.HTTPException:
            await ctx.respond(
                "Something went wrong while accessing that message, please try again!"
            )
            return

        if emoji:
            em = emoji.id if emoji.is_custom_emoji() else emoji.name
        else:
            em = None

        async with async_session() as session:
            new_trigger = models.Trigger(
                guild_id=ctx.guild_id,
                type=TriggerType.ReactionAdd,
                activation_params={
                    "channel_id": channel.id,
                    "message_id": msg_id,
                    "emoji": em,
                },
            )
            session.add(new_trigger)
            await session.commit()

        embed = self.base_response_embed(new_trigger)
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(
            name="Message", value=f"[Jump To Message]({msg.jump_url})"
        )
        embed.add_field(
            name="Emoji", value="All emojis" if emoji is None else str(emoji)
        )

        await ctx.respond(embed=embed)

    @trigger_add_group.command(name="reactionremove")
    @commands.has_guild_permissions(administrator=True)
    async def add_reaction_remove_trigger(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel,
        message_id: str,
        emoji: discord.PartialEmoji | None,
    ):
        """Add a trigger that executes when someone unreacts from a message. Looks for all emojis by default."""

        if not message_id.isnumeric():
            await ctx.respond(
                "Please enter a valid message ID!", ephemeral=True
            )
            return

        msg_id = int(message_id)

        try:
            # Make sure that the provided message is accessible
            msg = await channel.fetch_message(msg_id)
        except discord.NotFound:
            await ctx.respond(
                f"Unable to find a message with ID `{msg_id}` in {channel.mention}!"
            )
            return
        except discord.Forbidden:
            await ctx.respond(
                f"I don't have permission to access that message in {channel.mention}!"
            )
            return
        except discord.HTTPException:
            await ctx.respond(
                "Something went wrong while accessing that message, please try again!"
            )
            return

        if emoji:
            em = emoji.id if emoji.is_custom_emoji() else emoji.name
        else:
            em = None

        async with async_session() as session:
            new_trigger = models.Trigger(
                guild_id=ctx.guild_id,
                type=TriggerType.ReactionRemove,
                activation_params={
                    "channel_id": channel.id,
                    "message_id": msg_id,
                    "emoji": em,
                },
            )
            session.add(new_trigger)
            await session.commit()

        embed = self.base_response_embed(new_trigger)
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(
            name="Message", value=f"[Jump To Message]({msg.jump_url})"
        )
        embed.add_field(
            name="Emoji", value="All emojis" if emoji is None else str(emoji)
        )

        await ctx.respond(embed=embed)

    @trigger_group.command(name="remove")
    @commands.has_guild_permissions(administrator=True)
    @discord.option("trigger_id", autocomplete=trigger_id_autocomplete)
    async def remove_trigger(
        self, ctx: discord.ApplicationContext, trigger_id: int
    ):
        """Permanently remove a trigger and all associated actions"""

        async with async_session() as session:
            query = (
                select(models.Trigger)
                .where(models.Trigger.id == trigger_id)
                .where(models.Trigger.guild_id == ctx.guild_id)
                .options(selectinload(models.Trigger.actions))
            )
            trigger: models.Trigger | None = await session.scalar(query)

            if trigger:
                embed = discord.Embed(
                    title="Removed Trigger",
                    description="An existing trigger has been permanently removed, along with all actions associated with it!",
                    color=self.theme,
                )
                embed.add_field(name="Trigger ID", value=str(trigger.id))
                embed.add_field(name="Trigger Type", value=trigger.type.name)

                action_delete_tasks = [
                    session.delete(action) for action in trigger.actions
                ]
                await asyncio.gather(*action_delete_tasks)
                await session.delete(trigger)
                await session.commit()

                await ctx.respond(embed=embed)

            else:
                await ctx.respond(
                    f"Couldn't find any triggers with ID `{trigger_id}` in this server!",
                    ephemeral=True,
                )

    @trigger_group.command(name="list")
    async def list_triggers(self, ctx: discord.ApplicationContext):
        """List all the triggers in the current server"""

        if not ctx.guild:
            return

        async with async_session() as session:
            query = select(models.Trigger).where(
                models.Trigger.guild_id == ctx.guild_id
            )
            triggers: list[models.Trigger] = list(await session.scalars(query))

        max_per_page = 5
        total_pages = ceil(len(triggers) / max_per_page)
        embeds = [
            discord.Embed(
                title=f"Triggers in {ctx.guild.name}", color=self.theme
            ).set_footer(text=f"Page {i + 1} of {total_pages}")
            for i in range(total_pages)
        ]

        for i, trigger in enumerate(triggers):
            idx = floor(i / max_per_page)
            params_txt = "\n".join(
                [
                    f"{key.replace('_', ' ').title()}: `{value}`"
                    for key, value in trigger.activation_params.items()
                ]
            )

            embeds[idx].add_field(
                name=f"Trigger ID: {trigger.id}",
                value=f"Type: `{trigger.type.name}`\n{params_txt}",
                inline=False,
            )

        paginator = pages.Paginator(embeds)  # type: ignore
        await paginator.respond(ctx.interaction)


def setup(bot: commands.Bot):
    bot.add_cog(Triggers())
