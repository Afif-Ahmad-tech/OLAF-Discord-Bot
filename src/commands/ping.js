import { SlashCommandBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('ping')
  .setDescription('Check if OLAF is online.');

export async function execute(interaction) {
  const sent = await interaction.reply({ content: 'Pinging...', fetchReply: true });
  const roundTrip = sent.createdTimestamp - interaction.createdTimestamp;
  await interaction.editReply(`Pong! ${roundTrip}ms`);
}

