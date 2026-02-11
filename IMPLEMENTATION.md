# OpenClaw Implementation Doc

**Model:** `anthropic/claude-sonnet-4-5`

---

## What to Build

### Financial Models (Python + Excel)
1. DCF Valuation Model
2. Comparable Company Analysis
3. LBO Model
4. Portfolio Optimizer (Mean-Variance)
5. Options Pricing Calculator (Black-Scholes)

### AI/ML Models (Python)
1. Stock Price Prediction (LSTM)
2. Sentiment Analysis on Earnings Calls
3. Credit Risk Scoring
4. Trading Strategy Backtester

### Content
- **Blog posts:** Explainers for each model + finance concept deep dives
- **Research journal:** Daily market notes + what I learned + fintech news

---

## Schedule

| Day | Tasks |
|-----|-------|
| Daily 9 PM | Fetch market data, write journal entry, commit to GitHub |
| Mon/Fri 10 PM | Build next model on the list |
| Thu 8 PM | Write and publish blog post |
| Sun 6 PM | Compile weekly journal summary |

---

## GitHub Structure

```
student-finance-portfolio/
├── models/          # Python + Excel files
├── ml/              # AI/ML projects
├── blog/posts/      # Markdown blog posts
├── journal/daily/   # Daily entries
└── journal/weekly/  # Weekly summaries
```

---

## Standards

**Code:** Include docstrings, example usage, and comments explaining the finance concepts. Add disclaimer on any predictive models.

**Blog:** Keep it student-friendly. Explain what it is, why it matters, how to use it.

**Journal:** Market recap, 1 thing learned, 1 fintech company spotted, questions to explore.

---

## Data Sources (free)
- `yfinance` for stock data
- `fredapi` for economic data
- SEC EDGAR for filings

---

## Watchlist
AAPL, MSFT, NVDA, JPM, SQ, PYPL, COIN + any company being modeled

---

*Use Sonnet 4.5 for everything. Don't commit broken code.*
