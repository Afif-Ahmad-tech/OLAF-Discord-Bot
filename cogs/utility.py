from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Utility(commands.Cog):
    """OLAF Utility Commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    # --------------------------------------------------
    # PING
    # --------------------------------------------------

    @commands.command(name="ping")
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def ping(self, ctx: commands.Context) -> None:
        """Shows bot latency."""

        latency = round(self.bot.latency * 1000)

        uptime = (
            discord.utils.utcnow() - self.bot.started_at
            if hasattr(self.bot, "started_at")
            else None
        )

        description = f"🏓 **Latency:** `{latency} ms`"

        if uptime:
            description += (
                f"\n⏱️ **Uptime:** "
                f"`{helpers.format_duration(int(uptime.total_seconds()))}`"
            )

        embed = embeds.info(
            self.settings,
            description,
            title="Pong!"
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # SERVER INFO
    # --------------------------------------------------

    @commands.command(
        name="serverinfo",
        aliases=["guildinfo", "server"]
    )
    async def serverinfo(
        self,
        ctx: commands.Context
    ) -> None:

        if ctx.guild is None:
            return

        guild = ctx.guild

        embed = embeds.info(
            self.settings,
            "",
            title=guild.name
        )

        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )

        if guild.banner:
            embed.set_image(
                url=guild.banner.url
            )

        owner = guild.owner.mention if guild.owner else "Unknown"

        embed.add_field(
            name="👑 Owner",
            value=owner,
            inline=True
        )

        embed.add_field(
            name="👥 Members",
            value=str(guild.member_count),
            inline=True
        )

        embed.add_field(
            name="📅 Created",
            value=helpers.format_dt(
                guild.created_at,
                "R",
            ),
            inline=True,
        )

        embed.add_field(
            name="💬 Channels",
            value=(
                f"Text: **{len(guild.text_channels)}**\n"
                f"Voice: **{len(guild.voice_channels)}**\n"
                f"Stage: **{len(guild.stage_channels)}**"
            ),
            inline=True,
        )

        embed.add_field(
            name="🎭 Roles",
            value=str(len(guild.roles)),
            inline=True,
        )

        embed.add_field(
            name="😀 Emojis",
            value=str(len(guild.emojis)),
            inline=True,
        )

        embed.add_field(
            name="🚀 Boosts",
            value=(
                f"Level **{guild.premium_tier}**\n"
                f"Boosts **{guild.premium_subscription_count}**"
            ),
            inline=False,
        )

        if guild.description:
            embed.add_field(
                name="📝 Description",
                value=guild.description,
                inline=False,
            )

        embed.set_footer(
            text=f"Server ID: {guild.id}"
        )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # USER INFO
    # --------------------------------------------------
        @commands.command(name="userinfo", aliases=["whois"])
    async def userinfo(
        self,
        ctx: commands.Context,
        member: discord.Member | None = None,
    ) -> None:

        target = member or ctx.author

        embed = embeds.info(
            self.settings,
            "",
            title=f"{target}",
        )

        embed.set_thumbnail(
            url=target.display_avatar.url
        )

        embed.add_field(
            name="🆔 User ID",
            value=str(target.id),
            inline=False,
        )

        embed.add_field(
            name="📅 Account Created",
            value=helpers.format_dt(
                target.created_at,
                "R",
            ),
            inline=True,
        )

        if isinstance(target, discord.Member):

            embed.add_field(
                name="📥 Joined Server",
                value=helpers.format_dt(
                    target.joined_at,
                    "R",
                ),
                inline=True,
            )

            roles = [
                role.mention
                for role in target.roles
                if role != ctx.guild.default_role
            ]

            if roles:
                embed.add_field(
                    name=f"🎭 Roles ({len(roles)})",
                    value=", ".join(roles[:20]),
                    inline=False,
                )

            embed.add_field(
                name="⭐ Top Role",
                value=target.top_role.mention,
                inline=True,
            )

            embed.add_field(
                name="🤖 Bot",
                value="Yes" if target.bot else "No",
                inline=True,
            )

            embed.add_field(
                name="🟢 Status",
                value=str(target.status).title(),
                inline=True,
            )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # AVATAR
    # --------------------------------------------------

    @commands.command(
        name="avatar",
        aliases=["pfp", "icon"]
    )
    async def avatar(
        self,
        ctx: commands.Context,
        member: discord.Member | None = None,
    ) -> None:

        target = member or ctx.author

        embed = embeds.info(
            self.settings,
            f"[Click here to open avatar]({target.display_avatar.url})",
            title=f"{target.display_name}'s Avatar",
        )

        embed.set_image(
            url=target.display_avatar.url
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # MEMBER COUNT
    # --------------------------------------------------

    @commands.command(name="members")
    async def members(
        self,
        ctx: commands.Context,
    ) -> None:

        if ctx.guild is None:
            return

        guild = ctx.guild

        humans = sum(
            not member.bot
            for member in guild.members
        )

        bots = sum(
            member.bot
            for member in guild.members
        )

        online = sum(
            member.status != discord.Status.offline
            for member in guild.members
        )

        embed = embeds.info(
            self.settings,
            (
                f"👥 **Total Members:** {guild.member_count}\n"
                f"🧑 **Humans:** {humans}\n"
                f"🤖 **Bots:** {bots}\n"
                f"🟢 **Online:** {online}"
            ),
            title="Member Statistics",
        )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # SAY
    # --------------------------------------------------

    @commands.command(name="say")
    @commands.has_permissions(
        manage_messages=True
    )
    async def say(
        self,
        ctx: commands.Context,
        *,
        message: str,
    ) -> None:

        try:
            await ctx.message.delete()
        except (
            discord.Forbidden,
            discord.HTTPException,
        ):
            pass

        embed = embeds.info(
            self.settings,
            message,
        )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # HELP COMMAND
    # --------------------------------------------------
        @commands.command(name="help")
    async def help_cmd(
        self,
        ctx: commands.Context,
    ) -> None:

        prefix = (
            self.data.get_setting(
                ctx.guild.id,
                "prefix",
                self.settings.prefix,
            )
            if ctx.guild
            else self.settings.prefix
        )

        embed = embeds.info(
            self.settings,
            "",
            title=f"{self.settings.bot_name} Help",
        )

        embed.description = (
            f"Use `{prefix}` before commands.\n\n"
            "**Available Categories**\n"
            "🛡️ Moderation\n"
            "👋 Welcome\n"
            "🛠️ Utility\n"
            "🎮 Fun\n"
            "📊 Polls\n"
            "⭐ Leveling\n"
            "⏰ Reminders\n"
            "⚙️ Configuration\n"
            "📝 Logging"
        )

        for cog_name, cog in sorted(self.bot.cogs.items()):

            commands_list = [
                f"`{prefix}{command.name}`"
                for command in cog.get_commands()
                if not command.hidden
            ]

            if not commands_list:
                continue

            embed.add_field(
                name=f"📂 {cog_name}",
                value="\n".join(commands_list[:10]),
                inline=False,
            )

        embed.set_footer(
            text=f"{self.settings.bot_name} • {self.settings.version}"
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # SLASH HELP
    # --------------------------------------------------

    @app_commands.command(
        name="help",
        description="Shows all available OLAF commands.",
    )
    async def slash_help(
        self,
        interaction: discord.Interaction,
    ) -> None:

        prefix = (
            self.data.get_setting(
                interaction.guild.id,
                "prefix",
                self.settings.prefix,
            )
            if interaction.guild
            else self.settings.prefix
        )

        embed = discord.Embed(
            title=f"🤖 {self.settings.bot_name} Help",
            description=(
                "## 📚 Available Categories\n\n"
                "🛡️ **Moderation**\n"
                "👋 **Welcome**\n"
                "🛠️ **Utility**\n"
                "🎮 **Fun**\n"
                "📊 **Polls**\n"
                "⭐ **Leveling**\n"
                "⏰ **Reminders**\n"
                "⚙️ **Configuration**\n"
                "📝 **Logging**"
            ),
            color=self.settings.embed_color,
        )

        embed.add_field(
            name="💬 Prefix Commands",
            value=f"`{prefix}help`",
            inline=False,
        )

        slash_commands = []

        for command in self.bot.tree.walk_commands():
            slash_commands.append(f"`/{command.qualified_name}`")

        if slash_commands:

            embed.add_field(
                name="⚡ Slash Commands",
                value="\n".join(slash_commands[:20]),
                inline=False,
            )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.set_footer(
            text=f"{self.settings.bot_name} • Version {self.settings.version}"
        )

        await interaction.response.send_message(
            embed=embed
        )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Utility(bot)
    )