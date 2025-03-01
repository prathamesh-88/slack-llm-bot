# Prathamesh's Droid

A simple LLM driven slack bot that replies to your messages with a response generated by a LLM.

# Current Functionality
- Detects if a message is a question and replies with a response generated by a LLM.
- Sends the last 5 messages along with the previous bot responses to the LLM for proper context.
- Can be installed on multiple slack workspaces.

# Tech Stack
- Server: Python (Flask)
- LLM: Gemini Flash 2.0 with Langchain
- Hosting: GCP VM with Ngrok Tunnel

# Steps to set up
1. Setup a Slack App and get the required credentials.
2. Clone the repository.
3. Duplicate the `.env.sample` file as `.env` and fill in the required values.
4. Install the requirements with `pip install -r requirements.txt`. (You can use a virtual environment if you want.)
5. Run the development server with `python app.py`. You can also use `gunicorn app:app` to run the server in production mode with a proper WSGI server (Gunicorn).
6. Run `ngrok http 3000` to get a public URL for the server.
7. Update the Slack App's Event Subscriptions URL and OAuth Redirect URLs with the ngrok URL.

# To-Do
- [ ] Slack OAuth2 token management is currently done in-memory. Needs to be moved to a database.
- [ ] Once the token management is moved to a database, the server can be hosted on a serverless service.
- [ ] Make the message sending functionality async so that server can respond to Slack server quickly.

