from __future__ import annotations

import platform
from datetime import timedelta

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Utility(commands.Cog):
    """OLAF Utility Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    # ----------------------------------------------------
    # HELP
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="help",
        description="Shows every available command."
    )
    async def help(
        self,
        ctx: commands.Context,
    ):

        prefix = (
            self.data.get_setting(
                ctx.guild.id,
                "prefix",
                self.settings.prefix,
            )
            if ctx.guild
            else self.settings.prefix
        )

        embed = discord.Embed(
            title=f"🤖 {self.settings.bot_name}",
            description="Professional Discord Management Bot",
            color=self.settings.embed_color,
        )

        embed.add_field(
            name="🛠 Utility",
            value=(
                f"`{prefix}ping`\n"
                f"`{prefix}userinfo`\n"
                f"`{prefix}serverinfo`\n"
                f"`{prefix}avatar`\n"
                f"`{prefix}members`\n"
                f"`{prefix}uptime`\n"
                f"`{prefix}botinfo`"
            ),
            inline=True,
        )

        embed.add_field(
            name="🛡 Moderation",
            value=(
                "Kick\n"
                "Ban\n"
                "Mute\n"
                "Warn\n"
                "Clear"
            ),
            inline=True,
        )

        embed.add_field(
            name="🎉 Fun",
            value=(
                "Polls\n"
                "Reminders\n"
                "More coming soon..."
            ),
            inline=False,
        )

        embed.set_footer(
            text=f"Version {self.settings.version}"
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # PING
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="ping",
        description="Shows bot latency."
    )
    async def ping(
        self,
        ctx: commands.Context,
    ):

        latency = round(self.bot.latency * 1000)

        uptime = discord.utils.utcnow() - self.bot.started_at

        embed = embeds.success(
            self.settings,
            (
                f"🏓 **Latency:** `{latency} ms`\n"
                f"⏰ **Uptime:** `{helpers.format_duration(int(uptime.total_seconds()))}`"
            ),
            title="Pong!"
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        await ctx.send(embed=embed)
            # ----------------------------------------------------
    # USER INFO
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="userinfo",
        description="Shows information about a user."
    )
    async def userinfo(
        self,
        ctx: commands.Context,
        member: discord.Member | None = None,
    ):

        member = member or ctx.author

        embed = discord.Embed(
            title=f"👤 {member}",
            color=self.settings.embed_color,
            timestamp=discord.utils.utcnow(),
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="🆔 User ID",
            value=str(member.id),
            inline=True,
        )

        embed.add_field(
            name="🤖 Bot",
            value="Yes" if member.bot else "No",
            inline=True,
        )

        embed.add_field(
            name="🎭 Top Role",
            value=member.top_role.mention,
            inline=True,
        )

        if member.joined_at:
            embed.add_field(
                name="📥 Joined Server",
                value=helpers.format_dt(member.joined_at, "R"),
                inline=False,
            )

        embed.add_field(
            name="📅 Discord Account",
            value=helpers.format_dt(member.created_at, "R"),
            inline=False,
        )

        roles = [r.mention for r in member.roles if r != ctx.guild.default_role]

        if roles:
            embed.add_field(
                name=f"🎖 Roles ({len(roles)})",
                value=", ".join(roles[:15]) + ("..." if len(roles) > 15 else ""),
                inline=False,
            )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # SERVER INFO
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="serverinfo",
        aliases=["guildinfo"],
        description="Shows server information."
    )
    async def serverinfo(
        self,
        ctx: commands.Context,
    ):

        guild = ctx.guild

        if guild is None:
            return

        embed = discord.Embed(
            title=f"🏠 {guild.name}",
            color=self.settings.embed_color,
            timestamp=discord.utils.utcnow(),
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.add_field(
            name="👑 Owner",
            value=guild.owner.mention if guild.owner else "Unknown",
            inline=True,
        )

        embed.add_field(
            name="👥 Members",
            value=str(guild.member_count),
            inline=True,
        )

        embed.add_field(
            name="🎭 Roles",
            value=str(len(guild.roles)),
            inline=True,
        )

        embed.add_field(
            name="💬 Text Channels",
            value=str(len(guild.text_channels)),
            inline=True,
        )

        embed.add_field(
            name="🔊 Voice Channels",
            value=str(len(guild.voice_channels)),
            inline=True,
        )

        embed.add_field(
            name="😀 Emojis",
            value=str(len(guild.emojis)),
            inline=True,
        )

        embed.add_field(
            name="🚀 Boost Level",
            value=f"Level {guild.premium_tier}",
            inline=True,
        )

        embed.add_field(
            name="✨ Boosts",
            value=str(guild.premium_subscription_count),
            inline=True,
        )

        embed.add_field(
            name="📅 Created",
            value=helpers.format_dt(guild.created_at, "R"),
            inline=False,
        )

        embed.set_footer(
            text=f"Server ID: {guild.id}"
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # AVATAR
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="avatar",
        description="Shows a user's avatar."
    )
    async def avatar(
        self,
        ctx: commands.Context,
        member: discord.Member | None = None,
    ):

        member = member or ctx.author

        embed = discord.Embed(
            title=f"🖼 {member.display_name}'s Avatar",
            color=self.settings.embed_color,
        )

        embed.set_image(url=member.display_avatar.url)

        embed.description = (
            f"[🔗 Open Original]({member.display_avatar.url})"
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # MEMBER COUNT
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="members",
        description="Shows server member statistics."
    )
    async def members(
        self,
        ctx: commands.Context,
    ):

        guild = ctx.guild

        if guild is None:
            return

        humans = sum(not m.bot for m in guild.members)
        bots = sum(m.bot for m in guild.members)
        online = sum(
            m.status != discord.Status.offline
            for m in guild.members
        )

        embed = discord.Embed(
            title="👥 Member Statistics",
            color=self.settings.embed_color,
        )

        embed.add_field(
            name="Total Members",
            value=str(guild.member_count),
        )

        embed.add_field(
            name="Humans",
            value=str(humans),
        )

        embed.add_field(
            name="Bots",
            value=str(bots),
        )

        embed.add_field(
            name="Online",
            value=str(online),
        )

        await ctx.send(embed=embed)
            # ----------------------------------------------------
    # BOT INFO
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="botinfo",
        description="Shows information about OLAF."
    )
    async def botinfo(
        self,
        ctx: commands.Context,
    ):

        guilds = len(self.bot.guilds)
        users = sum(g.member_count or 0 for g in self.bot.guilds)

        uptime = discord.utils.utcnow() - self.bot.started_at

        embed = discord.Embed(
            title=f"🤖 {self.settings.bot_name}",
            description="Professional Discord Management Bot",
            color=self.settings.embed_color,
            timestamp=discord.utils.utcnow(),
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.add_field(
            name="🏠 Servers",
            value=str(guilds),
            inline=True,
        )

        embed.add_field(
            name="👥 Users",
            value=f"{users:,}",
            inline=True,
        )

        embed.add_field(
            name="🏓 Latency",
            value=f"{round(self.bot.latency * 1000)} ms",
            inline=True,
        )

        embed.add_field(
            name="🐍 Python",
            value=platform.python_version(),
            inline=True,
        )

        embed.add_field(
            name="📦 discord.py",
            value=discord.__version__,
            inline=True,
        )

        embed.add_field(
            name="⏰ Uptime",
            value=helpers.format_duration(
                int(uptime.total_seconds())
            ),
            inline=True,
        )

        embed.add_field(
            name="📌 Version",
            value=self.settings.version,
            inline=True,
        )

        embed.set_footer(
            text="OLAF v2"
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # UPTIME
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="uptime",
        description="Shows how long the bot has been online."
    )
    async def uptime(
        self,
        ctx: commands.Context,
    ):

        delta = discord.utils.utcnow() - self.bot.started_at

        embed = embeds.success(
            self.settings,
            f"⏰ **{helpers.format_duration(int(delta.total_seconds()))}**",
            title="Bot Uptime"
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # SAY
    # ----------------------------------------------------

    @commands.hybrid_command(
        name="say",
        description="Make OLAF say something."
    )
    @commands.has_permissions(manage_messages=True)
    async def say(
        self,
        ctx: commands.Context,
        *,
        message: str,
    ):

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, AttributeError):
            pass

        embed = discord.Embed(
            description=message,
            color=self.settings.embed_color,
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # ERROR HANDLER
    # ----------------------------------------------------

    async def cog_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ):

        if isinstance(error, commands.MissingPermissions):

            await ctx.send(
                embed=embeds.error(
                    self.settings,
                    "❌ You don't have permission to use this command."
                )
            )
            return

        if isinstance(error, commands.CommandOnCooldown):

            await ctx.send(
                embed=embeds.warning(
                    self.settings,
                    f"⏳ Try again in **{error.retry_after:.1f} seconds**."
                )
            )
            return

        if isinstance(error, commands.BadArgument):

            await ctx.send(
                embed=embeds.error(
                    self.settings,
                    "❌ Invalid command arguments."
                )
            )
            return

        raise error


async def setup(bot: commands.Bot):

    await bot.add_cog(
        Utility(bot)
    )