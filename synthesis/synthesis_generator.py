"""
synthesis.py
------------
Takes Snow Leopard market data + sentiment results + salesperson's view
and produces:
  1. A morning market brief
  2. Personalized draft emails per exposed client

Flow:
  Step 1 — write the brief (one Groq call)
  Step 2 — for each exposed client, draft a personalized email (parallel Groq calls)

Usage:
  python synthesis.py

  Or from the orchestrator:
    from synthesis.synthesis import run_synthesis
    output = run_synthesis(market_data, sentiment_results, salesperson_view, clients)

Environment variables:
  GROQ_API_KEY - your Groq API key from https://console.groq.com/keys
"""

import os
import sys
import json
import asyncio
import aiohttp
from typing import Any

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama-3.3-70b-versatile"

# ── Groq helper ───────────────────────────────────────────────────────────────

async def groq_call(
    session: aiohttp.ClientSession,
    system: str,
    user: str,
    max_tokens: int = 1000,
) -> str:
    """Fire a single Groq chat completion and return the text response."""
    payload = {
        "model":       GROQ_MODEL,
        "messages":    [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "max_tokens":  max_tokens,
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    async with session.post(
        GROQ_BASE_URL,
        headers=headers,
        json=payload,
        timeout=aiohttp.ClientTimeout(total=60),
    ) as resp:
        body = await resp.json()
        return body["choices"][0]["message"]["content"].strip()

# ── Step 1: Morning brief ─────────────────────────────────────────────────────

BRIEF_SYSTEM = """You are a senior analyst writing the morning market brief for a tech/semiconductor sales desk.

Write a concise, desk-ready brief that a salesperson can read in under 2 minutes.

Structure it exactly like this:

MORNING MARKET BRIEF — {date}

SALESPERSON VIEW
[one sentence summarising the salesperson's thesis for today]

MARKET SUMMARY
[2-3 sentences on overall tech/semi sector tone yesterday]

TOP MOVERS
[bullet per notable mover with price change and the reason why based on news]

KEY THEMES
[2-3 bullets on the most important themes a salesperson should mention to clients today]

RISKS TO WATCH
[1-2 bullets on bearish signals or things to be cautious about]

Keep it factual, punchy, and actionable. No fluff."""

async def write_brief(
    session: aiohttp.ClientSession,
    market_data: dict,
    sentiment_results: list[dict],
    salesperson_view: str,
    date: str,
) -> str:
    """Generate the morning brief from market data + sentiment + salesperson view."""

    # Format sentiment into readable block
    sentiment_block = "\n".join([
        f"- {r['ticker']}: {r['sentiment'].upper()} ({r['confidence']:.0%} confidence) | "
        f"urgency={r['urgency']} | {r['key_insight']}"
        for r in sentiment_results
    ])

    # Format market data into readable block
    movers_block = "\n".join([
        f"- {r.get('ticker')}: close=${r.get('close', 0):.2f} "
        f"({r.get('pct_change', 0):+.2f}%) volume_ratio={r.get('volume_ratio', 1):.1f}x "
        f"RSI={r.get('rsi_14', 50):.0f}"
        for r in market_data.get("movers", [])
    ]) or "No significant movers data available."

    user_message = f"""Date: {date}

SALESPERSON VIEW:
{salesperson_view}

YESTERDAY'S PRICE/VOLUME DATA:
{movers_block}

NEWS SENTIMENT ANALYSIS:
{sentiment_block}

Write the morning market brief now."""

    print("  Generating morning brief...")
    brief = await groq_call(session, BRIEF_SYSTEM, user_message, max_tokens=800)
    print("  Brief complete.")
    return brief

# ── Step 2: Client emails ─────────────────────────────────────────────────────

EMAIL_SYSTEM = """You are a sales professional on a tech/semiconductor trading desk.
Write a short, personalized client email based on their specific holdings and what happened in the market yesterday.

Rules:
- Max 4 sentences
- Open with their specific position that moved
- Reference the key news driving the move
- Include one forward-looking point or question to prompt a call
- Professional but warm tone — not robotic
- Do NOT include a subject line, just the email body
- Sign off as "Sales Desk" """

async def draft_email(
    session: aiohttp.ClientSession,
    client: dict,
    sentiment_results: list[dict],
    market_data: dict,
    salesperson_view: str,
) -> dict:
    """Draft a personalized email for one client based on their holdings."""

    # Find which of this client's holdings had notable moves or news
    holdings = [h.strip() for h in client.get("holdings", "").split(",")]

    # Get sentiment for client's holdings
    relevant_sentiment = [
        r for r in sentiment_results
        if r["ticker"] in holdings
    ]

    # Get price moves for client's holdings
    relevant_moves = [
        r for r in market_data.get("movers", [])
        if r.get("ticker") in holdings
    ]

    if not relevant_sentiment and not relevant_moves:
        return {
            "client_name":  client["name"],
            "client_email": client["email"],
            "firm":         client.get("firm", ""),
            "holdings":     client["holdings"],
            "email_body":   "No significant moves in this client's holdings yesterday.",
            "skipped":      True,
        }

    # Build context for this client
    moves_text = "\n".join([
        f"- {r.get('ticker')}: {r.get('pct_change', 0):+.2f}% | "
        f"volume {r.get('volume_ratio', 1):.1f}x average"
        for r in relevant_moves
    ]) or "No price data available."

    news_text = "\n".join([
        f"- {r['ticker']}: {r['sentiment'].upper()} | {r['key_insight']}"
        for r in relevant_sentiment
    ]) or "No news available."

    user_message = f"""Client: {client['name']} at {client.get('firm', 'their firm')}
Holdings: {client['holdings']}
AUM: ${client.get('aum_millions', 0):.0f}M

Yesterday's moves in their portfolio:
{moves_text}

News context:
{news_text}

Salesperson's view today:
{salesperson_view}

Write the personalized email body now."""

    email_body = await groq_call(session, EMAIL_SYSTEM, user_message, max_tokens=200)

    print(f"  Email drafted for {client['name']} ({client.get('firm', '')})")

    return {
        "client_name":  client["name"],
        "client_email": client["email"],
        "firm":         client.get("firm", ""),
        "holdings":     client["holdings"],
        "email_body":   email_body,
        "skipped":      False,
    }

# ── Step 3: Build call list ───────────────────────────────────────────────────

def build_call_list(
    clients: list[dict],
    sentiment_results: list[dict],
    market_data: dict,
) -> list[dict]:
    """
    Rank clients by how exposed they are to yesterday's moves.
    Higher score = call them first.
    """
    high_urgency_tickers  = {r["ticker"] for r in sentiment_results if r["urgency"] == "high"}
    big_movers            = {
        r.get("ticker") for r in market_data.get("movers", [])
        if abs(r.get("pct_change", 0)) > 2
    }

    ranked = []
    for client in clients:
        holdings = [h.strip() for h in client.get("holdings", "").split(",")]
        score = 0
        triggered_tickers = []

        for ticker in holdings:
            if ticker in high_urgency_tickers:
                score += 3
                triggered_tickers.append(ticker)
            if ticker in big_movers:
                score += 2
                if ticker not in triggered_tickers:
                    triggered_tickers.append(ticker)

        if score > 0:
            ranked.append({
                "name":               client["name"],
                "email":              client["email"],
                "firm":               client.get("firm", ""),
                "holdings":           client["holdings"],
                "aum_millions":       client.get("aum_millions", 0),
                "score":              score,
                "triggered_tickers":  triggered_tickers,
            })

    ranked.sort(key=lambda x: (-x["score"], -x["aum_millions"]))
    return ranked

# ── Main entry point ──────────────────────────────────────────────────────────

async def run_synthesis_async(
    market_data: dict,
    sentiment_results: list[dict],
    salesperson_view: str,
    clients: list[dict],
    date: str,
) -> dict[str, Any]:
    """
    Full synthesis pipeline:
      1. Write the morning brief
      2. Build the ranked call list
      3. Draft personalized emails for top clients in parallel
    """
    print(f"\n Synthesising morning brief and client emails...\n")

    async with aiohttp.ClientSession() as session:

        # Step 1 — brief
        brief = await write_brief(
            session, market_data, sentiment_results, salesperson_view, date
        )

        # Step 2 — call list
        call_list = build_call_list(clients, sentiment_results, market_data)
        print(f"\n  Call list: {len(call_list)} clients to contact today")
        for i, c in enumerate(call_list[:5], 1):
            print(f"    {i}. {c['name']} ({c['firm']}) — {', '.join(c['triggered_tickers'])}")

        # Step 3 — emails for top 10 exposed clients in parallel
        top_clients = call_list[:10]
        print(f"\n  Drafting {len(top_clients)} client emails in parallel...")
        emails = await asyncio.gather(*[
            draft_email(session, c, sentiment_results, market_data, salesperson_view)
            for c in top_clients
        ])

    return {
        "date":             date,
        "salesperson_view": salesperson_view,
        "brief":            brief,
        "call_list":        call_list,
        "emails":           [e for e in emails if not e.get("skipped")],
    }


def run_synthesis(
    market_data: dict,
    sentiment_results: list[dict],
    salesperson_view: str,
    clients: list[dict],
    date: str = None,
) -> dict[str, Any]:
    """Synchronous wrapper — call this from the orchestrator."""
    from datetime import date as dt, timedelta
    if date is None:
        d = dt.today() - timedelta(days=1)
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        date = str(d)
    return asyncio.run(run_synthesis_async(
        market_data, sentiment_results, salesperson_view, clients, date
    ))

# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Mock inputs for testing without the full pipeline
    mock_market_data = {
        "movers": [
            {"ticker": "NVDA", "close": 875.40, "pct_change": 4.5,  "volume_ratio": 2.8, "rsi_14": 72},
            {"ticker": "AMAT", "close": 157.47, "pct_change": 5.2,  "volume_ratio": 3.1, "rsi_14": 25},
            {"ticker": "AMD",  "close": 165.30, "pct_change": -3.8, "volume_ratio": 1.9, "rsi_14": 38},
            {"ticker": "INTC", "close": 37.20,  "pct_change": -2.1, "volume_ratio": 1.5, "rsi_14": 28},
            {"ticker": "ASML", "close": 753.05, "pct_change": 3.2,  "volume_ratio": 2.7, "rsi_14": 44},
        ]
    }

    mock_sentiment = [
        {"ticker": "NVDA", "sentiment": "bullish", "confidence": 0.95, "urgency": "high",
         "key_insight": "Blackwell shipments ahead of schedule — tell clients to add on any dip."},
        {"ticker": "AMAT", "sentiment": "bullish", "confidence": 0.92, "urgency": "high",
         "key_insight": "$2B TSMC order confirms equipment supercycle — buy-the-news situation."},
        {"ticker": "AMD",  "sentiment": "bearish", "confidence": 0.80, "urgency": "high",
         "key_insight": "AI revenue miss vs consensus — clients holding AMD should know risk is to the downside near-term."},
        {"ticker": "INTC", "sentiment": "bearish", "confidence": 0.88, "urgency": "medium",
         "key_insight": "Foundry losses widening — turnaround timeline extending further."},
        {"ticker": "ASML", "sentiment": "bullish", "confidence": 0.91, "urgency": "high",
         "key_insight": "Record EUV order backlog raised guidance — structural long thesis intact."},
    ]

    mock_clients = [
        {"name": "Sarah Chen",    "email": "schen@polariscap.com",    "firm": "Polaris Capital",    "holdings": "NVDA,AMD,ASML,KLAC", "aum_millions": 320},
        {"name": "David Kim",     "email": "dkim@quantedge.com",      "firm": "QuantEdge Partners", "holdings": "NVDA,ASML,KLAC,AMAT","aum_millions": 430},
        {"name": "Tom Walsh",     "email": "twalsh@bluerock.com",     "firm": "Blue Rock Funds",    "holdings": "INTC,AMD,AMAT,KLAC", "aum_millions": 95},
        {"name": "Emma Schulz",   "email": "eschulz@northpoint.com",  "firm": "Northpoint AM",      "holdings": "AMD,NVDA,MSFT,INTC", "aum_millions": 620},
        {"name": "Carlos Rivera", "email": "crivera@stonegate.com",   "firm": "Stonegate Capital",  "holdings": "KLAC,AMAT,ASML,QCOM","aum_millions": 145},
    ]

    mock_view = "Bullish on semis overall — AI infrastructure spend is accelerating. Cautious on AMD near-term given the AI revenue miss. AMAT and ASML are the cleanest longs into year-end."

    output = run_synthesis(mock_market_data, mock_sentiment, mock_view, mock_clients)

    print("\n" + "="*60)
    print("MORNING BRIEF")
    print("="*60)
    print(output["brief"])

    print("\n" + "="*60)
    print(f"CALL LIST ({len(output['call_list'])} clients)")
    print("="*60)
    for i, c in enumerate(output["call_list"], 1):
        print(f"{i}. {c['name']} ({c['firm']}) | AUM ${c['aum_millions']}M | {', '.join(c['triggered_tickers'])}")

    print("\n" + "="*60)
    print(f"DRAFT EMAILS ({len(output['emails'])})")
    print("="*60)
    for e in output["emails"]:
        print(f"\nTO: {e['client_name']} <{e['client_email']}> — {e['firm']}")
        print("-"*40)
        print(e["email_body"])