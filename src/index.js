import 'dotenv/config';
import { Client, Collection, Events, GatewayIntentBits, Partials } from 'discord.js';
import { commands } from './commands/index.js';

const token = process.env.DISCORD_TOKEN;

if (!token) {
  throw new Error('Missing DISCORD_TOKEN in .env');
}

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ],
  partials: [Partials.Channel]
});

client.commands = new Collection();

for (const command of commands) {
  client.commands.set(command.data.name, command);
}

client.once(Events.ClientReady, readyClient => {
  console.log(`OLAF is online as ${readyClient.user.tag}`);
});

client.on(Events.InteractionCreate, async interaction => {
  if (!interaction.isChatInputCommand()) return;

  const command = client.commands.get(interaction.commandName);
  if (!command) {
    await interaction.reply({ content: 'Unknown command.', ephemeral: true });
    return;
  }

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(`Command failed: ${interaction.commandName}`, error);
    const message = 'There was an error while running that command.';
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({ content: message, ephemeral: true });
    } else {
      await interaction.reply({ content: message, ephemeral: true });
    }
  }
});

client.on(Events.MessageCreate, async message => {
  if (message.author.bot) return;

  const content = message.content.toLowerCase();
  const askedCreator =
    content.includes('who created you') ||
    content.includes('who made you') ||
    content.includes('who created olaf') ||
    content.includes('who made olaf');

  const mentioned = message.mentions.users.has(client.user.id);

  if (askedCreator) {
    await message.reply('Mr Afif created me');
    return;
  }

  if (!mentioned) return;

  const question = message.content.replace(/<@!?\d+>/g, '').trim();
  if (!question) {
    await message.reply('Use `/help` to see my commands.');
    return;
  }

  if (question.toLowerCase().includes('creator') || question.toLowerCase().includes('created')) {
    await message.reply('Mr Afif created me');
    return;
  }

  if (process.env.OPENAI_API_KEY) {
    try {
      const { default: OpenAI } = await import('openai');
      const ai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
      const model = process.env.OPENAI_MODEL || 'gpt-4.1-mini';
      const response = await ai.responses.create({
        model,
        input: [
          {
            role: 'system',
            content:
              'You are OLAF, a helpful Discord bot. Keep answers clear and concise. If asked who created you, say: Mr Afif created me.'
          },
          { role: 'user', content: question }
        ]
      });

      const answer = response.output_text?.trim();
      await message.reply(answer || 'I could not generate a response right now.');
      return;
    } catch (error) {
      console.error('Mention reply failed:', error);
    }
  }

  await message.reply('Ask me with `/ask` or set `OPENAI_API_KEY` for smarter replies.');
});

client.login(token);

