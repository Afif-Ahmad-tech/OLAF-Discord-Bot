from __future__ import annotations

import io

import discord
from discord.ext import commands
from discord import app_commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Utility(commands.Cog):
    """Generic utilities: ping, serverinfo, userinfo, avatar, say."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    @commands.command(name="ping")
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def ping(self, ctx: commands.Context) -> None:
        latency_ms = round(self.bot.latency * 1000)
        uptime = discord.utils.utcnow() - self.bot.started_at
        embed = embeds.info(self.settings, f"Latency: **{latency_ms} ms**\nUptime: **{helpers.format_duration(int(uptime.total_seconds()))}**", title="Pong")
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo", aliases=["guildinfo"])
    async def serverinfo(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        if not guild:
            return
        embed = embeds.info(self.settings, "", title=guild.name)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "unknown", inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Created", value=helpers.format_dt(guild.created_at, "R"), inline=True)
        embed.add_field(
            name="Channels",
            value=f"{len(guild.text_channels)} text · {len(guild.voice_channels)} voice · {len(guild.stage_channels)} stage",
            inline=False,
        )
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Emoji", value=str(len(guild.emojis)), inline=True)
        embed.add_field(name="Boosts", value=f"Level {guild.premium_tier} · {guild.premium_subscription_count}", inline=True)
        if guild.description:
            embed.add_field(name="Description", value=guild.description, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo")
    async def userinfo(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        target = member or ctx.author
        roles = [r.mention for r in target.roles if r != ctx.guild.default_role] if isinstance(target, discord.Member) else []
        description = "\n".join(
            [
                f"ID: {target.id}",
                f"Joined: {helpers.format_dt(getattr(target, 'joined_at', None), 'R')}",
                f"Created: {helpers.format_dt(target.created_at, 'R')}",
            ]
        )
        embed = embeds.info(self.settings, description, title=str(target))
        embed.set_thumbnail(url=target.display_avatar.url)
        if roles:
            embed.add_field(name=f"Roles ({len(roles)})", value=", ".join(roles[:15]) + ("…" if len(roles) > 15 else ""), inline=False)
        if isinstance(target, discord.Member):
            embed.add_field(name="Top role", value=target.top_role.mention, inline=True)
            embed.add_field(name="Status", value=str(target.status).title(), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        target = member or ctx.author
        embed = embeds.info(self.settings, f"[Open in browser]({target.display_avatar.url})", title=f"{target.display_name}'s avatar")
        embed.set_image(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="members")
    async def members(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        if not guild:
            return
        online = sum(1 for m in guild.members if m.status != discord.Status.offline)
        humans = sum(1 for m in guild.members if not m.bot)
        bots = sum(1 for m in guild.members if m.bot)
        embed = embeds.info(
            self.settings,
            f"Total: **{guild.member_count}**\nHumans: **{humans}**\nBots: **{bots}**\nOnline-ish: **{online}**",
            title=f"{guild.name} member stats",
        )
        await ctx.send(embed=embed)

    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, *, message: str) -> None:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        embed = embeds.info(self.settings, message)
        await ctx.send(embed=embed)

    @commands.command(name="help")
    async def help_cmd(self, ctx: commands.Context) -> None:
        prefix = self.data.get_setting(ctx.guild.id, "prefix", self.settings.prefix) if ctx.guild else self.settings.prefix
        embed = embeds.info(self.settings, "", title=f"{self.settings.bot_name} help")
        embed.description = (
            f"Use {prefix}command or mention me. Categories: **moderation**, **welcome**, "
            "**utility**, **fun**, **polls**, **leveling**, **reminders**, **config**, **logging**."
        )
        for cog_name, cog in self.bot.cogs.items():
            shown = [f"{prefix}{cmd.name}" for cmd in cog.get_commands() if not cmd.hidden][:6]
            if shown:
                embed.add_field(
                    name=f"📂 {cog_name}",
                    value="\n".join(f"`{cmd}`" for cmd in shown),
                    inline=False,
                )
        embed.set_footer(text=f"Tip: run {prefix}help <command> on individual cogs for details.")
        await ctx.send(embed=embed)

    @app_commands.command(
    name="help",
    description="Shows all available OLAF commands."
)
async def slash_help(self, interaction: discord.Interaction):
    prefix = self.data.get_setting(
        interaction.guild.id,
        "prefix",
        self.settings.prefix,
    ) if interaction.guild else self.settings.prefix

    embed = discord.Embed(
        title=f"🤖 {self.settings.bot_name} Help",
        description=(
            "## 📚 Available Categories\n\n"
            "🛡️ **Moderation**\n"
            "👋 **Welcome**\n"
            "🛠️ **Utility**\n"
            "🎉 **Fun**\n"
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
        value=f"Use `{prefix}help` for text commands.",
        inline=False,
    )

    embed.add_field(
        name="⚡ Slash Commands",
        value="Type **/** to view all slash commands.",
        inline=False,
    )

    embed.set_footer(
        text=f"{self.settings.bot_name} • Version {self.settings.version}"
    )

    if self.bot.user:
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)