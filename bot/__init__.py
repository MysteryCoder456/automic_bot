import os
import json
import discord
from discord.ext import commands

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
    await ctx.respond(f"Pong! That took {latency} ms!")


def main(token: str):
    try:
        bot.run(token)
    except KeyboardInterrupt or SystemExit:
        print("Shutting down...")
