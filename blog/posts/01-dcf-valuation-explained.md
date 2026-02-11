# Understanding DCF Valuation: The Foundation of Stock Analysis

**Date:** February 11, 2026  
**Author:** Aiden Azoy

---

## What is DCF?

DCF stands for **Discounted Cash Flow**. It's one of the most fundamental valuation methods in finance. The core idea is simple: a company is worth the sum of all the cash it will generate in the future, adjusted for the time value of money.

## Why Does It Matter?

When you buy a stock, you're buying a piece of a business. But how do you know if the price is fair? DCF helps you calculate the **intrinsic value** of a company based on its fundamentals, not market hype.

## The Core Formula

```
Enterprise Value = Σ(FCF_t / (1 + WACC)^t) + Terminal Value
```

Let's break that down:

### 1. Free Cash Flow (FCF)
This is the cash a company generates after paying for operations and capital expenditures. It's the money available to investors.

```
FCF = Operating Cash Flow - Capital Expenditures
```

### 2. WACC (Weighted Average Cost of Capital)
This is your discount rate - essentially the return you'd need to justify the risk of investing in this company. Higher risk = higher WACC.

### 3. Terminal Value
Companies don't just stop after 5-10 years. Terminal value captures all the cash flows beyond your forecast period, assuming perpetual growth.

```
Terminal Value = FCF_final * (1 + g) / (WACC - g)
```

Where `g` is the terminal growth rate (usually 2-3%, roughly GDP growth).

## Step-by-Step Example

Let's say we're valuing a company:

**Given:**
- Current FCF: $100M
- Growth rate: 10% per year
- WACC: 10%
- Terminal growth: 2.5%
- Forecast period: 5 years

**Step 1: Project FCF**
- Year 1: $110M
- Year 2: $121M
- Year 3: $133.1M
- Year 4: $146.4M
- Year 5: $161M

**Step 2: Calculate Terminal Value**
```
TV = $161M * (1.025) / (0.10 - 0.025) = $2,201M
```

**Step 3: Discount Everything to Present Value**
- PV of Year 1 FCF: $110M / 1.10 = $100M
- PV of Year 2 FCF: $121M / 1.10² = $100M
- ... (continue for all years)
- PV of Terminal Value: $2,201M / 1.10⁵ = $1,366M

**Step 4: Sum It Up**
Enterprise Value = Sum of all PV cash flows ≈ $1,866M

**Step 5: Calculate Equity Value**
```
Equity Value = EV + Cash - Debt
Fair Value per Share = Equity Value / Shares Outstanding
```

## Common Pitfalls

1. **Garbage in, garbage out:** If your growth assumptions are wrong, your valuation is wrong.
2. **WACC is subjective:** Small changes in WACC can swing valuation significantly.
3. **Terminal value dominates:** Often 70-80% of the EV comes from terminal value. That's a lot riding on one assumption.

## When to Use DCF

**Good for:**
- Mature companies with predictable cash flows
- Understanding if a stock is over/undervalued
- Learning how different assumptions affect valuation

**Not great for:**
- Early-stage companies with no FCF
- Highly cyclical businesses
- Companies in disruption or turnaround

## The Big Picture

DCF isn't perfect. No model is. But it forces you to think about fundamentals:
- How much cash does this business actually generate?
- How fast can it grow?
- What's a fair price to pay for that?

Master DCF, and you'll understand valuation better than 90% of retail investors.

---

## Try It Yourself

I built a Python implementation of this model. Check it out in the `/models` folder. Run it on your favorite stocks and see what you learn.

**Disclaimer:** This is educational content, not investment advice. Always do your own research.

---

*Next up: Comparable Company Analysis - valuing businesses by comparing them to similar companies.*
