# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Ensure the bot script is executable
RUN chmod +x app.py

# Set environment variables (you can override these at runtime)
ENV DISCORD_TOKEN=your_discord_bot_token_here
ENV TMDB_KEY=your_tmdb_key_here
ENV TMDB_SESSION_ID=your_tmdb_session_id_here
ENV TMDB_TOKEN=your_tmdb_token_here

# Run the bot script
CMD ["python", "app.py"]
