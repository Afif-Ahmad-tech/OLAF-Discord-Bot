# OLAF Discord Bot

OLAF is a Discord bot built with `discord.js` that:

- supports slash commands
- can answer in chat when mentioned
- has a fixed creator response: `Mr Afif created me`
- can optionally use OpenAI for better answers if `OPENAI_API_KEY` is set

## Features

- `/ping` - simple latency check
- `/help` - shows available commands
- `/ask` - ask OLAF a question
- `/creator` - shows who created OLAF

OLAF also responds in plain chat when someone asks who created it.

## Setup

1. Install Node.js 18 or newer.
2. In this folder, install dependencies:

   ```bash
   npm install
   ```

3. Copy `.env.example` to `.env` and fill in your values.
4. Deploy commands to your server:

   ```bash
   npm run deploy:commands
   ```

5. Start the bot:

   ```bash
   npm start
   ```

## Required Discord Settings

Create a Discord application and bot at the Discord Developer Portal, then add the bot token and application client ID to `.env`.

## Notes

- If `OPENAI_API_KEY` is not set, OLAF will still work, but `/ask` will use a simple fallback response.
- The creator response is hardcoded to: `Mr Afif created me`

## GitHub Ready

This project includes:

- source files
- environment example
- ignore rules
- install and run instructions

