import os
from dotenv import load_dotenv
#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
#from langchain.memory import HumanMessage, SystemMessage   
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
import speech_recognition as sr
from datetime import datetime
import re



#from langchain.agents import create_agent

import json
import base64

load_dotenv()

current_date = datetime.now().strftime("%d-%m-%Y")

# --- 1. Vision Tool to Analyze Image ---
@tool
def analyze_food_image(image_path: str):
    """Analyzes a food image to estimate calories and macronutrients."""
    
    # Encode image to base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    #llm = ChatOpenAI(model="gpt-4o", temperature=0)
    llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0,
    api_key="AIzaSyDl8w4u6Qd3nKTJqaIC-m4EBNyQBoyhOQo"  # Pass your key here
    )
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Analyze this food image and return ONLY a JSON object with 'food_name', 'calories', 'protein_g', 'carbs_g', 'fat_g'. Estimate portions reasonably.Current Date {current_date}."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"},
            },
        ]
    )
    
    response = llm.invoke([message])
    print(1)
    print(response)
    print(1)
    # Assuming response is clean JSON, parse it
    try:
        print(json.loads(response.content.replace("```json", "").replace("```", "")))
        return json.loads(response.content.replace("```json", "").replace("```", ""))
    except:
        return {"error": "Failed to parse API response", "raw": response.content}

#####Voice Tool
@tool
def analyze_food_voice(api_key: str):
    """
    Captures audio from microphone, transcribes it, 
    and estimates calories/macros using Gemini.
    """
    # 1. Capture Voice Input
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening to food description...")
        audio = recognizer.listen(source, phrase_time_limit=5)
    
    try:
        # Transcribe audio to text
        voice_text = recognizer.recognize_google(audio)
        print(f"User said: {voice_text}")
    except sr.UnknownValueError:
        return {"error": "Could not understand audio"}
    except sr.RequestError as e:
        return {"error": f"Speech service error: {e}"}

    # 2. Analyze Text with Gemini
    llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0,
    api_key="AIzaSyDl8w4u6Qd3nKTJqaIC-m4EBNyQBoyhOQo"  # Pass your key here
    )
    
    
    prompt = f"""
    Analyze this description of food: '{voice_text}'.
    Return ONLY a JSON object with: 
    "food_name", "calories", "protein_g", "carbs_g", "fat_g". 
    Estimate portions reasonably based on the text. Current Date: {current_date}.
    """

    message = HumanMessage(content=prompt)
    response = llm.invoke([message])

    # 3. Parse JSON response
    try:
        # Remove potential markdown code block formatting
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except:
        return {
            "error": "Failed to parse API response",
            "raw": response.content
        }

# Usage
# result = analyze_food_voice(api_key="YOUR_KEY")
# print(result)

#
######
# --- 2. Define Agent Tools and Model ---
tools = [analyze_food_image]
toolsvoice = [analyze_food_voice]
#model = ChatOpenAI(model="gpt-4o", temperature=0)
#model = ChatOpenAI(model="gpt-4o", temperature=0)

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0,
    api_key="AIzaSyDl8w4u6Qd3nKTJqaIC-m4EBNyQBoyhOQo"
)


# --- 3. Build Agent with Memory ---
system_message = SystemMessage(content="""You are a helpful nutrition agent. 
Analyze food images, provide all the food Items, calorie counts, and track user's daily intake.
Be concise and focus on nutrition. Put TImestamp as current date in DD-MM-YYYY format.""")

# --- 4. Build Agent with Memory ---
system_message1 = SystemMessage(content="""You are a helpful nutrition agent. 
Analyze food voice, provide all the food Items, calorie counts, and track user's daily intake.
Be concise and focus on nutrition. Put TImestamp as current date in DD-MM-YYYY format.""")

#agent_executor = create_react_agent(model, tools, prompt=system_message)
#agent_executor = create_react_agent(model, tools, prompt=system_message)
agent_executor = create_agent(model, tools, system_prompt=system_message)
agent_executor1 = create_react_agent(model, toolsvoice, prompt=system_message1  )
#print(agent_executor)

def get_calorie_agent():
    return agent_executor

def get_voice_calorie_agent():
    return agent_executor1

def log_calories_via_voice():
    # Initialize recognizer
    recognizer = sr.Recognizer()
    total_calories = 0
    
    print("Speak the food you ate (e.g., 'ate 300 calories of pizza')")

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            # Recognize speech
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            
            # Simple keyword parsing - in a real app, use AI/NLP here
            # For demonstration, we assume user says: "I ate X calories"
            #if "calories" in text:
            print(3)
            if re.search(r"calories?", text, re.IGNORECASE): 
                words = text.split()
                print(4)
                # Find the number before 'calories'
                for i, word in enumerate(words):
                    if 'calorie' in word or 'calories' in word:
                        calories = int(words[i-1])
                        total_calories += calories
                        print(f"Logged: {calories} calories.")
                        print(f"Total Daily Calories: {total_calories}")
            else:
                print("Could not parse calorie count.")
                
            if re.search(r"proteins?", text, re.IGNORECASE): 
                words = text.split()
                print(4)
                # Find the number before 'calories'
                for i, word in enumerate(words):
                    if 'protein' in word or 'proteins' in word:
                        proteins = int(words[i-1])
                        total_proteins += proteins
                        print(f"Logged: {proteins} proteins.")

            else:
                print("Could not parse Protein count.")
                
            
            if re.search(r"carbs?", text, re.IGNORECASE): 
                words = text.split()
                print(4)
                # Find the number before 'calories'
                for i, word in enumerate(words):
                    if 'carb' in word or 'carbs' in word:
                        carbs = int(words[i-1])
                        total_carbs += carbs
                        print(f"Logged: {carbs} carbs.")
                        print(f"Total Daily Carbs: {total_carbs}")
            else:
                print("Could not parse carbs count.")
                
            if re.search(r"fats?", text, re.IGNORECASE): 
                words = text.split()
                print(4)
                # Find the number before 'calories'
                for i, word in enumerate(words):
                    if 'fat' in word or 'fats' in word:
                        fats = int(words[i-1])
                        total_fats += fats
                        print(f"Logged: {fats} fats.")
                        print(f"Total Daily Fats: {total_fats}")
            else:
                print("Could not parse Fats count.")

        except sr.UnknownValueError:
            print("Sorry, I could not understand audio.")
        except sr.RequestError:
            print("Could not request results from service.")
            
    a=[total_calories, total_proteins, total_carbs, total_fats]
    b=text
    return a, b