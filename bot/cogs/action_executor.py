import asyncio
import re
import discord
from discord.abc import GuildChannel, PrivateChannel
from discord.ext import commands
from sqlalchemy.future import select
from sqlalchemy.engine.result import ChunkedIteratorResult
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
            result: ChunkedIteratorResult = await session.execute(query)

            for trigger in result.scalars():
                # For type hinting only, has no functional purpose
                trigger: models.Trigger = trigger

                params: dict = trigger.activation_params  # type: ignore
                match_statement: str = params["match_statement"]
                channel_id: int = params["channel_id"]

                re_result = re.fullmatch(match_statement, message.content)

                if re_result is not None and message.channel.id == channel_id:
                    action_tasks = []

                    for action in trigger.actions:
                        dynamic_params = action.type.value.copy()
                        dynamic_params["member"] = message.author
                        dynamic_params[
                            "member_mention"
                        ] = message.author.mention
                        dynamic_params["channel"] = message.channel.mention  # type: ignore
                        dynamic_params["matched_string"] = re_result.string

                        task = self.execute_action(action, **dynamic_params)
                        action_tasks.append(task)

                    await asyncio.gather(*action_tasks)


def setup(bot: commands.Bot):
    bot.add_cog(ActionExecutor(bot))
