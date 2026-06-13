import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CHANNELS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "channels.json")


def load_channels() -> dict:
    if not os.path.exists(CHANNELS_FILE):
        return {}
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_channels(data: dict) -> None:
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_allowed_channel(guild_id: int) -> int | None:
    channels = load_channels()
    return channels.get(str(guild_id))


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="set", description="このチャンネルをBotの操作チャンネルとして設定します")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_channel(self, interaction: discord.Interaction) -> None:
        channels = load_channels()
        channels[str(interaction.guild_id)] = interaction.channel_id
        save_channels(channels)

        embed = discord.Embed(
            title="Channel Set",
            description=(
                f"<#{interaction.channel_id}> をBot操作チャンネルに設定しました。\n"
                "このチャンネル以外ではコマンドが無効になります。"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @set_channel.error
    async def set_channel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "このコマンドはチャンネル管理権限が必要です。", ephemeral=True
            )
