import os
import requests

def send_discord_alert(name, cuisine, db_id):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("   ⚠️ Skipping Discord alert: No webhook URL found in .env")
        return
    
    # Ensure the key is exactly "content"
    message = {
        "content": f"🎉 **Success!** New data generated for **{cuisine}**.\n🍽️ **Name:** {name}\n🗄️ **Database ID:** {db_id}"
    }
    
    try:
        # We must use json=message to properly encode it
        response = requests.post(webhook_url, json=message)
        response.raise_for_status() 
        print("   ✅ Discord alert sent successfully!")
        
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ Failed to send Discord alert: {e}")
        # NEW: Print exactly what Discord is complaining about!
        print(f"      Discord's exact error: {e.response.text}")
        
    except Exception as e:
        print(f"   ❌ A system error occurred: {e}")