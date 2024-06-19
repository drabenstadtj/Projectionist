import os
import random
import requests
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables from .env file
load_dotenv()

# Get the bot token, TMDB key, and session ID from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
TMDB_KEY = os.getenv('TMDB_KEY')
TMDB_SESSION_ID = os.getenv('TMDB_SESSION_ID')
TMDB_TOKEN = os.getenv('TMDB_TOKEN')
TMDB_LIST_ID = '8303899'  # Replace with your TMDB account ID

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the intents
intents = discord.Intents.default()
intents.message_content = True

# Define the bot's command prefix (e.g., '!')
bot = commands.Bot(command_prefix='!', intents=intents)

# TMDB API URLs
TMDB_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/original"

# Event: When the bot is ready
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

def fetch_tmdb_list():
    url = f"{TMDB_URL}/list/{TMDB_LIST_ID}?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        logger.info("Fetched TMDB list successfully.")
        return data['items']
    else:
        logger.error(f"Failed to fetch TMDB list: {response.status_code} - {response.text}")
        return []

def get_movie_details(movie_id):
    url = f"{TMDB_URL}/movie/{movie_id}?language=en-US&api_key={TMDB_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"Fetched movie details for movie ID {movie_id}.")
        return response.json()
    else:
        logger.error(f"Failed to fetch movie details: {response.status_code} - {response.text}")
        return None

