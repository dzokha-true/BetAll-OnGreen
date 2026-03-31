import { useState, useEffect } from "react";

const MOCK_OUTPUT = {
  date: "2026-03-27",
  brief: `MORNING MARKET BRIEF — 2026-03-27

SALESPERSON VIEW
Bullish on semis with selective caution — AI capex cycle intact, AMD near-term risk elevated.

MARKET SUMMARY
The semiconductor sector saw divergent action yesterday with equipment names surging on record order flows while AMD sold off on an AI revenue miss. Overall market breadth was positive with 11 of 15 names in the watchlist finishing higher. Volume was elevated across the board suggesting institutional repositioning.

TOP MOVERS
• AMAT +5.2% on 3.1x volume — $2B TSMC Arizona equipment order, largest single contract in company history
• NVDA +4.5% on 2.8x volume — Record Q4 data center revenue, Blackwell shipments confirmed ahead of schedule
• ASML +3.2% on 2.7x volume — Record EUV order backlog, full-year guidance raised for third consecutive quarter
• AMD -3.8% on 1.9x volume — Q4 AI revenue missed consensus at $2.3B vs $2.5B expected
• INTC -2.1% on 1.5x volume — Foundry losses widened to $2.5B, RSI in oversold territory

KEY THEMES
• Equipment supercycle accelerating: AMAT and KLAC orders at record levels as TSMC Arizona ramp drives non-China capex
• Nvidia moat widening: Blackwell ahead of schedule creates a 2-quarter lead over AMD MI350X roadmap
• AI inference vs training split: AMD losing training share but winning inference — mixed picture for H1

RISKS TO WATCH
• AMD AI revenue trajectory: Two consecutive misses vs consensus raises questions about share gain timeline
• Export control expansion: Further H20 restrictions could create NVDA volatility despite manageable direct impact`,

  call_list: [
    { name: "David Kim",     email: "dkim@quantedge.com",      firm: "QuantEdge Partners", holdings: "NVDA,ASML,KLAC,AMAT", aum_millions: 430, score: 10, triggered_tickers: ["NVDA","ASML","AMAT"] },
    { name: "Sarah Chen",    email: "schen@polariscap.com",    firm: "Polaris Capital",    holdings: "NVDA,AMD,ASML,KLAC",  aum_millions: 320, score: 9,  triggered_tickers: ["NVDA","AMD","ASML"] },
    { name: "Emma Schulz",   email: "eschulz@northpoint.com",  firm: "Northpoint AM",      holdings: "AMD,NVDA,MSFT,INTC",  aum_millions: 620, score: 8,  triggered_tickers: ["AMD","NVDA","INTC"] },
    { name: "Carlos Rivera", email: "crivera@stonegate.com",   firm: "Stonegate Capital",  holdings: "KLAC,AMAT,ASML,QCOM", aum_millions: 145, score: 8,  triggered_tickers: ["AMAT","ASML"] },
    { name: "Tom Walsh",     email: "twalsh@bluerock.com",     firm: "Blue Rock Funds",    holdings: "INTC,AMD,AMAT,KLAC",  aum_millions: 95,  score: 7,  triggered_tickers: ["AMD","AMAT","INTC"] },
    { name: "Yuki Tanaka",   email: "ytanaka@tokyoglobal.com", firm: "Tokyo Global",       holdings: "NVDA,ASML,AMAT,SNPS", aum_millions: 380, score: 7,  triggered_tickers: ["NVDA","ASML","AMAT"] },
    { name: "Nina Petrov",   email: "npetrov@easteurope.com",  firm: "East Europe Fund",   holdings: "NVDA,ASML,KLAC,AVGO", aum_millions: 115, score: 6,  triggered_tickers: ["NVDA","ASML"] },
  ],

  emails: [
    {
      client_name: "David Kim", client_email: "dkim@quantedge.com", firm: "QuantEdge Partners", holdings: "NVDA,ASML,KLAC,AMAT",
      email_body: `Hi David,

Wanted to flag a strong morning for your core positions — AMAT is up 5.2% on a landmark $2B TSMC Arizona equipment order (the largest single contract in the company's history) and NVDA is up 4.5% after confirming Blackwell shipments are ahead of schedule with record Q4 data center revenue.

ASML also raised guidance for the third consecutive quarter on record EUV order intake. All three names are seeing institutional volume 2-3x their 30-day average, suggesting this is more than a one-day move.

Would love to catch up on whether you want to add into the strength or take some chips off the table — are you free for a quick call this morning?

Best,
Sales Desk`
    },
    {
      client_name: "Sarah Chen", client_email: "schen@polariscap.com", firm: "Polaris Capital", holdings: "NVDA,AMD,ASML,KLAC",
      email_body: `Hi Sarah,

Mixed picture in your portfolio this morning — NVDA and ASML are both up strongly (4.5% and 3.2% respectively) while AMD is down 3.8% after Q4 AI revenue came in at $2.3B vs the $2.5B consensus estimate.

The NVDA move is particularly clean with Blackwell shipments confirmed ahead of schedule and gross margins at 76.7%. The AMD miss is worth discussing — two consecutive AI revenue misses raises the question of whether the MI300X ramp timeline needs to be pushed out.

Happy to walk through the positioning implications — worth a quick call?

Best,
Sales Desk`
    },
    {
      client_name: "Emma Schulz", client_email: "eschulz@northpoint.com", firm: "Northpoint AM", holdings: "AMD,NVDA,MSFT,INTC",
      email_body: `Hi Emma,

Your semiconductor names are moving in opposite directions this morning — NVDA is up 4.5% on record Blackwell demand while AMD is down 3.8% on a Q4 AI revenue miss and INTC is down 2.1% with foundry losses widening to $2.5B.

The divergence between NVDA and AMD is sharpening as Blackwell shipments ahead of schedule widen the performance gap heading into H1. MSFT is flat on strong Azure AI numbers which is a positive for the software side of your book.

The AMD and INTC weakness is worth talking through — let me know if you have 10 minutes this morning.

Best,
Sales Desk`
    },
    {
      client_name: "Carlos Rivera", client_email: "crivera@stonegate.com", firm: "Stonegate Capital", holdings: "KLAC,AMAT,ASML,QCOM",
      email_body: `Hi Carlos,

Strong morning for your equipment names — AMAT is up 5.2% on a $2B TSMC Arizona equipment order and ASML is up 3.2% after raising guidance for the third straight quarter on record EUV order intake. Both are trading on elevated volume suggesting institutional conviction.

KLAC is also moving higher in sympathy as the TSMC N2 ramp drives broad equipment demand. Your equipment book is having one of its best days of the year.

Would love to discuss whether this changes your positioning — free for a call?

Best,
Sales Desk`
    },
    {
      client_name: "Tom Walsh", client_email: "twalsh@bluerock.com", firm: "Blue Rock Funds", holdings: "INTC,AMD,AMAT,KLAC",
      email_body: `Hi Tom,

Mixed signals in your book this morning — AMAT is up 5.2% on the TSMC Arizona order win while AMD is down 3.8% on a Q4 AI revenue miss and INTC is down 2.1% with foundry losses widening further.

The AMAT strength partially offsets the AMD and INTC weakness but the net picture is slightly negative. INTC RSI is now deeply oversold which historically precedes either a bounce or acceleration lower.

Happy to talk through the risk picture on AMD and INTC specifically — are you around this morning?

Best,
Sales Desk`
    },
  ]
};

