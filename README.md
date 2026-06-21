# OLAF Discord Bot

A modular Discord bot named **OLAF** that handles moderation, welcomes, leveling, fun
commands, polls, reminders, and event logging once it's invited to your server.

## Features

- **Moderation**: kick, ban, unban, mute/unmute, purge, warn, lock/unlock, auto-timeout after 3 warnings.
- **Welcome**: customizable greeting templates, automatic role assignment, leave messages.
- **Event logging**: edits, deletions, joins, leaves, all routed to a single log channel.
- **Utility**: ping, serverinfo, userinfo, avatar, member counts, help, say-as-embed.
- **Fun**: 8-ball, dice, coinflip, choose, rock-paper-scissors, jokes, ratings.
- **Polls**: structured multi-option polls and quick yes/no/maybe polls.
- **Leveling**: XP on chat, level-up notifications, rank card, leaderboard.
- **Reminders**: personal !remind with s/m/h/d durations, list, and cancel.
- **Per-server config**: custom prefix, mod-log channel, auto-role, level channel.
- **Data persistence**: JSON file in data/bot_data.json; nothing leaves your machine.

## Project layout

`
OLAF discord bot/
+- bot.py              # entry point
+- config.py           # environment-driven settings
+- requirements.txt
+- .env.example        # copy to .env and fill in your token
+- data/
¦  +- manager.py       # JSON-backed store
+- utils/
¦  +- helpers.py
¦  +- embeds.py
+- cogs/
   +- moderation.py
   +- welcome.py
   +- utility.py
   +- fun.py
   +- polls.py
   +- logging.py
   +- leveling.py
   +- reminders.py
   +- config_cog.py
`

## Setup

### 1. Create the Discord application

1. Visit https://discord.com/developers/applications and click **New Application**.
2. Name it OLAF, accept the terms, then open **Bot** in the sidebar.
3. Click **Reset Token**, copy the token, and store it somewhere safe.
4. Under **Privileged Gateway Intents**, enable **Server Members Intent** and **Message Content Intent**.
5. Open **OAuth2 ? URL Generator**:
   - Scopes: ot, pplications.commands
   - Bot permissions: Administrator (or pick the granular permissions you want).
6. Copy the generated URL and paste it in a browser to invite OLAF to your server.

### 2. Install Python dependencies

Requires Python 3.10 or newer.

`ash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
`

### 3. Configure environment

Copy .env.example to .env and fill in the values:

`env
DISCORD_TOKEN=your-bot-token-here
BOT_OWNER_ID=your-discord-user-id
BOT_PREFIX=!
`

### 4. Run the bot

`ash
python bot.py
`

The first run creates data/bot_data.json automatically. Keep this file safe; it stores
warnings, levels, reminders, and per-guild settings.

## Command reference

Default prefix is ! (overridable per server with !config prefix <value> or by mentioning OLAF).

| Category | Commands |
| --- | --- |
| Moderation | !kick @user, !ban @user, !unban <id>, !mute @user 30m, !unmute @user, !purge 25, !warn @user reason, !warnings @user, !clearwarnings @user, !lock, !unlock |
| Welcome | !welcome channel #lobby, !welcome message Hello {mention}!, !welcome autorole @Member, !welcome show, !welcome disable |
| Utility | !ping, !serverinfo, !userinfo @user, !avatar @user, !members, !say, !help |
| Fun | !8ball, !roll 2d20, !coinflip, !choose a | b | c, !rps rock, !joke, !rate Olaf |
| Polls | !poll Lunch? | Pizza | Sushi | Tacos, !quickpoll Should we merge? |
| Leveling | !rank, !leaderboard, !leveling toggle, !leveling channel #levels |
| Reminders | !remind 30m Stretch, !reminders, !cancelremind 3 |
| Logs | !logs channel #mod-log, !logs show, !logs disable |
| Config | !config prefix, !config prefix ?, !config modlog #mod-log, !config show, !config reset |

## Permissions OLAF needs

| Permission | Why |
| --- | --- |
| Manage Roles | auto-role, mute role interactions |
| Kick Members | !kick |
| Ban Members | !ban / !unban |
| Moderate Members | !mute / !unmute (timeouts) |
| Manage Messages | !purge, !say cleanup |
| Manage Channels | !lock / !unlock |
| Send Messages / Embed Links / Read Message History | everything |

Grant **Administrator** for the smoothest experience, or the granular list above.

## Notes

- Wipe data/bot_data.json to reset every server.
- The bot stores data locally only — there is no external database.
- Reminders persist across restarts because they are persisted in the same JSON file.
