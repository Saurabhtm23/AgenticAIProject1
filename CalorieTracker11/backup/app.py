from datetime import date
from http import client
import streamlit as st
from agent import get_calorie_agent
from langchain_core.messages import HumanMessage
import csv
#from openai import OpenAI
from pydantic import BaseModel
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
import os

## 1. Setup Client
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0,
    api_key=""  # Pass your key here
    )
#Client = ChatGoogleGenerativeAI(
#    model="gemini-3.1-flash-lite-preview",
#    temperature=0,
#    api_key="AIzaSyAStVsU5FC5vYum8LshRkmoxeXe9j0d7ko"
#)

# 2. Define the expected structure
class AnalyzedMessage(BaseModel):
    Message_ID: str
    Timestamp: date
    Userid: str
    Username: str
    Calories: int
    Protein: float
    Carbs: float
    Fats: float
    Key_Entities: List[str]
    

st.set_page_config(page_title="Agentic Calorie Tracker")
st.title("🍎 Agentic AI Calorie Tracker")

# Session State for History
if "messages" not in st.session_state:
    st.session_state.messages = []

# File uploader
uploaded_file = st.file_uploader("Upload meal image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save file locally
    with open("temp_meal.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.image("temp_meal.jpg", caption="Uploaded Meal", use_column_width=True)
    
    if st.button("Analyze Meal"):
        with st.spinner("Agent is analyzing your meal..."):
            agent = get_calorie_agent()
            
            
            print(agent)  # Debug: Check agent details
            
            
            # Run Agent
            input_msg = HumanMessage(content="analyze_food_image(image_path='temp_meal.jpg')")
            response = agent.invoke({"messages": [input_msg]})
            
            print(response)  # Debug: Check raw response from agent
            print(response["messages"][-1].content)  # Debug: Check last message content
            
            
            # Get last message
            result = response["messages"][-1].content
            
            print(result[0]['text'])  # Debug: Check final result before displaying
            
            
            st.success("Analysis Complete!")
            #st.json(result)
            
            #print(st.session_state.messages)  # Debug: Check session state messages before appending
            
            
            # Store in session
            st.session_state.messages.append(result[0]['text'])

# Display Summary
if st.session_state.messages:
    st.subheader("Daily History")
    for msg in st.session_state.messages:
        st.write(msg)

        if st.button("Click it to Add"):
            with st.spinner("Agent is Adding your meal..."):
                print("Adding your meal in file")
                with open('example1.txt','w') as file:
                     file.write(msg)
                     structured_llm = llm.with_structured_output(AnalyzedMessage)
                     result = structured_llm.invoke(msg)
                     print(result)
                     #completion = client.beta.chat.completions.parse(
                     #   model="gemini-3.1-flash-lite-preview",
                     #   messages=[
                     #   {"role": "system", "content": "Extract structured data from the message."},
                     #   {"role": "user", "content": msg},
                     #   ],
                     #   response_format=AnalyzedMessage,
                     #)
                     #result = completion.choices[0].message.parsed
                     csv_file = "Calorielog3.csv"
                     fieldnames = ["Message_ID", "Timestamp", "Userid", "Username", "Calories", "Protein", "Carbs","Fats","Key_Entities"]
                     with open(csv_file, mode="a", newline="") as file:
                          writer = csv.DictWriter(file, fieldnames=fieldnames)
    
                    # Write header only if file is new
                    #      file.seek(0, 2)
                          if file.tell() == 0:
                             writer.writeheader()
    
                    # Convert list of entities to a string for CSV compatibility
                          row = result.model_dump()
                          print(row)
                          row["Key_Entities"] = ", ".join(row["Key_Entities"])
                          try:
                                writer.writerow(row)
                          except Exception as e:
                                print(f"Error writing row to CSV: {e}")
                    #      file.flush()
                    #      file.close() # Explicitly closes the file
                          print(f"Analysis saved to {csv_file}")
                    
# 3. Unstructured Input
#unstructured_text = """
#'''
#Subject: Urgent: Order #5521 delay. 
#Hi team, I'm John from TechCorp. I'm very frustrated that my 
#shipment of 50 monitors hasn't arrived in London yet. 
#Please fix this immediately!
#'''

# 4. Analyze using ChatGPT with Structured Output
#client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

