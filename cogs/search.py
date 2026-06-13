import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
from utils.google_api import search_images, search_videos, search_web, search_news
from cogs.settings import get_allowed_channel


def channel_guard(interaction: discord.Interaction) -> bool:
    allowed = get_allowed_channel(interaction.guild_id)
    if allowed is None:
        return True
    return interaction.channel_id == allowed


# --------------------------------------------------------------------------- #
#  Image pagination view
# --------------------------------------------------------------------------- #

class ImagePaginationView(discord.ui.View):
    def __init__(self, results: list[dict], query: str, user: discord.User | discord.Member):
        super().__init__(timeout=120)
        self.results = results
        self.query = query
        self.user = user
        self.index = 0
        self._update_buttons()

    def _update_buttons(self) -> None:
        self.back_btn.disabled = self.index == 0
        self.next_btn.disabled = self.index >= len(self.results) - 1

    def build_embed(self) -> discord.Embed:
        item = self.results[self.index]
        embed = discord.Embed(
            title=item["title"],
            url=item["url"],
            color=discord.Color.blue(),
        )
        embed.add_field(name="Image URL", value=item["url"], inline=False)
        embed.add_field(name="Source Page", value=item["page_url"] or "N/A", inline=False)
        embed.add_field(name="Source", value=item["source"], inline=True)
        embed.add_field(name="Copyright", value=item["license"], inline=True)
        embed.set_image(url=item["url"])
        embed.set_footer(text=f"Searched by {self.user.display_name}  |  {self.index + 1} / {len(self.results)}")
        return embed

    async def _check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("このボタンはコマンドを実行したユーザーのみ操作できます。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not await self._check(interaction):
            return
        self.index -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not await self._check(interaction):
            return
        self.index += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


# --------------------------------------------------------------------------- #
#  Video pagination view
# --------------------------------------------------------------------------- #

class VideoPaginationView(discord.ui.View):
    def __init__(self, results: list[dict], query: str, user: discord.User | discord.Member, next_page_token: str | None = None):
        super().__init__(timeout=120)
        self.results = results
        self.query = query
        self.user = user
        self.next_page_token = next_page_token
        self.index = 0
        self._update_buttons()

    def _update_buttons(self) -> None:
        self.back_btn.disabled = self.index == 0
        self.next_btn.disabled = self.index >= len(self.results) - 1 and self.next_page_token is None

    def build_embed(self) -> discord.Embed:
        item = self.results[self.index]
        embed = discord.Embed(
            title=item["title"],
            url=item["url"],
            color=discord.Color.red(),
        )
        embed.add_field(name="Video URL", value=item["url"], inline=False)
        embed.add_field(name="Channel", value=item["channel"], inline=True)
        embed.set_image(url=item["thumbnail"])
        embed.set_footer(text=f"Searched by {self.user.display_name}  |  {self.index + 1} / {len(self.results)}")
        return embed

    async def _check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("このボタンはコマンドを実行したユーザーのみ操作できます。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not await self._check(interaction):
            return
        self.index -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not await self._check(interaction):
            return
        if self.index < len(self.results) - 1:
            self.index += 1
        elif self.next_page_token:
            await interaction.response.defer(thinking=True)
            new_results, new_token = await search_videos(self.query, self.next_page_token)
            self.results.extend(new_results)
            self.next_page_token = new_token
            self.index += 1
            self._update_buttons()
            await interaction.edit_original_response(embed=self.build_embed(), view=self)
            return
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


# --------------------------------------------------------------------------- #
#  Web / News list view
# --------------------------------------------------------------------------- #

class WebListView(discord.ui.View):
    def __init__(self, results: list[dict], query: str, user: discord.User | discord.Member, mode: str = "web"):
        super().__init__(timeout=120)
        self.results = results
        self.query = query
        self.user = user
        self.mode = mode
        self.index = 0
        self._update_buttons()

    def _update_buttons(self) -> None:
        self.back_btn.disabled = self.index == 0
        self.next_btn.disabled = self.index >= len(self.results) - 1

    def build_embed(self) -> discord.Embed:
        item = self.results[self.index]
        color = discord.Color.green() if self.mode == "news" else discord.Color.blurple()
        embed = discord.Embed(
            title=item["title"],
            url=item["url"],
            description=item.get("snippet", ""),
            color=color,
        )
        embed.add_field(name="Source", value=item["source"], inline=True)
        embed.set_footer(text=f"Searched by {self.user.display_name}  |  {self.index + 1} / {len(self.results)}")
        return embed

    async def _check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("このボタンはコマンドを実行したユーザーのみ操作できます。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not await self._check(interaction):
            return
        self.index -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not await self._check(interaction):
            return
        self.index += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


# --------------------------------------------------------------------------- #
#  Cog
# --------------------------------------------------------------------------- #

class Search(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _denied_embed(self, allowed_channel_id: int) -> discord.Embed:
        return discord.Embed(
            description=f"このBotは <#{allowed_channel_id}> チャンネルでのみ使用できます。",
            color=discord.Color.red(),
        )

    # ------------------------------------------------------------------ #
    #  /google_search
    # ------------------------------------------------------------------ #

    @app_commands.command(name="google_search", description="Google検索 — image / video / AI モードを選択できます")
    @app_commands.describe(
        query="検索キーワード",
        mode="検索モードを選択 (image / video / ai)",
    )
    async def google_search(
        self,
        interaction: discord.Interaction,
        query: str,
        mode: Literal["image", "video", "ai"] = "image",
    ) -> None:
        allowed = get_allowed_channel(interaction.guild_id)
        if allowed and interaction.channel_id != allowed:
            await interaction.response.send_message(embed=self._denied_embed(allowed), ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        if mode == "image":
            results = await search_images(query)
            if not results:
                await interaction.followup.send("検索結果が見つかりませんでした。")
                return
            view = ImagePaginationView(results, query, interaction.user)
            await interaction.followup.send(embed=view.build_embed(), view=view)

        elif mode == "video":
            results, next_token = await search_videos(query)
            if not results:
                await interaction.followup.send("検索結果が見つかりませんでした。")
                return
            view = VideoPaginationView(results, query, interaction.user, next_token)
            await interaction.followup.send(embed=view.build_embed(), view=view)

        elif mode == "ai":
            results = await search_web(query)
            if not results:
                await interaction.followup.send("検索結果が見つかりませんでした。")
                return
            embed = discord.Embed(
                title=f"AI Search: {query}",
                description=(
                    "Google Custom Search から上位結果をまとめました。\n\n"
                    + "\n\n".join(
                        f"**[{r['title']}]({r['url']})**\n{r['snippet']}"
                        for r in results[:5]
                    )
                ),
                color=discord.Color.gold(),
            )
            embed.set_footer(text=f"Searched by {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

    # ------------------------------------------------------------------ #
    #  /google_image
    # ------------------------------------------------------------------ #

    @app_commands.command(name="google_image", description="Google画像検索")
    @app_commands.describe(query="検索キーワード")
    async def google_image(self, interaction: discord.Interaction, query: str) -> None:
        allowed = get_allowed_channel(interaction.guild_id)
        if allowed and interaction.channel_id != allowed:
            await interaction.response.send_message(embed=self._denied_embed(allowed), ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        results = await search_images(query)
        if not results:
            await interaction.followup.send("画像が見つかりませんでした。")
            return
        view = ImagePaginationView(results, query, interaction.user)
        await interaction.followup.send(embed=view.build_embed(), view=view)

    # ------------------------------------------------------------------ #
    #  /google_video
    # ------------------------------------------------------------------ #

    @app_commands.command(name="google_video", description="YouTube動画検索")
    @app_commands.describe(query="検索キーワード")
    async def google_video(self, interaction: discord.Interaction, query: str) -> None:
        allowed = get_allowed_channel(interaction.guild_id)
        if allowed and interaction.channel_id != allowed:
            await interaction.response.send_message(embed=self._denied_embed(allowed), ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        results, next_token = await search_videos(query)
        if not results:
            await interaction.followup.send("動画が見つかりませんでした。")
            return
        view = VideoPaginationView(results, query, interaction.user, next_token)
        await interaction.followup.send(embed=view.build_embed(), view=view)

    # ------------------------------------------------------------------ #
    #  /google_news
    # ------------------------------------------------------------------ #

    @app_commands.command(name="google_news", description="Googleニュース検索")
    @app_commands.describe(query="検索キーワード")
    async def google_news(self, interaction: discord.Interaction, query: str) -> None:
        allowed = get_allowed_channel(interaction.guild_id)
        if allowed and interaction.channel_id != allowed:
            await interaction.response.send_message(embed=self._denied_embed(allowed), ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        results = await search_news(query)
        if not results:
            await interaction.followup.send("ニュースが見つかりませんでした。")
            return
        view = WebListView(results, query, interaction.user, mode="news")
        await interaction.followup.send(embed=view.build_embed(), view=view)

    # ------------------------------------------------------------------ #
    #  /google_web
    # ------------------------------------------------------------------ #

    @app_commands.command(name="google_web", description="Google Web検索")
    @app_commands.describe(query="検索キーワード")
    async def google_web(self, interaction: discord.Interaction, query: str) -> None:
        allowed = get_allowed_channel(interaction.guild_id)
        if allowed and interaction.channel_id != allowed:
            await interaction.response.send_message(embed=self._denied_embed(allowed), ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        results = await search_web(query)
        if not results:
            await interaction.followup.send("検索結果が見つかりませんでした。")
            return
        view = WebListView(results, query, interaction.user, mode="web")
        await interaction.followup.send(embed=view.build_embed(), view=view)
