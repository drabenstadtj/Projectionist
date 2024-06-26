import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the intents
intents = discord.Intents.default()
intents.message_content = True

# Define the bot's command prefix (e.g., '!')
bot = commands.Bot(command_prefix='!', intents=intents)

# Import the setup function from cogs
from cogs import setup_cogs

# Load cogs
setup_cogs(bot)

# Event: When the bot is ready
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

# Run the bot with your token
bot.run(TOKEN)
