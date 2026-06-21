import { SlashCommandBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('help')
  .setDescription('Show OLAF commands.');

export async function execute(interaction) {
  await interaction.reply({
    content:
      [
        '**OLAF Commands**',
        '/ping - Check bot latency',
        '/help - Show this message',
        '/ask <question> - Ask OLAF a question',
        '/creator - Show who created OLAF'
      ].join('\n'),
    ephemeral: true
  });
}

