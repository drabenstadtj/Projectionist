import os
import json

def load_session_id():
    SESSION_FILE = 'tmdb_session.json'
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get('session_id')
    return None

def is_authorized():
    return load_session_id() is not None
