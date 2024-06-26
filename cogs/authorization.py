import os
import json
import requests
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TMDB_TOKEN = os.getenv('TMDB_TOKEN')
SESSION_FILE = 'tmdb_session.json'
logger = logging.getLogger(__name__)

def save_session_id(session_id):
    with open(SESSION_FILE, 'w') as f:
        json.dump({'session_id': session_id}, f)

def load_session_id():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get('session_id')
    return None

def create_request_token():
    url = 'https://api.themoviedb.org/3/authentication/token/new'
    headers = {
        'Authorization': f'Bearer {TMDB_TOKEN}',
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('request_token')
    else:
        logger.error(f"Failed to create request token: {response.status_code} - {response.text}")
        return None

def create_session_id(request_token):
    url = 'https://api.themoviedb.org/3/authentication/session/new'
    headers = {
        'Authorization': f'Bearer {TMDB_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'request_token': request_token
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('session_id')
    else:
        logger.error(f"Failed to create session ID: {response.status_code} - {response.text}")
        return None

class Authorization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='authorize')
    async def authorize(self, ctx):
        request_token = create_request_token()
        if request_token:
            auth_url = f"https://www.themoviedb.org/authenticate/{request_token}"
            link_message = await ctx.send(f"Please visit this URL to authorize the request token: {auth_url}")
            confirmation_message = await ctx.send("After authorization, react to this message with ✅ to complete the process.")
            await confirmation_message.add_reaction('✅')

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == '✅' and reaction.message.id == confirmation_message.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=600.0, check=check)  # Wait for up to 10 minutes
                session_id = create_session_id(request_token)
                if session_id:
                    save_session_id(session_id)
                    await ctx.send("Authorization complete! Your session ID has been saved securely.")
                    await confirmation_message.clear_reaction('✅')
                    await link_message.delete()
                    await confirmation_message.delete()
                else:
                    await ctx.send("Failed to create session ID. Please try again.")
            except asyncio.TimeoutError:
                await ctx.send("Authorization timed out. Please try again.")
        else:
            await ctx.send("Failed to create request token. Please try again.")

async def setup(bot):
    await bot.add_cog(Authorization(bot))
    logger.info('Authorization cog loaded and command registered.')
