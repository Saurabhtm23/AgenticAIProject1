import os
import time
import json
import requests
from dotenv import load_dotenv
#from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(location="New York,US"):
    """Tool: Fetches live temperature for the location."""
    url = f"http://openweathermap.org{location}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temp": data['main']['temp'],
            "condition": data['weather'][0]['main']
        }
    return {"error": "Could not fetch weather"}

def make_decision(weather_data):
    """Brain: LLM decides if court action is needed based on weather."""
    prompt = f"""
    You are an autonomous AI Agent managing legal filings for a New York City firm.
    Current New York weather: {weather_data['temp']}°C, Condition: {weather_data['condition']}.
    
    Rules:
    - If temperature is below 0°C (32°F) OR if there is heavy snow, court appearances are discouraged.
    - Otherwise, normal operations.
    
    Decide if court action is "REQUIRED" (safe) or "POSTPONED" (dangerous).
    Also, draft a short email subject for a clerk.
    
    Return JSON only: {{"decision": "...", "reason": "...", "email_subject": "..."}}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a legal assistant agent."},
                  {"role": "user", "content": prompt}],
        temperature=0.2 # Consistent, predictable behavior
    )
    return json.loads(response.choices[0].message.content)

def autonomous_loop():
    """Agentic Loop: Observe, Decide, Act."""
    print("🤖 Agentic AI Started: Monitoring NY Courts...")
    while True: # Continuous Loop
        try:
            print("\n--- New Observation Cycle ---")
            
            # 1. Observe
            weather = get_weather()
            print(f"Weather Observed: {weather}")
            
            # 2. Decide
            decision_data = make_decision(weather)
            print(f"Decision: {decision_data['decision']}")
            print(f"Reasoning: {decision_data['reason']}")
            
            # 3. Act (Simulated)
            if decision_data['decision'] == "POSTPONED":
                print(f"✅ ACTION TAKEN: Requesting adjournment. Email: {decision_data['email_subject']}")
            else:
                print(f"✅ ACTION TAKEN: Proceeding with court scheduling.")
                
            # Loop delay (e.g., check every 1 hour)
            time.sleep(3600)
            
        except Exception as e:
            print(f"Error in loop: {e}")
            time.sleep(300) # Wait 5 mins before retrying after error

if __name__ == "__main__":
    autonomous_loop()
