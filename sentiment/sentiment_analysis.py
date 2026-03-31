"""
sentiment.py
------------
Loads articles from article.py, scores each one with Groq,
and returns structured sentiment results.

Run from the project root:
  python sentiment_analysis/sentiment.py

Or from the orchestrator:
  from sentiment_analysis.sentiment import get_sentiment
  results = get_sentiment()

Environment variables:
  GROQ_API_KEY  - your Groq API key from https://console.groq.com/keys
"""

import os
import sys
import json
import asyncio
import aiohttp
from typing import Any

# ── Path fix — works regardless of where you run the script from ──────────────
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from dataset.tech_tickers.article_data.article import get_articles

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama-3.3-70b-versatile"

# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior equity analyst on a sales and trading desk.
Read the news article and return ONLY a valid JSON object — no preamble, no markdown.

{
  "sentiment":   "bullish" | "bearish" | "neutral",
  "confidence":  0.0 to 1.0,
  "key_insight": "one punchy sentence a salesperson can say to a client right now",
  "urgency":     "high" | "medium" | "low"
}

urgency:
  high   = client needs to know today, affects their positions
  medium = useful context but not immediately actionable
  low    = background info, no immediate action needed"""

# ── Score one article ─────────────────────────────────────────────────────────

async def score_article(session: aiohttp.ClientSession, article: tuple) -> dict[str, Any]:
    ticker, date, source, category, _, headline, body = article

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Ticker: {ticker}\nHeadline: {headline}\n\n{body}"},
        ],
        "max_tokens":  300,
        "temperature": 0.1,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }

    try:
        async with session.post(
            GROQ_BASE_URL,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            raw = (await resp.json())["choices"][0]["message"]["content"].strip()
            if "```" in raw:
                raw = raw.split("```")[1].lstrip("json").strip()
            scored = json.loads(raw)

            print(f"  ✓ [{ticker}] {scored['sentiment'].upper():8} "
                  f"conf={scored['confidence']:.0%} urgency={scored['urgency']:6} "
                  f"-> {scored['key_insight'][:55]}...")

            return {
                "ticker":      ticker,
                "date":        date,
                "headline":    headline,
                "source":      source,
                "category":    category,
                "sentiment":   scored["sentiment"],
                "confidence":  scored["confidence"],
                "key_insight": scored["key_insight"],
                "urgency":     scored["urgency"],
            }

    except Exception as e:
        print(f"  x [{ticker}] Error: {e}")
        return {
            "ticker": ticker, "date": date, "headline": headline,
            "source": source, "category": category,
            "sentiment": "neutral", "confidence": 0.0,
            "key_insight": "Unable to score -- check GROQ_API_KEY.", "urgency": "low",
        }

# ── Main ──────────────────────────────────────────────────────────────────────

async def run_sentiment() -> list[dict[str, Any]]:
    articles = get_articles()
    print(f"\n Scoring sentiment for {len(articles)} articles via Groq...\n")

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[score_article(session, a) for a in articles])

    urgency_rank = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda r: (urgency_rank.get(r["urgency"], 2), -r["confidence"]))

    bullish = sum(1 for r in results if r["sentiment"] == "bullish")
    bearish = sum(1 for r in results if r["sentiment"] == "bearish")
    neutral = sum(1 for r in results if r["sentiment"] == "neutral")
    high    = [r["ticker"] for r in results if r["urgency"] == "high"]

    print(f"\n Bullish: {bullish}  Bearish: {bearish}  Neutral: {neutral}")
    if high:
        print(f"   High urgency tickers: {', '.join(high)}")

    return results


def get_sentiment() -> list[dict]:
    """Synchronous wrapper -- call this from the orchestrator."""
    return asyncio.run(run_sentiment())


if __name__ == "__main__":
    results = get_sentiment()
    print("\n-- Results --")
    for r in results:
        print(f"\n{r['ticker']} [{r['sentiment'].upper()} {r['confidence']:.0%}] urgency={r['urgency']}")
        print(f"  -> {r['key_insight']}")