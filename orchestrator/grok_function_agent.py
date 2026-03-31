import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from sentiment.sentiment_analysis import get_sentiment

try:
    from snowleopard import SnowLeopardClient
except Exception:
    SnowLeopardClient = None

load_dotenv()

@dataclass
class AgentState:
    tool_outputs: dict[str, Any] = field(default_factory=dict)
    last_tool_call_id: str | None = None

SYSTEM_PROMPT = """
You are a senior market analyst. Use your tools to create a market report.
1. Use db_req to get hard price data/SQL results.
2. Use sentiment_AI to get news sentiment.
Reference specific companies and data points. Do not show raw SQL queries.
""".strip()

# Groq/xAI standard tool schema
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "db_req",
            "description": "Run a structured market-data retrieval request for stock prices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "human_query": {
                        "type": "string",
                        "description": "Natural language query for market data.",
                    },
                    "data_top_size": {
                        "type": "integer",
                        "description": "How many rows to return.",
                        "default": 5,
                    },
                },
                "required": ["human_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sentiment_AI",
            "description": "Analyze sentiment for financial news and articles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze for sentiment.",
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Optional ticker symbol (e.g., NVDA).",
                    },
                },
                "required": ["text"],
            },
        },
    },
]

def build_client() -> OpenAI:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY in environment.")
    return OpenAI(
        api_key=api_key, 
        base_url="https://api.groq.com/openai/v1"
    )

def db_req(human_query: str, data_top_size: int = 5) -> dict[str, Any]:
    api_key = os.getenv("SNOW_LEOPARD_API_KEY")
    datafile_id = os.getenv("SNOW_LEOPARD_DATAFILE_ID_TICKER")
    try:
        if SnowLeopardClient is None:
            return {"status": "error", "message": "SnowLeopardClient not installed"}
        
        client_sl = SnowLeopardClient(api_key=api_key)
        response = client_sl.retrieve(user_query=human_query, datafile_id=datafile_id)
        
        if response.data:
            latest = response.data[0]
            return {
                "status": "ok",
                "sql_query": latest.query,
                "data_top": latest.rows[:data_top_size],
                "num_rows": len(latest.rows),
            }
        return {"status": "empty", "message": "No data returned."}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

def sentiment_AI(text: str, ticker: str | None = None) -> dict[str, Any]:
    try:
        # Note: If this fails with 'choices', check sentiment_analysis.py 
        # and ensure you added time.sleep(1) in the loop!
        all_results = get_sentiment() 
        if ticker:
            filtered = [r for r in all_results if r['ticker'].upper() == ticker.upper()]
            return {"status": "ok", "results": filtered}
        return {"status": "ok", "results": all_results[:5]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

TOOL_IMPL = {
    "db_req": db_req,
    "sentiment_AI": sentiment_AI,
}

def run_agent(
    user_input: str,
    model: str = "llama-3.3-70b-versatile",
    max_tool_rounds: int = 3,
) -> tuple[str, AgentState]:
    client = build_client()
    state = AgentState()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for _ in range(max_tool_rounds):
        # We use a try block to catch the 400 'Failed to call a function' error
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            return f"Agent Error: {str(e)}", state

        response_message = response.choices[0].message
        messages.append(response_message)

        if not response_message.tool_calls:
            break

        for tool_call in response_message.tool_calls:
            name = tool_call.function.name
            
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                # Handle cases where Groq returns malformed JSON
                args = {"human_query": user_input} if name == "db_req" else {"text": user_input}

            # Execute tool logic
            result = TOOL_IMPL.get(name, lambda **x: {"error": "tool not found"})(**args)

            state.tool_outputs[tool_call.id] = {"tool": name, "args": args, "result": result}
            state.last_tool_call_id = tool_call.id
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": json.dumps(result),
            })

    # Return logic that handles both ChatCompletionMessage and Dict
    final_msg = messages[-1]
    if hasattr(final_msg, 'content'):
        return final_msg.content or "[No Response Content]", state
    return final_msg.get('content', "[No Response Content]"), state

if __name__ == "__main__":
    print("🤖 Agent starting...")
    # You can change the query here to test different companies
    prompt = "Check NVDA sentiment and give me its latest price from the database."
    answer, state = run_agent(prompt)
    
    print("\n--- ASSISTANT RESPONSE ---")
    print(answer)
    print("\n--- TOOL LOG ---")
    for tid, info in state.tool_outputs.items():
        print(f"Used {info['tool']} with args {info['args']}")