import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")

if not DISCORD_TOKEN:
    raise RuntimeError(".env に DISCORD_TOKEN が設定されていません。")
if not DISCORD_APPLICATION_ID:
    raise RuntimeError(".env に DISCORD_APPLICATION_ID が設定されていません。")


intents = discord.Intents.default()
intents.message_content = False

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=int(DISCORD_APPLICATION_ID),
)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


async def main() -> None:
    async with bot:
        await bot.load_extension("cogs.settings")
        await bot.load_extension("cogs.search")
        await bot.tree.sync()
        print("Slash commands synced.")
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
