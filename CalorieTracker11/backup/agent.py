import os
from dotenv import load_dotenv
#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
#from langchain.memory import HumanMessage, SystemMessage   
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
#from langchain.agents import create_agent

import json
import base64

load_dotenv()

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
    api_key="AIzaSyAStVsU5FC5vYum8LshRkmoxeXe9j0d7ko"  # Pass your key here
    )
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Analyze this food image and return ONLY a JSON object with 'food_name', 'calories', 'protein_g', 'carbs_g', 'fat_g'. Estimate portions reasonably."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"},
            },
        ]
    )
    
    response = llm.invoke([message])
    # Assuming response is clean JSON, parse it
    try:
        return json.loads(response.content.replace("```json", "").replace("```", ""))
    except:
        return {"error": "Failed to parse API response", "raw": response.content}

# --- 2. Define Agent Tools and Model ---
tools = [analyze_food_image]
#model = ChatOpenAI(model="gpt-4o", temperature=0)
#model = ChatOpenAI(model="gpt-4o", temperature=0)

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0,
    api_key="AIzaSyAStVsU5FC5vYum8LshRkmoxeXe9j0d7ko"
)


# --- 3. Build Agent with Memory ---
system_message = SystemMessage(content="""You are a helpful nutrition agent. 
Analyze food images, provide calorie counts, and track user's daily intake.
Be concise and focus on nutrition.""")

#agent_executor = create_react_agent(model, tools, prompt=system_message)
agent_executor = create_react_agent(model, tools, prompt=system_message)
#print(agent_executor)

def get_calorie_agent():
    return agent_executor