const MOVERS = [
  { ticker: "AMAT",  close: 157.47, pct: +5.2,  vol: "3.1x", rsi: 25,  dir: "up" },
  { ticker: "NVDA",  close: 875.40, pct: +4.5,  vol: "2.8x", rsi: 72,  dir: "up" },
  { ticker: "ASML",  close: 753.05, pct: +3.2,  vol: "2.7x", rsi: 44,  dir: "up" },
  { ticker: "AVGO",  close: 830.32, pct: +2.1,  vol: "2.5x", rsi: 34,  dir: "up" },
  { ticker: "AMD",   close: 165.30, pct: -3.8,  vol: "1.9x", rsi: 38,  dir: "down" },
  { ticker: "INTC",  close: 37.17,  pct: -2.1,  vol: "1.5x", rsi: 28,  dir: "down" },
  { ticker: "GOOGL", close: 193.32, pct: -1.99, vol: "1.6x", rsi: 50,  dir: "down" },
];

const LOADING_STEPS = [
  "Querying Snow Leopard for market signals...",
  "Running sentiment analysis on overnight news...",
  "Identifying exposed client portfolios...",
  "Drafting personalized client emails...",
  "Synthesising morning brief...",
];

export default function App() {
  const [view, setView]               = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [loadStep, setLoadStep]       = useState(0);
  const [output, setOutput]           = useState(null);
  const [activeTab, setActiveTab]     = useState("brief");
  const [copiedIdx, setCopiedIdx]     = useState(null);
  const [time, setTime]               = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!isGenerating) return;
    let step = 0;
    const t = setInterval(() => {
      step++;
      setLoadStep(step);
      if (step >= LOADING_STEPS.length) clearInterval(t);
    }, 520);
    return () => clearInterval(t);
  }, [isGenerating]);

  const handleGenerate = () => {
    if (!view.trim()) return;
    setIsGenerating(true);
    setOutput(null);
    setLoadStep(0);
    setTimeout(() => {
      setIsGenerating(false);
      setOutput(MOCK_OUTPUT);
      setActiveTab("brief");
    }, 3000);
  };

  const handleCopy = (i, text) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(i);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const timeStr = time.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });

  return (
    <div style={s.root}>
      <div style={s.scanlines} />

      {/* ── Header ── */}
      <header style={s.header}>
        <div style={s.hLeft}>
          <span style={s.logo}>⬡ DESK</span>
          <span style={s.logoSub}>MORNING INTELLIGENCE</span>
        </div>
        <div style={s.hCenter}>
          {MOVERS.map(m => (
            <span key={m.ticker} style={s.pill}>
              <span style={s.pillTicker}>{m.ticker}</span>
              <span style={{ color: m.dir === "up" ? "#00ff9d" : "#ff4d6d", fontWeight: 600 }}>
                {m.pct > 0 ? "+" : ""}{m.pct.toFixed(1)}%
              </span>
            </span>
          ))}
        </div>
        <div style={s.hRight}>
          <span style={s.clock}>{timeStr}</span>
          <span style={s.dateLabel}>NYSE · {MOCK_OUTPUT.date}</span>
        </div>
      </header>

      {/* ── Body ── */}
      <div style={s.body}>

        {/* Left sidebar */}
        <aside style={s.sidebar}>

          {/* View input */}
          <div style={s.card}>
            <div style={s.cardHead}>
              <span style={s.cardLabel}>YOUR MARKET VIEW</span>
              <span style={{ ...s.dot, background: "#f5a623", boxShadow: "0 0 6px #f5a62344" }} />
            </div>
            <textarea
              style={s.textarea}
              placeholder="e.g. Bullish on semis, cautious on AMD near-term. AMAT and ASML are cleanest longs..."
              value={view}
              onChange={e => setView(e.target.value)}
              rows={5}
            />
            <button
              style={{ ...s.genBtn, opacity: view.trim() ? 1 : 0.35, cursor: view.trim() ? "pointer" : "default" }}
              onClick={handleGenerate}
              disabled={!view.trim() || isGenerating}
            >
              {isGenerating
                ? <span style={{ display: "flex", alignItems: "center", gap: 8, justifyContent: "center" }}>
                    <span style={s.spin}>◌</span> GENERATING...
                  </span>
                : "GENERATE MORNING BRIEF →"}
            </button>
          </div>

          {/* Market snapshot */}
          <div style={s.card}>
            <div style={s.cardHead}>
              <span style={s.cardLabel}>MARKET SNAPSHOT</span>
              <span style={{ ...s.dot, background: "#00ff9d", boxShadow: "0 0 6px #00ff9d44" }} />
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["TICKER","CLOSE","CHG%","VOL","RSI"].map(h => (
                    <th key={h} style={s.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {MOVERS.map(m => (
                  <tr key={m.ticker} style={{ borderBottom: "1px solid #0a1020" }}>
                    <td style={{ ...s.td, color: "#c8d6e8", fontWeight: 600 }}>{m.ticker}</td>
                    <td style={s.td}>${m.close.toFixed(2)}</td>
                    <td style={{ ...s.td, color: m.dir === "up" ? "#00ff9d" : "#ff4d6d", fontWeight: 600 }}>
                      {m.pct > 0 ? "+" : ""}{m.pct.toFixed(1)}%
                    </td>
                    <td style={{ ...s.td, color: parseFloat(m.vol) >= 2 ? "#f5a623" : "#4a6070" }}>{m.vol}</td>
                    <td style={{ ...s.td, color: m.rsi > 70 ? "#ff4d6d" : m.rsi < 30 ? "#00e87a" : "#4a6070" }}>{m.rsi}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </aside>

        {/* Main content */}
        <main style={s.main}>

          {/* Empty state */}
          {!output && !isGenerating && (
            <div style={s.empty}>
              <div style={{ fontSize: 52, color: "#0f1c2e", marginBottom: 16 }}>◈</div>
              <div style={{ fontSize: 11, color: "#1e2d45", letterSpacing: 2, textAlign: "center", lineHeight: 1.8 }}>
                ENTER YOUR MARKET VIEW<br />AND GENERATE THE MORNING BRIEF
              </div>
            </div>
          )}

          {/* Loading */}
          {isGenerating && (
            <div style={s.loading}>
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                {LOADING_STEPS.map((line, i) => (
                  <div
                    key={i}
                    style={{
                      fontSize: 12, letterSpacing: 0.5,
                      color: i < loadStep ? "#00ff9d" : i === loadStep ? "#5a9a7a" : "#1a2a3a",
                      display: "flex", gap: 10, alignItems: "center",
                      transition: "color 0.3s",
                    }}
                  >
                    <span style={{ color: i < loadStep ? "#00ff9d" : "#1a2a3a" }}>
                      {i < loadStep ? "✓" : "▸"}
                    </span>
                    {line}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Output */}
          {output && (
            <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>

              {/* Tabs */}
              <div style={s.tabs}>
                {[
                  { id: "brief",  label: "BRIEF" },
                  { id: "calls",  label: `CALL LIST (${output.call_list.length})` },
                  { id: "emails", label: `EMAILS (${output.emails.length})` },
                ].map(tab => (
                  <button
                    key={tab.id}
                    style={{ ...s.tab, ...(activeTab === tab.id ? s.tabOn : {}) }}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Brief */}
              {activeTab === "brief" && (
                <div style={{ padding: 28, overflowY: "auto", flex: 1 }}>
                  <pre style={s.briefText}>{output.brief}</pre>
                </div>
              )}

              {/* Call list */}
              {activeTab === "calls" && (
                <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 8, overflowY: "auto", flex: 1 }}>
                  {output.call_list.map((c, i) => (
                    <div key={i} style={s.clientCard}>
                      <div style={s.rank}>#{i + 1}</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, color: "#e8f0f8", fontWeight: 600, marginBottom: 2 }}>{c.name}</div>
                        <div style={{ fontSize: 10, color: "#2d4a6e", letterSpacing: 0.5, marginBottom: 8 }}>{c.firm}</div>
                        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                          {c.holdings.split(",").map(h => (
                            <span key={h} style={{
                              ...s.tag,
                              ...(c.triggered_tickers.includes(h.trim()) ? s.tagOn : {})
                            }}>
                              {h.trim()}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                        <span style={{ fontSize: 11, color: "#4a6070" }}>${c.aum_millions}M AUM</span>
                        <span style={{ fontSize: 10, color: "#f5a623", letterSpacing: 3 }}>
                          {"▮".repeat(Math.min(c.score, 5))}{"▯".repeat(Math.max(5 - c.score, 0))}
                        </span>
                        <a href={`mailto:${c.email}`} style={s.emailLink}>EMAIL →</a>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Emails */}
              {activeTab === "emails" && (
                <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16, overflowY: "auto", flex: 1 }}>
                  {output.emails.map((e, i) => (
                    <div key={i} style={s.emailCard}>
                      <div style={s.emailHead}>
                        <div>
                          <div style={{ fontSize: 13, color: "#e8f0f8", fontWeight: 600, marginBottom: 2 }}>{e.client_name}</div>
                          <div style={{ fontSize: 10, color: "#2d4a6e", marginBottom: 3 }}>{e.firm} · {e.client_email}</div>
                          <div style={{ fontSize: 9, color: "#3a5470", letterSpacing: 1 }}>{e.holdings}</div>
                        </div>
                        <div style={{ display: "flex", gap: 8 }}>
                          <button style={s.copyBtn} onClick={() => handleCopy(i, e.email_body)}>
                            {copiedIdx === i ? "COPIED ✓" : "COPY"}
                          </button>
                          <a href={`mailto:${e.client_email}`} style={s.sendBtn}>SEND →</a>
                        </div>
                      </div>
                      <pre style={s.emailBody}>{e.email_body}</pre>
                    </div>
                  ))}
                </div>
              )}

            </div>
          )}
        </main>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #080c14; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: #080c14; }
        ::-webkit-scrollbar-thumb { background: #0f1c2e; border-radius: 2px; }
        textarea::placeholder { color: #1e2d45 !important; }
        textarea:focus { outline: none; border-color: #00ff9d !important; }
        button:hover { opacity: 0.85; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

const s = {
  root: { background: "#080c14", minHeight: "100vh", fontFamily: "'IBM Plex Mono', monospace", color: "#c8d6e8", position: "relative" },
  scanlines: { position: "fixed", inset: 0, pointerEvents: "none", zIndex: 999, background: "repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.025) 2px,rgba(0,0,0,0.025) 4px)" },
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 20px", borderBottom: "1px solid #0d1825", background: "#05080f", position: "sticky", top: 0, zIndex: 100 },
  hLeft: { display: "flex", alignItems: "center", gap: 10 },
  logo: { fontSize: 17, fontWeight: 600, color: "#00ff9d", letterSpacing: 4 },
  logoSub: { fontSize: 8, color: "#1e3050", letterSpacing: 3 },
  hCenter: { display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center", flex: 1, padding: "0 16px" },
  pill: { display: "flex", gap: 5, alignItems: "center", background: "#0a0f1a", border: "1px solid #0d1825", padding: "3px 8px", borderRadius: 3, fontSize: 10 },
  pillTicker: { color: "#3a5470", fontWeight: 500 },
  hRight: { display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 2 },
  clock: { fontSize: 13, color: "#00ff9d", fontWeight: 600, letterSpacing: 2 },
  dateLabel: { fontSize: 8, color: "#1e3050", letterSpacing: 1 },
  body: { display: "grid", gridTemplateColumns: "320px 1fr", height: "calc(100vh - 51px)", overflow: "hidden" },
  sidebar: { background: "#05080f", borderRight: "1px solid #0d1825", overflowY: "auto", padding: 14, display: "flex", flexDirection: "column", gap: 14 },
  main: { overflowY: "auto", position: "relative", display: "flex", flexDirection: "column" },
  card: { background: "#090d17", border: "1px solid #0d1825", borderRadius: 4, padding: 14 },
  cardHead: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  cardLabel: { fontSize: 8, letterSpacing: 3, color: "#1e3050", fontWeight: 600 },
  dot: { width: 6, height: 6, borderRadius: "50%" },
  textarea: { width: "100%", background: "#05080f", border: "1px solid #0d1825", borderRadius: 3, padding: "10px 12px", color: "#c8d6e8", fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, lineHeight: 1.7, resize: "none", marginBottom: 10, transition: "border-color 0.2s" },
  genBtn: { width: "100%", padding: "11px 0", background: "transparent", border: "1px solid #00ff9d", color: "#00ff9d", borderRadius: 3, fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, letterSpacing: 2, fontWeight: 600, transition: "opacity 0.2s" },
  spin: { display: "inline-block", animation: "spin 1s linear infinite" },
  th: { fontSize: 7, letterSpacing: 2, color: "#1e3050", textAlign: "left", padding: "4px 6px", borderBottom: "1px solid #0d1825", fontWeight: 600 },
  td: { fontSize: 11, padding: "6px 6px", color: "#4a6070" },
  empty: { display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", flex: 1 },
  loading: { display: "flex", alignItems: "center", justifyContent: "center", height: "100%", flex: 1, padding: 40 },
  tabs: { display: "flex", borderBottom: "1px solid #0d1825", background: "#05080f", position: "sticky", top: 0, zIndex: 10, flexShrink: 0 },
  tab: { padding: "12px 22px", background: "transparent", border: "none", borderBottom: "2px solid transparent", color: "#1e3050", fontFamily: "'IBM Plex Mono', monospace", fontSize: 9, letterSpacing: 2, cursor: "pointer", transition: "all 0.15s" },
  tabOn: { color: "#00ff9d", borderBottomColor: "#00ff9d" },
  briefText: { fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, lineHeight: 2, color: "#c8d6e8", whiteSpace: "pre-wrap" },
  clientCard: { display: "flex", alignItems: "center", gap: 14, background: "#090d17", border: "1px solid #0d1825", borderRadius: 4, padding: "12px 16px" },
  rank: { fontSize: 18, color: "#0d1825", fontWeight: 600, minWidth: 28 },
  tag: { fontSize: 9, padding: "2px 7px", borderRadius: 2, letterSpacing: 1, background: "#0a0f1a", border: "1px solid #0d1825", color: "#2d4060" },
  tagOn: { background: "#001a0d", border: "1px solid #00ff9d33", color: "#00ff9d" },
  emailLink: { fontSize: 9, letterSpacing: 2, color: "#00ff9d", border: "1px solid #00ff9d33", padding: "4px 10px", borderRadius: 2, textDecoration: "none", background: "#001a0d" },
  emailCard: { background: "#090d17", border: "1px solid #0d1825", borderRadius: 4, overflow: "hidden" },
  emailHead: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", padding: "12px 16px", borderBottom: "1px solid #0d1825", background: "#05080f" },
  copyBtn: { fontSize: 9, letterSpacing: 2, color: "#4a6070", border: "1px solid #0d1825", padding: "5px 12px", borderRadius: 2, background: "#0a0f1a", cursor: "pointer", fontFamily: "'IBM Plex Mono', monospace" },
  sendBtn: { fontSize: 9, letterSpacing: 2, color: "#00ff9d", border: "1px solid #00ff9d33", padding: "5px 12px", borderRadius: 2, textDecoration: "none", background: "#001a0d" },
  emailBody: { padding: "16px 18px", fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, lineHeight: 1.8, color: "#6a8090", whiteSpace: "pre-wrap" },
};
