import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize the Lean Brain
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_restaurant_name_and_items(cuisine):
    """
    Uses Groq API to generate a restaurant name and menu items.
    Replaces the heavy LangChain implementation.
    """
    prompt = (
        f"Suggest a catchy, creative name for a {cuisine} restaurant "
        f"and provide a list of 5 popular menu items. "
        f"Return the response in JSON format with keys: 'restaurant_name' and 'menu_items'."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # High-speed model
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} # Ensures we get clean JSON back
        )
        
        # Parse the JSON response
        result = json.loads(completion.choices[0].message.content)
        return result

    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return {
            "restaurant_name": f"The {cuisine} Spot",
            "menu_items": ["Dish 1", "Dish 2", "Dish 3", "Dish 4", "Dish 5"]
        }