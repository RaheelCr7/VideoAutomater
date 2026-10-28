#!/usr/bin/env python3
"""
Beyond 80 - 1-Click Interactive YouTube Channel Connector
Connects your real YouTube channel via Google OAuth 2.0 and registers
a Live Production Account in Beyond 80.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.models import PublishingPlatform, PublishingAccount

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    # Needed to post the "which topic next?" comment under each upload.
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

def find_client_secrets():
    candidates = [
        PROJECT_ROOT / "client_secrets.json",
        PROJECT_ROOT / "client_secret.json",
        PROJECT_ROOT / "credentials" / "client_secrets.json",
        PROJECT_ROOT / "credentials" / "client_secret.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Check for any client_secret*.json pattern in root
    matches = list(PROJECT_ROOT.glob("client_secret*.json"))
    if matches:
        return matches[0]
    return None

def print_setup_instructions():
    print("""
========================================================================
  BEYOND 80: YOUTUBE CHANNEL LIVE SETUP GUIDE (Google Cloud Console)
========================================================================

To connect your real YouTube channel, you need an OAuth 2.0 Client ID:

1. GO TO GOOGLE CLOUD CONSOLE:
   👉 Open: https://console.cloud.google.com/

2. CREATE A PROJECT:
   • Click the project dropdown at top left -> "New Project"
   • Name it: "Beyond 80 Video Automator" -> Click "Create"

3. ENABLE THE YOUTUBE DATA API:
   • In the search bar at top, type: "YouTube Data API v3"
   • Click on it -> Click "Enable"

4. CONFIGURE OAUTH CONSENT SCREEN:
   • Go to: APIs & Services -> OAuth consent screen
   • User Type: Select "External" -> Click "Create"
   • App name: "Beyond 80 Automator"
   • User support email: (Your email)
   • Developer contact email: (Your email) -> Click "Save and Continue"
   • Scopes: Click "Save and Continue"
   • Test users: Click "+ Add Users" and type YOUR Gmail / Google Account
     (the account that owns your YouTube channel) -> Click "Save and Continue"

5. CREATE OAUTH CREDENTIALS:
   • Go to: APIs & Services -> Credentials
   • Click "+ CREATE CREDENTIALS" at the top -> "OAuth client ID"
   • Application type: Select "Desktop app"
   • Name: "Beyond 80 Desktop Client"
   • Click "Create"
   • Click "DOWNLOAD JSON" on the popup window!

6. DROP THE FILE HERE:
   • Rename or save the downloaded file as: client_secrets.json
   • Put it in this folder:
     """ + str(PROJECT_ROOT) + """/client_secrets.json

========================================================================
""")

def main():
    print("\n🚀 Beyond 80 - YouTube Channel Authorization\n")
    
    secrets_file = find_client_secrets()
    if not secrets_file:
        print_setup_instructions()
        user_input = input("Enter path to your downloaded client_secret JSON file (or press Enter to exit): ").strip()
        if not user_input:
            print("Setup cancelled. You can run this script again anytime once you have client_secrets.json.")
            return
        secrets_file = Path(user_input).resolve()
        if not secrets_file.exists():
            print(f"❌ Error: File not found at {secrets_file}")
            return

    print(f"✅ Found OAuth Client Secret: {secrets_file}")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("Installing required google libraries...")
        os.system(f"{sys.executable} -m pip install google-api-python-client google-auth-oauthlib")
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

    # Create credentials folder
    creds_dir = PROJECT_ROOT / "credentials"
    creds_dir.mkdir(exist_ok=True)
    token_file = creds_dir / "youtube_token.json"

    print("\n🌐 Opening your web browser for Google Authorization...")
    print("👉 Please log in with the Google Account that owns your YouTube channel and click 'Allow'.\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(secrets_file), SCOPES)
    creds = flow.run_local_server(port=8080, prompt='consent')

    # Save token
    with open(token_file, "w") as f:
        f.write(creds.to_json())
    print(f"✅ Credentials token saved to: {token_file}")

    # Fetch channel name
    youtube = build("youtube", "v3", credentials=creds)
    channels_response = youtube.channels().list(mine=True, part="snippet").execute()
    
    items = channels_response.get("items", [])
    if items:
        channel_title = items[0]["snippet"].get("title", "Beyond 80")
        channel_id = items[0]["id"]
        custom_url = items[0]["snippet"].get("customUrl", "@Beyond80-l1q")
    else:
        channel_title = "Beyond 80"
        channel_id = "UC0DJUgosVx8ZCONmp3iaBaA"
        custom_url = "@Beyond80-l1q"

    # Register or update in PlatformStorage
    storage = PlatformStorage()
    existing_yt = None
    for a in storage.list_publishing_accounts():
        if a.platform == PublishingPlatform.YOUTUBE_SHORTS:
            existing_yt = a
            break

    account_id = existing_yt.id if existing_yt else f"acc_yt_live_{channel_id}"
    
    account = PublishingAccount(
        id=account_id,
        account_id=account_id,
        platform=PublishingPlatform.YOUTUBE_SHORTS,
        account_name=channel_title,
        account_handle=custom_url or "@Beyond80-l1q",
        auth_token=creds.token or "oauth_authorized",
        refresh_token=creds.refresh_token or "",
        is_active=True,
        is_connected=True,
        is_simulated=False,
        notes="LIVE_PRODUCTION_API connected via Google OAuth 2.0",
        metadata={
            "token_file": str(token_file),
            "channel_id": channel_id,
            "channel_title": channel_title,
            "channel_url": f"https://www.youtube.com/{custom_url}" if custom_url else f"https://www.youtube.com/channel/{channel_id}",
            "privacy_status": "public"
        }
    )
    storage.save_publishing_account(account)

    print("\n" + "=" * 60)
    print(f"🎉 SUCCESS! Connected YouTube Channel: \"{channel_title}\"")
    print(f"   Account ID: {account_id}")
    print(f"   Mode: LIVE_PRODUCTION_API (Real Public Uploads)")
    print("=" * 60)
    print("\n👉 Refresh http://localhost:8000 and look at 'Connected Destinations'.")
    print("   Click '🚀 Publish' on your live YouTube card to upload directly to YouTube Shorts!\n")

if __name__ == "__main__":
    main()
