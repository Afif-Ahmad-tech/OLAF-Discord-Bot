from __future__ import annotations

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds


class ServerConfig(commands.Cog):
    """Top-level settings: prefix, mod-log channel, clearing data."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    @commands.group(name="config", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def config_group(self, ctx: commands.Context) -> None:
        embed = embeds.info(
            self.settings,
            "Subcommands: prefix, modlog, show, reset",
            title="Server configuration",
        )
        await ctx.send(embed=embed)

    @config_group.command(name="prefix")
    @commands.has_permissions(administrator=True)
    async def config_prefix(self, ctx: commands.Context, prefix: str | None = None) -> None:
        if prefix is None:
            current = self.data.get_setting(ctx.guild.id, "prefix", self.settings.prefix)
            await ctx.send(embed=embeds.info(self.settings, f"Current prefix: {current}", title="Prefix"))
            return
        if len(prefix) > 5:
            await ctx.send(embed=embeds.error(self.settings, "Keep the prefix under 5 characters."))
            return
        self.data.set_setting(ctx.guild.id, "prefix", prefix)
        await ctx.send(embed=embeds.success(self.settings, f"Prefix updated to {prefix}. Mentioning me still works."))

    @config_group.command(name="modlog")
    @commands.has_permissions(administrator=True)
    async def config_modlog(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        self.data.set_setting(ctx.guild.id, "mod_log", channel.id)
        await ctx.send(embed=embeds.success(self.settings, f"Mod-log channel set to {channel.mention}."))

    @config_group.command(name="show")
    async def config_show(self, ctx: commands.Context) -> None:
        prefix = self.data.get_setting(ctx.guild.id, "prefix", self.settings.prefix)
        mod_log_id = self.data.get_setting(ctx.guild.id, "mod_log")
        log_id = self.data.get_setting(ctx.guild.id, "log_channel")
        welcome_id = self.data.get_setting(ctx.guild.id, "welcome_channel")
        auto_role_id = self.data.get_setting(ctx.guild.id, "auto_role")
        level_channel_id = self.data.get_setting(ctx.guild.id, "level_channel")

        mod_log = ctx.guild.get_channel(mod_log_id) if mod_log_id else None
        log_ch = ctx.guild.get_channel(log_id) if log_id else None
        welcome_ch = ctx.guild.get_channel(welcome_id) if welcome_id else None
        auto_role = ctx.guild.get_role(auto_role_id) if auto_role_id else None
        level_ch = ctx.guild.get_channel(level_channel_id) if level_channel_id else None

        description = (
            f"Prefix: {prefix}\n"
            f"Mod log: {mod_log.mention if mod_log else 'not set'}\n"
            f"Event log: {log_ch.mention if log_ch else 'not set'}\n"
            f"Welcome channel: {welcome_ch.mention if welcome_ch else 'not set'}\n"
            f"Auto-role: {auto_role.mention if auto_role else 'not set'}\n"
            f"Level-up channel: {level_ch.mention if level_ch else 'fallback to original channel'}"
        )
        await ctx.send(embed=embeds.info(self.settings, description, title=f"{ctx.guild.name} configuration"))

    @config_group.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def config_reset(self, ctx: commands.Context) -> None:
        self.data.clear_guild(ctx.guild.id)
        await ctx.send(embed=embeds.success(self.settings, "Cleared all OLAF settings, warnings, levels, and reminders for this server."))

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=embeds.error(self.settings, "You need the Administrator permission for that."))
            return
        await ctx.send(embed=embeds.error(self.settings, f"Something went wrong: {error}"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ServerConfig(bot))
