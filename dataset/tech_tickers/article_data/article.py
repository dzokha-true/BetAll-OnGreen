"""
articles_data.py
----------------
15 mock news articles — one per ticker, all dated yesterday.
Each article explains the price/volume anomaly Snow Leopard will detect.

Each tuple: (ticker, date, source, category, sentiment, headline, body)

Usage:
    from articles_data import get_articles
    articles = get_articles()
"""

from datetime import date, timedelta

def get_yesterday():
    d = date.today() - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d

def get_articles():
    yesterday = str(get_yesterday())

    return [

        ("NVDA", yesterday, "Bloomberg", "earnings", "bullish",
         "Nvidia Posts Record Quarter, Data Center Revenue Up 409% YoY",
         "Nvidia smashed Q4 estimates with data center revenue of $18.4B, up 409% year-over-year. "
         "CEO Jensen Huang called Blackwell GPU demand 'insane' on the earnings call. "
         "The company guided Q1 revenue to $24B, well above the $22B consensus. "
         "Gross margins hit 76.7%, the highest in company history, driving heavy volume as institutions added to positions."),

        ("AMD", yesterday, "Reuters", "earnings", "bearish",
         "AMD Q4 AI Revenue Misses Estimates, Shares Fall on Guidance Concerns",
         "AMD reported Q4 AI accelerator revenue of $2.3B, below the $2.5B consensus estimate. "
         "Total data center revenue grew 69% YoY but the AI miss disappointed investors expecting faster share gains against Nvidia. "
         "CEO Lisa Su reiterated full-year guidance but the market reacted negatively, sending shares lower on elevated volume. "
         "Analysts are split on whether the miss is a one-quarter blip or a sign of deeper competitive pressure from Nvidia's CUDA moat."),

        ("INTC", yesterday, "WSJ", "earnings", "bearish",
         "Intel Q4 Misses on Revenue and EPS as Foundry Losses Widen to $2.5B",
         "Intel reported Q4 revenue and EPS below consensus estimates as its foundry division losses widened to $2.5B for the quarter. "
         "CEO Pat Gelsinger acknowledged the turnaround is taking longer than expected and announced cost cuts targeting $3B in savings. "
         "The stock is now trading near its 52-week low as investors question the timeline for the company's manufacturing recovery. "
         "RSI has fallen deep into oversold territory reflecting sustained institutional selling pressure over recent weeks."),

        ("ASML", yesterday, "Bloomberg", "earnings", "bullish",
         "ASML Reports Record EUV Order Backlog, Raises Full Year Guidance",
         "ASML reported its strongest quarterly order intake on record driven by surging demand for EUV lithography machines from TSMC and Samsung. "
         "While Dutch export restrictions have limited sales to China, demand from non-restricted markets more than offsets the shortfall. "
         "The company raised full-year guidance sending shares to a fresh 52-week high on above-average volume. "
         "High-NA EUV system orders also exceeded internal expectations, driving a meaningful step-up in average selling price per unit."),

        ("QCOM", yesterday, "CNBC", "product", "bullish",
         "Qualcomm Snapdragon X Elite Wins Major PC Design Deals at Dell and HP",
         "Qualcomm announced expanded design wins for its Snapdragon X Elite chip at Dell and HP, a significant step in its effort to break into the laptop market dominated by Intel. "
         "Analysts estimate the PC opportunity could add $2B in annual revenue by 2026. "
         "Shares rose on average volume as the market weighed near-term mobile weakness against the long-term PC upside opportunity. "
         "Independent benchmarks released yesterday showed Snapdragon X Elite outperforming Apple M3 in multi-threaded workloads."),

        ("AVGO", yesterday, "Reuters", "earnings", "bullish",
         "Broadcom AI Networking Revenue Triples, Custom Chip Pipeline Expanding",
         "Broadcom disclosed that AI-related networking revenue tripled year-over-year driven by demand for custom AI accelerators and high-speed networking chips from major cloud providers. "
         "The company reiterated its full-year AI revenue target of $10B which analysts believe is conservative given pipeline visibility. "
         "Volume surged to nearly 3x the 30-day average as momentum investors added to positions following the disclosure. "
         "Management also confirmed a fifth hyperscaler customer is in advanced discussions for a custom AI chip design engagement."),

        ("MSFT", yesterday, "WSJ", "earnings", "bullish",
         "Microsoft Azure AI Revenue Grows 33% as Copilot Enterprise Adoption Accelerates",
         "Microsoft reported Azure AI services grew 33% in the latest quarter ahead of consensus estimates as enterprise Copilot adoption accelerated significantly. "
         "CFO Amy Hood raised full-year cloud guidance for the third consecutive quarter citing strong Copilot seat expansion. "
         "Shares edged higher on steady volume continuing their grind toward all-time highs. "
         "Management highlighted that Copilot for Microsoft 365 has now crossed 1 million paid enterprise seats within six months of general availability."),

        ("AAPL", yesterday, "Bloomberg", "product", "bullish",
         "Apple Intelligence Features Drive Strongest iPhone Upgrade Cycle in Five Years",
         "Multiple analysts raised Apple price targets following channel checks suggesting stronger-than-expected iPhone 16 demand driven by Apple Intelligence on-device AI features. "
         "Wedbush raised its target to $275 calling the AI upgrade cycle the largest in the company's history. "
         "Volume was in line with the 30-day average as the stock consolidated near recent highs ahead of the next earnings report. "
         "Analysts estimate only 15% of the iPhone installed base has upgraded to an AI-capable model, suggesting a multi-year runway."),

        ("GOOGL", yesterday, "FT", "earnings", "bullish",
         "Alphabet Gemini Ultra Wins Enterprise Contracts as Search AI Overviews Monetise",
         "Alphabet shares rose after the company confirmed Gemini Ultra is winning enterprise contracts previously held by OpenAI. "
         "Management also confirmed that AI Overviews in Search are now monetising at rates comparable to traditional search ads, alleviating a key investor concern. "
         "The stock is recovering from a brief oversold dip with RSI moving back toward neutral territory on above-average volume. "
         "Google Cloud revenue grew 28% year-over-year driven by Gemini AI services adoption, narrowing the gap with Microsoft Azure in enterprise workloads."),

        ("META", yesterday, "CNBC", "earnings", "bullish",
         "Meta Ad Revenue Reaccelerates on AI Targeting, Llama 4 Drives Developer Momentum",
         "Meta Platforms reported accelerating advertising revenue growth aided by AI-driven ad targeting improvements that increased conversion rates by an estimated 20%. "
         "The open-source release of Llama 4 drove 50,000 developer downloads in its first week, the fastest adoption of any open-source AI model to date. "
         "Shares hit a 52-week high on volume nearly double the 30-day average as institutional investors re-rated the stock. "
         "Management also confirmed the Meta AI assistant has reached 500 million monthly active users across its platforms."),

        ("CRM", yesterday, "Barron's", "product", "bullish",
         "Salesforce Agentforce Signs 500 Enterprise Deals, Raises ARR Guidance",
         "Salesforce announced that its Agentforce AI platform signed over 500 enterprise deals in its first full quarter of availability, significantly ahead of internal targets. "
         "The company raised annual recurring revenue guidance and announced a $2B share buyback program. "
         "Volume was elevated as growth investors who had previously rotated out began rebuilding positions following the strong update. "
         "Average contract values are increasing as customers expand from pilot deployments to enterprise-wide Agentforce rollouts."),

        ("ADBE", yesterday, "Reuters", "product", "mixed",
         "Adobe Firefly Hits 10 Billion Generations but AI Competition Concerns Linger",
         "Adobe reported Firefly generative AI reached 10 billion image generations with monetisation through Creative Cloud subscriptions beginning to inflect positively. "
         "The company beat earnings estimates and raised guidance, easing some concerns about AI competition from Midjourney and OpenAI. "
         "However the stock's recovery from oversold levels was modest as investors remain cautious about long-term competitive dynamics in the consumer creative segment. "
         "Volume was elevated as traders repositioned following the earnings beat with both buyers and sellers active throughout the session."),

        ("SNPS", yesterday, "Bloomberg", "earnings", "bullish",
         "Synopsys Reports Record Bookings as AI Chip Design Complexity Drives EDA Demand",
         "Synopsys reported record bookings driven by surging demand from AI chip designers at Nvidia, Apple, and AMD who require increasingly sophisticated design automation tools. "
         "The company's AI-assisted design tools are now used in over 60% of leading-edge chip projects globally. "
         "Shares quietly approached their 52-week high on steady volume in a pattern analysts describe as classic institutional accumulation. "
         "The pending Ansys acquisition received final regulatory approval yesterday adding simulation capabilities to Synopsys's EDA portfolio."),

        ("KLAC", yesterday, "WSJ", "earnings", "bullish",
         "KLA Process Control Orders Surge as TSMC Accelerates 2nm Node Capacity Expansion",
         "KLA Corporation reported a significant jump in process control equipment orders driven by TSMC's aggressive expansion of its 2-nanometer node capacity in Taiwan and Arizona. "
         "KLA's inspection and metrology tools are non-discretionary at leading-edge nodes as chipmakers cannot sacrifice yield to cut costs. "
         "Volume spiked to 2x the 30-day average following the order announcement as investors recognized the earnings upside. "
         "Analysts note that process control spending intensity is increasing at each new node generation, structurally growing KLA's total addressable market."),

        ("AMAT", yesterday, "Reuters", "earnings", "bullish",
         "Applied Materials Wins $2B TSMC Arizona Equipment Order, Stock Surges on Heavy Volume",
         "Applied Materials announced a landmark $2B equipment order from TSMC's Arizona fabrication facility covering deposition and etch equipment for N3 and N2 process nodes. "
         "The order is the largest single contract in the company's history and will be delivered over 18 months. "
         "The stock gapped up at the open on exceptionally heavy volume — over 3x the 30-day average — triggering overbought RSI readings by midday. "
         "Analysts raised price targets across the board with UBS calling it evidence of a multi-year semiconductor equipment supercycle."),
    ]