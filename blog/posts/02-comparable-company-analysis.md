# Comparable Company Analysis: The Shortcut to Valuation

**Date:** February 12, 2026  
**Author:** Aiden Azoy

---

Last time we talked about DCF - the "theoretical" way to value a company. Today? We're doing comps. It's faster, it's messier, and honestly, it's what most people actually use.

## The Basic Idea

Instead of building a whole cash flow model, you just look at what similar companies are trading for. If Netflix trades at 30x earnings and Disney trades at 25x earnings, maybe your streaming startup should be valued somewhere in that range.

Think of it like buying a house. You don't calculate the present value of every future year of shelter. You look at what similar houses in the neighborhood sold for. That's comps.

## Why Comps Are Useful

DCF requires like 20 assumptions. Growth rates, discount rates, terminal values... one wrong number and your valuation is off by 50%.

Comps? Way simpler:
1. Find similar companies
2. See what multiples they trade at
3. Apply those multiples to your company

It's not perfect, but it's fast and grounded in what the market actually pays.

## The Key Multiples

### P/E Ratio (Price to Earnings)

```
P/E = Stock Price / Earnings Per Share
```

Most common multiple. If Apple trades at 30x earnings and makes $6/share, the stock "should" be $180.

**The catch:** What if earnings are weird this year? One-time charges? Accounting tricks? P/E can be misleading.

### EV/EBITDA (Enterprise Value to EBITDA)

```
EV/EBITDA = (Market Cap + Debt - Cash) / EBITDA
```

I think this is better than P/E for most purposes. EBITDA (Earnings Before Interest, Taxes, Depreciation, Amortization) strips out a lot of accounting noise and shows how the core business is doing.

Also, using Enterprise Value instead of just market cap means you're comparing companies with different debt levels fairly.

### Price to Sales (P/S)

```
P/S = Market Cap / Revenue
```

Useful when companies aren't profitable yet (looking at you, tech startups). If they're growing fast but burning cash, P/S lets you compare them anyway.

### Price to Book (P/B)

```
P/B = Stock Price / Book Value Per Share
```

Good for banks and asset-heavy businesses. Not so great for tech companies where most value is intangible.

## How to Actually Do It

Let's say you want to value... I don't know, a hypothetical coffee chain.

**Step 1: Pick Your Comps**

Find similar companies. For a coffee chain, maybe:
- Starbucks
- Dutch Bros
- Luckin Coffee (if you're feeling spicy)

You want companies that:
- Are in the same industry
- Have similar business models
- Are at a similar stage (don't compare a startup to Apple)
- Operate in similar markets

**Step 2: Pull the Data**

Get their financial info. For each comp, calculate:
- P/E ratio
- EV/EBITDA
- P/S ratio
- Whatever else is relevant

Let's say you get:

| Company | P/E | EV/EBITDA | P/S |
|---------|-----|-----------|-----|
| Starbucks | 28 | 18 | 2.5 |
| Dutch Bros | 35 | 45 | 4.0 |
| Luckin Coffee | 22 | 12 | 1.8 |

**Step 3: Calculate the Median**

Don't use the average - one outlier will mess you up. Use the median.

- Median P/E: 28
- Median EV/EBITDA: 18
- Median P/S: 2.5

**Step 4: Apply to Your Company**

If your coffee chain has:
- Earnings: $100M
- EBITDA: $150M
- Revenue: $800M

Then implied valuations:
- Using P/E: $100M × 28 = $2.8B market cap
- Using EV/EBITDA: $150M × 18 = $2.7B enterprise value
- Using P/S: $800M × 2.5 = $2.0B market cap

**Step 5: Triangulate**

You've got a range. Maybe $2.0B to $2.8B is reasonable. Now think about why your company might deserve to be at the high or low end of that range.

Growing faster than peers? High end.  
Worse margins? Low end.  
Better brand? High end.

## What Can Go Wrong

### 1. Picking Bad Comps

If you compare a luxury brand to a discount retailer, your valuation will be garbage. Really think about whether companies are actually comparable.

### 2. Different Accounting

One company capitalizes R&D, another expenses it. Their earnings look different even if the business is the same. Be careful.

### 3. Market Timing

What if the whole sector is overvalued? Comps will tell you a stock is "fairly valued" when really everything is in a bubble. Remember 2021 tech stocks?

### 4. One-Time Events

If a company just had a massive writedown or windfall gain, their multiples will look weird. Adjust for that or use normalized figures.

## DCF vs Comps: When to Use What

I think DCF is better when:
- You're doing serious analysis and have time
- The company has stable, predictable cash flows
- You want to understand the business deeply

Comps are better when:
- You need a quick sanity check
- You're valuing a private company for an acquisition
- You want to see how the market is pricing similar companies

Honestly? Use both. DCF gives you the "intrinsic value," comps tell you what the market will actually pay. The gap between them is interesting.

## Real World Example

Tesla trades at like 60x earnings. Traditional automakers trade at 6x earnings. Which is "right"?

DCF says: depends on whether Tesla can maintain hypergrowth and become an AI/energy company.

Comps say: if it's just a car company, it's wildly overvalued. If it's a tech company, maybe it's fine.

The confusing part is Tesla is kind of both. That's why valuation is an art, not a science.

## Try It Yourself

Pick a public company you're interested in. Find 3-5 good comps. Calculate P/E, EV/EBITDA, and P/S for all of them. See if your target company looks cheap or expensive relative to peers.

You might be surprised. Sometimes "expensive" stocks are actually cheap compared to their industry, and vice versa.

---

## Next Up

I'm thinking about writing about financial statements next - how to actually read a 10-K without falling asleep. Or maybe something about margin of safety and position sizing. Let me know if you have preferences.

**Disclaimer:** Educational content, not investment advice. I'm a high school student learning this stuff, not a CFA.

---

*P.S. - If you want to see Python code for pulling comp data automatically, check the models folder. I'm working on a screener that does this at scale.*
