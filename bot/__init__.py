import os
import json
import asyncio
import pathlib
import discord
from discord.ext import commands
from sqlalchemy.future import select

from bot import db
from bot.db import models

if testing_guilds_txt := os.getenv("TESTING_GUILDS"):
    TESTING_GUILDS: list[int] | None = json.loads(testing_guilds_txt)
else:
    TESTING_GUILDS = None

intents = discord.Intents.all()
bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.slash_command(guild_ids=TESTING_GUILDS)
async def ping(ctx: discord.ApplicationContext):
    latency = round(bot.latency * 1000)
    await ctx.respond(f"Pong! That took `{latency} ms`!")


async def trigger_id_autocomplete(
    ctx: discord.AutocompleteContext,
) -> list[int]:
    """Returns a list of trigger IDs in the current server."""

    async with db.async_session() as session:
        query = select(models.Trigger).where(
            models.Trigger.guild_id == ctx.interaction.guild_id
        )
        triggers = await session.scalars(query)
        return [t.id for t in triggers if str(t.id) in ctx.value or len(ctx.value) == 0]


def add_cogs():
    cogs_dir = pathlib.Path(__file__).parent / "cogs"
    cogs_list = [
        f"bot.cogs.{file[:-3]}"
        for file in os.listdir(cogs_dir)
        if file.endswith(".py")
    ]
    loaded_cogs = bot.load_extensions(*cogs_list, store=False)

    if isinstance(loaded_cogs, list):
        print(f"Loaded {len(loaded_cogs)} cogs:", *loaded_cogs, sep="\n")


def main(token: str):
    loop = asyncio.get_event_loop()

    try:
        db.init_engine()
        add_cogs()
        loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt or SystemExit:
        print("Shutting down...")
        loop.run_until_complete(bot.close())
        loop.run_until_complete(db.deinit_engine())
