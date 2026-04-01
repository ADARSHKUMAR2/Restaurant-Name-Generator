# alerts.py
import os
import requests

def send_discord_alert(name, cuisine, db_id):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("   ⚠️ Skipping Discord alert: No webhook URL found in .env")
        return
    
    message = {
        "content": f"🚨 **New AI Generation!**\n🍽️ **{name}** ({cuisine})\n💾 Saved to Postgres & Pinecone (ID: {db_id})"
    }
    
    try:
        # Fire the message to Discord
        response = requests.post(webhook_url, json=message)
        response.raise_for_status() # Check for HTTP errors
    except Exception as e:
        print(f"   ❌ Failed to send Discord alert: {e}")