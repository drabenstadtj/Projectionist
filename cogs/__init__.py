import os
import logging
import asyncio

# Set up logging
logger = logging.getLogger(__name__)

async def setup(bot):
    COGS_DIR = os.path.dirname(__file__)

    for filename in os.listdir(COGS_DIR):
        if filename.endswith('.py') and filename != '__init__.py':
            cog_name = filename[:-3]  # Remove the .py extension
            if cog_name != 'checks':  # Skip loading checks.py as a cog
                try:
                    await bot.load_extension(f'cogs.{cog_name}')
                    logger.info(f'Successfully loaded cog: {cog_name}')
                except Exception as e:
                    logger.error(f'Failed to load cog {cog_name}: {e}')

def setup_cogs(bot):
    asyncio.run(setup(bot))
