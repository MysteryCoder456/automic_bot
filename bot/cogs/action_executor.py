import re
import asyncio
from typing import Iterable

import discord
from discord.abc import GuildChannel, PrivateChannel
from discord.ext import commands
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from bot.db import async_session, models
from bot.enums import ActionType, TriggerType


class ActionExecutor(commands.Cog):
    """Listens for trigger events and executes actions"""

    def __init__(self, bot: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def get_or_fetch_channel(
        self, channel_id: int
    ) -> GuildChannel | PrivateChannel | discord.Thread:
        """Gets a channel from local cache, but queries Discord API if not found in cache"""

        return self.bot.get_channel(
            channel_id
        ) or await self.bot.fetch_channel(channel_id)

    async def execute_action(self, action: models.Action, **kwargs):
        params: dict = action.action_params  # type: ignore

        if action.type == ActionType.MessageSend:
            message_content = params["message_content"]
            channel_id = params["channel_id"]

            formatted_msg_content = message_content.format(**kwargs)
            channel = await self.get_or_fetch_channel(channel_id)

            if isinstance(channel, discord.TextChannel):
                await channel.send(formatted_msg_content)

        # TODO: Add other action types...

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listens for Message trigger events"""

        if not message.guild:
            return

        async with async_session() as session:
            query = (
                select(models.Trigger)
                .where(models.Trigger.guild_id == message.guild.id)
                .where(models.Trigger.type == TriggerType.Message)
                .options(selectinload(models.Trigger.actions))
            )
            triggers: Iterable[models.Trigger] = await session.scalars(query)

            for trigger in triggers:
                params: dict = trigger.activation_params  # type: ignore
                match_statement: str = params["match_statement"]
                channel_id: int = params["channel_id"]

                re_result = re.fullmatch(match_statement, message.content)

                if re_result is not None and message.channel.id == channel_id:
                    dynamic_params = trigger.type.value.copy()
                    dynamic_params["member"] = message.author
                    dynamic_params["member_mention"] = message.author.mention
                    dynamic_params["channel"] = message.channel.mention  # type: ignore
                    dynamic_params["matched_string"] = re_result.string
                    dynamic_params["messsage_content"] = message.content

                    action_tasks = [
                        self.execute_action(action, **dynamic_params)
                        for action in trigger.actions
                    ]
                    await asyncio.gather(*action_tasks)

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ):
        """Listens for ReactionAdd trigger events"""

        channel = await self.get_or_fetch_channel(payload.channel_id)

        if not (
            payload.guild_id
            and payload.member
            and isinstance(channel, discord.TextChannel)
        ):
            return

        async with async_session() as session:
            query = (
                select(models.Trigger)
                .where(models.Trigger.guild_id == payload.guild_id)
                .where(models.Trigger.type == TriggerType.ReactionAdd)
                .options(selectinload(models.Trigger.actions))
            )
            triggers: Iterable[models.Trigger] = await session.scalars(query)

            for trigger in triggers:
                params: dict = trigger.activation_params  # type: ignore
                channel_id: int = params["channel_id"]
                message_id: int = params["message_id"]
                emoji: str | int | None = params["emoji"]

                payload_emoji = (
                    payload.emoji.id
                    if payload.emoji.is_custom_emoji()
                    else payload.emoji.name
                )

                if (
                    payload.channel_id == channel_id
                    and payload.message_id == message_id
                    and (emoji is None or emoji == payload_emoji)
                ):
                    dynamic_params = trigger.type.value.copy()
                    dynamic_params["member"] = payload.member
                    dynamic_params["member_mention"] = payload.member.mention
                    dynamic_params["channel"] = channel.mention
                    dynamic_params["emoji"] = payload.emoji

                    action_tasks = [
                        self.execute_action(action, **dynamic_params)
                        for action in trigger.actions
                    ]
                    await asyncio.gather(*action_tasks)


def setup(bot: commands.Bot):
    bot.add_cog(ActionExecutor(bot))