# Command: Add or remove a movie from the list using TMDB
@bot.command(name='mw')
async def manage_movies(ctx, action: str, *, movie_name_or_url: str = None):
    if action == 'add' and movie_name_or_url:
        logger.info(f"Attempting to add movie: {movie_name_or_url}")
        # Check if the input is a TMDB URL
        if movie_name_or_url.startswith("https://www.themoviedb.org/movie/"):
            movie_id = movie_name_or_url.split("/")[-1]
            movie = get_movie_details(movie_id)
        else:
            # Make a request to the TMDB API to search for the movie
            params = {
                'query': movie_name_or_url,
                'include_adult': False,
                'language': 'en-US',
                'page': 1,
                'api_key': TMDB_KEY
            }
            response = requests.get(f"{TMDB_URL}/search/movie", params=params)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    movie = data['results'][0]
                else:
                    movie = None
            else:
                movie = None
        
        if movie:
            movie_details = {
                'title': movie['title'],
                'overview': movie['overview'],
                'release_date': movie['release_date'],
                'vote_average': movie['vote_average'],
                'poster_path': movie['poster_path'],
                'id': movie['id']
            }

            # Create an embed message
            embed = discord.Embed(title=movie_details['title'], description=movie_details['overview'], url=f"https://www.themoviedb.org/movie/{movie['id']}")
            embed.set_image(url=f"{TMDB_IMAGE_URL}{movie['poster_path']}")
            embed.add_field(name="Release Date", value=movie_details['release_date'], inline=True)
            embed.add_field(name="Rating", value=movie_details['vote_average'], inline=True)
            
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('✅')
            await msg.add_reaction('❌')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                if str(reaction.emoji) == '✅':
                    await ctx.send(f"Adding movie: {movie_details['title']}")

                    watchlist_url = f"{TMDB_URL}/list/{TMDB_LIST_ID}/add_item?session_id={TMDB_SESSION_ID}"
                    # Add the movie to the TMDB watchlist
                    payload = {
                        "media_type": "movie",
                        "media_id": movie['id']
                    }
                    headers = {
                        "accept": "application/json",
                        "content-type": "application/json",
                        "Authorization": f"Bearer {TMDB_TOKEN}"
                    }
                    watchlist_response = requests.post(watchlist_url, json=payload, headers=headers)
                    if watchlist_response.status_code == 201:
                        logger.info(f"Successfully added movie to TMDB watchlist: {movie_details['title']}")
                    elif watchlist_response.status_code == 403:
                        error_data = watchlist_response.json()
                        if error_data.get('status_code') == 8:
                            await ctx.send(f"{movie_details['title']} is already in the watchlist.")
                            logger.warning(f"Duplicate entry: {movie_details['title']} is already in the watchlist.")
                        else:
                            await ctx.send(f"Failed to add movie to TMDB watchlist: {watchlist_response.status_code} - {watchlist_response.text}")
                            logger.error(f"Failed to add movie to TMDB watchlist: {watchlist_response.status_code} - {watchlist_response.text}")
                    else:
                        await ctx.send(f"Failed to add movie to TMDB watchlist: {watchlist_response.status_code} - {watchlist_response.text}")
                        logger.error(f"Failed to add movie to TMDB watchlist: {watchlist_response.status_code} - {watchlist_response.text}")
                else:
                    await ctx.send(f"Movie not added: {movie_details['title']}")
                    logger.info(f"Movie not added: {movie_details['title']}")
            except asyncio.TimeoutError:
                await ctx.send(f"No reaction received, movie not added: {movie_details['title']}")
                logger.warning(f"No reaction received, movie not added: {movie_details['title']}")
            
            # Attempt to remove reactions after handling
            try:
                await msg.clear_reactions()
            except discord.Forbidden:
                await ctx.send("I don't have permission to clear reactions.")
                logger.warning("Bot does not have permission to clear reactions.")
        else:
            await ctx.send('Movie not found.')
            logger.warning(f"Movie not found: {movie_name_or_url}")
    elif action == 'remove' and movie_name_or_url:
        logger.info(f"Attempting to remove movie: {movie_name_or_url}")
        movies_from_tmdb = fetch_tmdb_list()
        if movies_from_tmdb:
            # Check if the input is a TMDB URL
            if movie_name_or_url.startswith("https://www.themoviedb.org/movie/"):
                movie_id_to_remove = movie_name_or_url.split("/")[-1]
            else:
                # Search for the movie ID to remove by name
                movie_id_to_remove = None
                for movie in movies_from_tmdb:
                    if movie['title'].lower() == movie_name_or_url.lower():
                        movie_id_to_remove = movie['id']
                        break
            
            if movie_id_to_remove:
                # Remove the movie from the TMDB list
                url = f"{TMDB_URL}/list/{TMDB_LIST_ID}/remove_item?session_id={TMDB_SESSION_ID}"
                payload = { "media_id": movie_id_to_remove }
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "Authorization": f"Bearer {TMDB_TOKEN}"
                }
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    await ctx.send(f"Removed movie: {movie_name_or_url}")
                    logger.info(f"Removed movie: {movie_name_or_url}")
                else:
                    await ctx.send(f"Failed to remove movie from TMDB list: {response.status_code} - {response.text}")
                    logger.error(f"Failed to remove movie from TMDB list: {response.status_code} - {response.text}")
            else:
                await ctx.send(f"Movie not found in the list: {movie_name_or_url}")
                logger.warning(f"Movie not found in the list: {movie_name_or_url}")
        else:
            await ctx.send('Failed to fetch the list of movies.')
            logger.error('Failed to fetch the list of movies.')
    elif action == 'spin':
        logger.info("Spinning the wheel to choose a random movie.")
        movies_from_tmdb = fetch_tmdb_list()
        if movies_from_tmdb:
            emojis = ["🟥", "🟨", "🟩", "🟦"]
            spin_duration = .5  # seconds
            spin_speed = 0.1  # seconds per frame
            total_frames = int(spin_duration / spin_speed)

            msg = await ctx.send("Spinning...")
            for i in range(total_frames):
                frame = ''.join([emojis[(i + j) % len(emojis)] for j in range(4)])
                await msg.edit(content=f"Spinning... {frame}")
                await asyncio.sleep(spin_speed)
            
            chosen_movie = random.choice(movies_from_tmdb)
            embed = discord.Embed(title=chosen_movie['title'], description=chosen_movie['overview'], url=f"https://www.themoviedb.org/movie/{chosen_movie['id']}")
            embed.set_image(url=f"{TMDB_IMAGE_URL}{chosen_movie['poster_path']}")
            embed.add_field(name="Release Date", value=chosen_movie['release_date'], inline=True)
            embed.add_field(name="Rating", value=chosen_movie['vote_average'], inline=True)
            
            await msg.edit(content="The chosen movie is:", embed=embed)
            logger.info(f"The chosen movie is: {chosen_movie['title']}")
        else:
            await ctx.send('No movies in the TMDB list to choose from.')
            logger.warning('No movies in the TMDB list to choose from.')
    elif action == 'list':
        embed = discord.Embed(title='The Wired Watchlist', url=f"https://www.themoviedb.org/list/8303899-the-wired-watchlist")
        await ctx.send(embed=embed)
        logger.info("Provided the watchlist link.")
    elif action == 'help':
        embed = discord.Embed(title="Movie Wheel Bot Commands", description="Here are the available commands:")
        embed.add_field(name="!mw add <movie name or URL>", value="Search for a movie by name or add it directly using the TMDB URL.", inline=False)
        embed.add_field(name="!mw remove <movie name or URL>", value="Remove a movie from the watchlist by name or TMDB URL.", inline=False)
        embed.add_field(name="!mw spin", value="Spin the wheel to choose a random movie from the watchlist.", inline=False)
        embed.add_field(name="!mw list", value="Get the link to the watchlist.", inline=False)
        embed.add_field(name="!mw help", value="Show this help message.", inline=False)
        await ctx.send(embed=embed)
        logger.info("Displayed the help message.")
    else:
        await ctx.send('Invalid command usage. Use "!mw help" to see the list of available commands.')
        logger.warning(f"Invalid command usage: {action} {movie_name_or_url}")

# Run the bot with your token
bot.run(TOKEN)
