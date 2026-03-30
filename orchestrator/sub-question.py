import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("GROQ_API")

client = Groq(api_key=api_key)

def generate_sub_questions(user_prompt):
    system_prompt = """
    You are a Market Data Analyst. Break down the user's request into 3 specific 
    data-driven questions that can be answered using a SQL database of stock prices.
    Return ONLY a Python list of strings.
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    # Convert string response to a list
    return eval(completion.choices[0].message.content)

# Example Usage:
questions = generate_sub_questions("How did the semiconductor industry do yesterday?")
print(questions)
# Output: ["What was the average price change for tickers in the tech sector?", ...]