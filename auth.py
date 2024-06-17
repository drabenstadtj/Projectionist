import requests

# Load your TMDB API key
TMDB_API_KEY = 'b7dd5b6043a6d8305da50c741b003070'

# Step 1: Create a request token
def create_request_token(api_key):
    url = 'https://api.themoviedb.org/3/authentication/token/new'
    headers = {
        'Authorization' : 'Bearer ' + api_key,
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('request_token')
    else:
        print(f"Failed to create request token: {response.status_code} - {response.text}")
        return None

# Step 2: Ask the user for permission
def ask_user_for_permission(request_token):
    auth_url = f"https://www.themoviedb.org/authenticate/{request_token}"
    print(f"Please visit this URL to authorize the request token: {auth_url}")
    print("After authorization, press Enter to continue...")
    input()

# Step 3: Create a session ID
def create_session_id(api_key, request_token):
    url = 'https://api.themoviedb.org/3/authentication/session/new'
    headers = {
        'Authorization':'Bearer ' + api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'request_token': request_token
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('session_id')
    else:
        print(f"Failed to create session ID: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # Replace with your TMDB API key
    api_key = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiN2RkNWI2MDQzYTZkODMwNWRhNTBjNzQxYjAwMzA3MCIsInN1YiI6IjY2NzA0ODU2ZjE4MmU0MTlkYmQxZTJlZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.m76_yMYHuhFdL_FxD39PrnFO62Z0yy1ZOjlGxdephuY'
    
    # Step 1: Create a request token
    request_token = create_request_token(api_key)
    if request_token:
        print(f"Request Token: {request_token}")
        
        # Step 2: Ask the user for permission
        ask_user_for_permission(request_token)
        
        # Step 3: Create a session ID
        session_id = create_session_id(api_key, request_token)
        if session_id:
            print(f"Session ID: {session_id}")
