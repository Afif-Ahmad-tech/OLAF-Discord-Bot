import { SlashCommandBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('creator')
  .setDescription('Show who created OLAF.');

export async function execute(interaction) {
  await interaction.reply('Mr Afif created me');
}

