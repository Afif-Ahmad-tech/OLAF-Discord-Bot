import { SlashCommandBuilder } from 'discord.js';
import OpenAI from 'openai';

const client = process.env.OPENAI_API_KEY ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY }) : null;

export const data = new SlashCommandBuilder()
  .setName('ask')
  .setDescription('Ask OLAF a question.')
  .addStringOption(option =>
    option
      .setName('question')
      .setDescription('Your question')
      .setRequired(true)
  );

async function getOpenAIAnswer(question) {
  if (!client) return null;

  const model = process.env.OPENAI_MODEL || 'gpt-4.1-mini';
  const response = await client.responses.create({
    model,
    input: [
      {
        role: 'system',
        content:
          'You are OLAF, a helpful Discord bot. Be concise, accurate, and friendly. If asked who created you, say: Mr Afif created me.'
      },
      { role: 'user', content: question }
    ]
  });

  const text = response.output_text?.trim();
  return text || null;
}

export async function execute(interaction) {
  const question = interaction.options.getString('question', true);

  if (question.toLowerCase().includes('who created you') || question.toLowerCase().includes('who made you')) {
    await interaction.reply('Mr Afif created me');
    return;
  }

  await interaction.deferReply();

  try {
    const answer = await getOpenAIAnswer(question);
    if (answer) {
      await interaction.editReply(answer);
      return;
    }

    await interaction.editReply(
      'I can answer basic questions right now. Set `OPENAI_API_KEY` in `.env` to enable full AI responses.'
    );
  } catch (error) {
    console.error('Ask command failed:', error);
    await interaction.editReply('I had trouble answering that right now.');
  }
}

