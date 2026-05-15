"""
One-time script to generate a Google OAuth refresh token.

Usage:
  1. In Google Cloud Console, create an OAuth 2.0 Desktop app credential.
  2. Copy the Client ID and Client Secret into the prompts below (or set them as
     GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars beforehand).
  3. Run: python get_google_token.py
  4. Paste the resulting GOOGLE_REFRESH_TOKEN into your .env.
  5. You can delete this script afterwards.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

client_id = os.environ.get("GOOGLE_CLIENT_ID") or input("Client ID: ").strip()
client_secret = os.environ.get("GOOGLE_CLIENT_SECRET") or input("Client Secret: ").strip()

client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

print("\n--- Add these to your .env ---")
print(f"GOOGLE_CLIENT_ID={client_id}")
print(f"GOOGLE_CLIENT_SECRET={client_secret}")
print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
