import 'dotenv/config';
import { REST, Routes } from 'discord.js';
import { commands } from './commands/index.js';

const token = process.env.DISCORD_TOKEN;
const clientId = process.env.CLIENT_ID;
const guildId = process.env.GUILD_ID;

if (!token || !clientId || !guildId) {
  throw new Error('Missing DISCORD_TOKEN, CLIENT_ID, or GUILD_ID in .env');
}

const body = commands.map(command => command.data.toJSON());
const rest = new REST({ version: '10' }).setToken(token);

async function main() {
  await rest.put(Routes.applicationGuildCommands(clientId, guildId), { body });
  console.log(`Registered ${body.length} guild commands.`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

