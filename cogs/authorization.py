import os
import json
import requests
import asyncio
import logging
import discord
from discord.ext import commands
from discord.ui import Button, View
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
    try:
        return response.json()
    except json.JSONDecodeError:
        logger.error(f"Failed to decode session ID response: {response.text}")
        return {"error": "Invalid response"}

class Authorization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='authorize')
    async def authorize(self, ctx):
        logger.info("Starting authorization process...")
        request_token = create_request_token()
        if request_token:
            user = ctx.message.author
            logger.info(f"Request token created: {request_token}")
            dm_channel = await user.create_dm()
            auth_url = f"https://www.themoviedb.org/authenticate/{request_token}"

            # Create the view with buttons
            view = View()
            view.add_item(Button(label="Authorize", url=auth_url, style=discord.ButtonStyle.link))
            authorize_button = Button(label="I have authorized", style=discord.ButtonStyle.green)
            view.add_item(authorize_button)

            async def button_callback(interaction):
                if interaction.user != user:
                    await interaction.response.send_message("You cannot use this button.", ephemeral=True)
                    return
                await interaction.response.send_message("Checking authorization status...", ephemeral=True)
                
                session_id_response = create_session_id(request_token)
                if 'session_id' in session_id_response:
                    session_id = session_id_response['session_id']
                    save_session_id(session_id)
                    await dm_channel.send("Authorization complete! Your session ID has been saved securely.")
                    logger.info("Session ID created and saved.")
                elif session_id_response.get('status_code') != 17:
                    await dm_channel.send("An error occurred while creating the session ID. Please try again.")
                    logger.error(f"Failed to create session ID: {session_id_response}")
                else:
                    await dm_channel.send("Authorization timed out. Please try again.")
                    logger.warning("Authorization timed out.")

            authorize_button.callback = button_callback

            await dm_channel.send(
                f"Please visit this URL to authorize the request token: {auth_url}",
                view=view
            )
        else:
            logger.error("Failed to create request token.")
            await ctx.message.author.send("Failed to create request token. Please try again.")

async def setup(bot):
    await bot.add_cog(Authorization(bot))
    logger.info('Authorization cog loaded and command registered.')
