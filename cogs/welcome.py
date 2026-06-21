from __future__ import annotations

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Welcome(commands.Cog):
    """Sends greetings and applies an auto-role when members join."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        # Auto role
        role_id = self.data.get_setting(member.guild.id, "auto_role")
        if role_id:
            role = member.guild.get_role(role_id)
            if role is not None:
                try:
                    await member.add_roles(role, reason="OLAF auto-role")
                except discord.Forbidden:
                    pass

        # Welcome message
        channel_id = self.data.get_setting(member.guild.id, "welcome_channel")
        template = self.data.get_setting(member.guild.id, "welcome_message") or (
            "Welcome to **{server}**, {mention}! We're glad to have you. (member #{count})"
        )
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if channel is None:
            return
        message = template.format(
            server=member.guild.name,
            mention=member.mention,
            user=member.display_name,
            count=member.guild.member_count,
        )
        embed = embeds.info(self.settings, message, title=f"Welcome, {member.display_name}!")
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        channel_id = self.data.get_setting(member.guild.id, "welcome_channel")
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if channel is None:
            return
        embed = embeds.info(
            self.settings,
            f"{member.display_name} just left the server. We now have {member.guild.member_count} members.",
            title="Goodbye",
        )
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.group(name="welcome", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx: commands.Context) -> None:
        embed = embeds.info(
            self.settings,
            "Subcommands: channel, message, utorole, show, disable",
            title="Welcome settings",
        )
        await ctx.send(embed=embed)

    @welcome.command(name="channel")
    @commands.has_permissions(manage_guild=True)
    async def welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        self.data.set_setting(ctx.guild.id, "welcome_channel", channel.id)
        await ctx.send(embed=embeds.success(self.settings, f"Welcome messages will now be sent to {channel.mention}."))

    @welcome.command(name="message")
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self, ctx: commands.Context, *, template: str) -> None:
        if len(template) > 800:
            await ctx.send(embed=embeds.error(self.settings, "Keep the template under 800 characters."))
            return
        self.data.set_setting(ctx.guild.id, "welcome_message", template)
        await ctx.send(embed=embeds.success(self.settings, "Welcome message template updated. Placeholders: {server}, {mention}, {user}, {count}."))

    @welcome.command(name="autorole")
    @commands.has_permissions(manage_guild=True)
    async def welcome_autorole(self, ctx: commands.Context, role: discord.Role) -> None:
        if role >= ctx.guild.me.top_role:
            await ctx.send(embed=embeds.error(self.settings, "Pick a role lower than my top role."))
            return
        self.data.set_setting(ctx.guild.id, "auto_role", role.id)
        await ctx.send(embed=embeds.success(self.settings, f"New members will receive {role.mention}."))

    @welcome.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def welcome_disable(self, ctx: commands.Context) -> None:
        self.data.set_setting(ctx.guild.id, "welcome_channel", None)
        self.data.set_setting(ctx.guild.id, "auto_role", None)
        await ctx.send(embed=embeds.success(self.settings, "Welcome channel and auto-role disabled."))

    @welcome.command(name="show")
    async def welcome_show(self, ctx: commands.Context) -> None:
        channel_id = self.data.get_setting(ctx.guild.id, "welcome_channel")
        role_id = self.data.get_setting(ctx.guild.id, "auto_role")
        message = self.data.get_setting(ctx.guild.id, "welcome_message") or "(default)"
        channel = ctx.guild.get_channel(channel_id) if channel_id else None
        role = ctx.guild.get_role(role_id) if role_id else None
        description = (
            f"Channel: {channel.mention if channel else 'not set'}\n"
            f"Auto-role: {role.mention if role else 'not set'}\n"
            f"Message:\n{helpers.truncate(message, 800)}"
        )
        embed = embeds.info(self.settings, description, title="Current welcome setup")
        await ctx.send(embed=embed)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=embeds.error(self.settings, "You need the Manage Server permission for that."))
            return
        await ctx.send(embed=embeds.error(self.settings, f"Something went wrong: {error}"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
