import discord
from sqlalchemy.future import select

from bot.db import async_session, models


class MessageSendActionModal(discord.ui.Modal):
    """Modal for creating message send actions"""

    def __init__(self):
        super().__init__(
            discord.ui.InputText(
                label="Trigger ID",
                placeholder="Which trigger should execute this action?",
                style=discord.InputTextStyle.singleline,
            ),
            discord.ui.InputText(
                label="Channel ID",
                placeholder="Where do you want the bot to send a message?",
                style=discord.InputTextStyle.singleline,
            ),
            discord.ui.InputText(
                label="Message Content",
                placeholder="What do you want the bot to say?",
                style=discord.InputTextStyle.multiline,
            ),
            title="New Message Send Action",
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        # Check whether fields are entered correctly
        try:
            trigger_id = int(self.children[0].value)  # type: ignore
            channel_id = int(self.children[1].value)  # type: ignore
            message_content = self.children[2].value

        except ValueError:
            await interaction.response.send_message(
                "One of the fields was entered incorrectly, please try again..."
            )
            return

        # Make sure the provided channel exists
        try:
            _ = await interaction.guild.fetch_channel(channel_id)

        except discord.HTTPException or discord.Forbidden or discord.NotFound:
            await interaction.response.send_message(
                f"Unable to find any channel with ID `{channel_id}` in this server!"
            )
            return

        async with async_session() as session:
            # Check whether the given trigger ID is valid
            query = (
                select(models.Trigger)
                .where(models.Trigger.id == trigger_id)
                .where(models.Trigger.guild_id == interaction.guild_id)
            )
            result = await session.execute(query)
            trigger: models.Trigger | None = result.scalar()

            if not trigger:
                await interaction.response.send_message(
                    f"Unable to find a trigger with ID `{trigger_id}` in this server!"
                )
                return

            new_action = models.MessageSendAction(
                guild_id=interaction.guild_id,
                trigger=trigger,
                channel_id=channel_id,
                message_content=message_content,
            )
            session.add(new_action)
            await session.commit()

        embed = discord.Embed(
            title="New Action",
            description="A new action has been created!",
            color=discord.Color.green(),
        )
        embed.add_field(name="Action ID", value=str(new_action.id))
        embed.add_field(name="Action Type", value="MessageSend")
        embed.add_field(name="Trigger ID", value=str(new_action.trigger_id))

        await interaction.response.send_message(embed=embed)
