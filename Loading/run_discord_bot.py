import discord
from discord.ext import commands
import csv
from dotenv import load_dotenv
import os

# load token variable
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def fetch_and_save(ctx, channel_id: int, limit: int = 100):
    """Fetches the last `limit` messages from a channel and saves them to a CSV file."""
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("Channel not found!")
        return

    messages = [message async for message in channel.history(limit=limit)]

    # prepare data for CSV
    message_data = [
        {"author": str(msg.author), "content": msg.content, "timestamp": msg.created_at}
        for msg in messages
    ]

    # define CSV export path
    csv_file = "data/messages.csv"

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["author", "content", "timestamp"])
        writer.writeheader()  
        writer.writerows(message_data)  

    await ctx.send(f"Fetched {len(messages)} messages and saved to {csv_file}!")

# run the bot
bot.run(TOKEN)
