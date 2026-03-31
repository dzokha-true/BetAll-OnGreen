import json
import os
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

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
You are a helpful assistant that uses tools in order create a market report for the user which includes the following companies:  "NVDA", "AMD", "INTC", "ASML", "QCOM",  "AVGO", "MSFT", "AAPL", "GOOGL", "CRM",  "ADBE", "SNPS", "KLAC", "AMAT".
    
    Use your tools to get data for the market report. 
    After receiving data from your tools, use the SQL data from db_req and the sentiment from sentiment_AI in order to build a full market report.
    NEVER enumerate returned rows or show raw queries.
	 Pull stock data from db_req, structure a SQL friendly query when using db_req.
	 Pull sentiment data from sentiment_AI, use that sentiment data to understand why certain changes happened or why certain stocks are fine despite not doing well. Make sure to reference specific articles. 
	 Assume that you will generate a overview of the tech market. After report is returned to the user, the user might ask follow up questions. Ask if the user wants to incorporate that sentiment into the report and edit the report to user specifications if requested.

		
	 
    Example:
	 Initial user input : Generate a market report for today.
    db_req call: db_req(orchestrator_output: "Return the top performing stocks today, with columns current_price, change_in_last_24hrs, percentage_last_24hrs")
	 sentiment_AI call: sentiment_AI(human_query: "What is the general sentiment regarding our stocks today?")
    db_req response: {"sql_query": "select * from ...", data_top: [{"stock": "GOOGL", "high", "234.23"...}, {"stock": "AVGO", "high", "2500000"...}, ...]}
    sentiment_AI response: NVDA — NVIDIA Corporation
		Sentiment is mixed to bullish, with strong fundamental momentum offset by softer near-term market positioning. Demand for AI accelerators remains robust, and earnings growth continues to be driven by hyperscaler capex cycles and data center expansion. However, shares are down modestly year-to-date and are viewed as “relatively cheap” versus historical multiples, suggesting weaker market sentiment despite strong fundamentals. Key tailwinds include continued AI infrastructure spending and ecosystem dominance, while risks center on valuation compression, supply constraints, and increasing competition from custom....

	
    <GUARDRAILS>
    Never suggest follow up actions that you cannot perform (such as editing data or writing CSV / Excel files).
    Never make more than one db_req and sentiment_AI tool call per conversation turn. If the tool errors or returns different results than expected, summarize the situation and ask the user how to proceed.
    </GUARDRAILS>
""".strip()


TOOLS = [
    {
        "type": "function",
        "name": "db_req",
        "description": "Run a structured market-data retrieval request.",
        "parameters": {
            "type": "object",
            "properties": {
                "human_query": {
                    "type": "string",
                    "description": "Natural language query for market data.",
                },
                "data_top_size": {
                    "type": "integer",
                    "description": "How many rows to return in preview.",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 50,
                },
            },
            "required": ["human_query"],
        },
    },
    {
        "type": "function",
        "name": "sentiment_AI",
        "description": "Analyze sentiment for financial text and optionally a ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to analyze for sentiment.",
                },
                "ticker": {
                    "type": "string",
                    "description": "Optional ticker symbol for context (e.g., NVDA).",
                },
            },
            "required": ["text"],
        },
    },
]


def build_client() -> OpenAI:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("Missing XAI_API_KEY in environment.")
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


def db_req(human_query: str, data_top_size: int = 5) -> dict[str, Any]:
    """
    Data retrieval tool.
    If SnowLeopard is installed and configured, use it.
    Otherwise return a safe stub so the tool loop still works.
    """
    if SnowLeopardClient is None:
        return {
            "status": "stub",
            "message": "SnowLeopardClient not installed; returning framework stub.",
            "human_query": human_query,
            "data_top": [],
            "num_rows": 0,
        }

    datafile_id = os.getenv("SNOW_LEOPARD_DATAFILE_ID")
    if not datafile_id:
        return {
            "status": "error",
            "message": "Missing SNOW_LEOPARD_DATAFILE_ID.",
            "human_query": human_query,
        }

    try:
        response = SnowLeopardClient().retrieve(
            user_query=human_query,
            datafile_id=datafile_id,
        )
        latest = response.data[-1] if getattr(response, "data", None) else None
        rows = getattr(latest, "rows", []) if latest else []
        query = getattr(latest, "query", None) if latest else None
        return {
            "status": "ok",
            "sql_query": query,
            "data_top": rows[:data_top_size],
            "num_rows": len(rows),
        }
    except Exception as exc:
        return {"status": "error", "message": f"{type(exc).__name__}: {exc}"}


def sentiment_AI(text: str, ticker: str | None = None) -> dict[str, Any]:
    """
    Placeholder sentiment tool.
    Replace this logic with your real sentiment model/service.
    """
    lowered = text.lower()
    positive_words = {"beat", "growth", "upside", "bullish", "surge", "strong"}
    negative_words = {"miss", "risk", "downside", "bearish", "drop", "weak"}

    pos_hits = sum(1 for word in positive_words if word in lowered)
    neg_hits = sum(1 for word in negative_words if word in lowered)
    score = pos_hits - neg_hits

    label = "neutral"
    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"

    return {
        "status": "ok",
        "ticker": ticker,
        "sentiment": label,
        "score": score,
        "note": "This is a baseline lexical scorer; swap with production sentiment model.",
    }


TOOL_IMPL = {
    "db_req": db_req,
    "sentiment_AI": sentiment_AI,
}


def _extract_text(response: Any) -> str:
    texts: list[str] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) == "message":
            for content_item in getattr(item, "content", []) or []:
                text_val = getattr(content_item, "text", None)
                if text_val:
                    texts.append(text_val)
    return "\n".join(texts).strip()


def run_agent(
    user_input: str,
    model: str = "grok-4-1",
    max_tool_rounds: int = 3,
) -> tuple[str, AgentState]:
    client = build_client()
    state = AgentState()

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        tools=TOOLS,
        tool_choice="auto",
    )

    for _ in range(max_tool_rounds):
        tool_calls = [
            item for item in (getattr(response, "output", []) or [])
            if getattr(item, "type", None) == "function_call"
        ]
        if not tool_calls:
            break

        tool_outputs = []
        for call in tool_calls:
            name = getattr(call, "name", "")
            call_id = getattr(call, "call_id", "")
            args_raw = getattr(call, "arguments", "{}")

            try:
                args = json.loads(args_raw) if args_raw else {}
            except json.JSONDecodeError:
                args = {}

            if name not in TOOL_IMPL:
                result = {"status": "error", "message": f"Unknown tool: {name}"}
            else:
                result = TOOL_IMPL[name](**args)

            state.tool_outputs[call_id] = {"tool": name, "args": args, "result": result}
            state.last_tool_call_id = call_id
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result),
                }
            )

        response = client.responses.create(
            model=model,
            input=tool_outputs,
            tools=TOOLS,
            previous_response_id=response.id,
        )

    return _extract_text(response), state


if __name__ == "__main__":
    answer, state = run_agent(
        "Check NVDA sentiment from this text: NVDA had strong growth but some downside risk."
    )
    print("Assistant:", answer or "[no text response]")
    print("Last tool call id:", state.last_tool_call_id)
