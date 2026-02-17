"""
LBO (Leveraged Buyout) Model

This models how private equity firms buy companies using mostly borrowed money,
run them for a few years, and then sell them for (hopefully) a profit.

The basic idea:
1. Buy a company with ~30% equity, 70% debt
2. Use the company's cash flow to pay down debt over 5-7 years
3. Sell the company (the "exit")
4. Calculate your return (IRR and money multiple)

Key metrics:
- IRR (Internal Rate of Return): Annual return percentage
- MoM (Money on Money): How many times you multiplied your investment

⚠️ DISCLAIMER: Educational purposes only. Not investment advice.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime


class LBOModel:
    """
    Leveraged Buyout financial model.
    
    This calculates returns from a hypothetical PE acquisition.
    Pretty straightforward once you understand the debt paydown logic.
    """
    
    def __init__(self, ticker, entry_multiple=10.0, exit_multiple=10.0, 
                 debt_ratio=0.70, holding_period=5, interest_rate=0.06):
        """
        Set up the LBO with acquisition assumptions.
        
        Args:
            ticker (str): Company ticker symbol
            entry_multiple (float): Purchase price as multiple of EBITDA (typically 8-12x)
            exit_multiple (float): Sale price as multiple of EBITDA (typically 8-12x)
            debt_ratio (float): % of purchase price financed with debt (typically 60-80%)
            holding_period (int): Years until exit (typically 5-7)
            interest_rate (float): Interest rate on debt (typically 5-8%)
        """
        self.ticker = ticker.upper()
        self.entry_multiple = entry_multiple
        self.exit_multiple = exit_multiple
        self.debt_ratio = debt_ratio
        self.equity_ratio = 1 - debt_ratio
        self.holding_period = holding_period
        self.interest_rate = interest_rate
        self.stock = yf.Ticker(self.ticker)
        
    def get_current_ebitda(self):
        """
        Pull the most recent EBITDA from financial statements.
        
        EBITDA = Earnings Before Interest, Taxes, Depreciation, and Amortization
        It's basically operating profit before all the accounting stuff.
        PE firms love it because it shows pure business performance.
        
        Returns:
            float: Most recent annual EBITDA
        """
        income_stmt = self.stock.financials
        
        # Try to get EBITDA directly
        if 'EBITDA' in income_stmt.index:
            ebitda = income_stmt.loc['EBITDA'].iloc[0]
        else:
            # Calculate it: EBIT + D&A
            ebit = income_stmt.loc['EBIT'].iloc[0]
            
            # Get D&A from cash flow statement
            cash_flow = self.stock.cashflow
            if 'Depreciation And Amortization' in cash_flow.index:
                da = cash_flow.loc['Depreciation And Amortization'].iloc[0]
            else:
                # Rough estimate: ~5% of revenue
                revenue = income_stmt.loc['Total Revenue'].iloc[0]
                da = revenue * 0.05
            
            ebitda = ebit + da
        
        return ebitda
    
    def get_cash_flow_metrics(self):
        """
        Get metrics we need for projections.
        
        The tricky part here is figuring out how much cash the business
        actually generates after maintaining itself (capex, working capital, etc).
        """
        cash_flow = self.stock.cashflow
        income_stmt = self.stock.financials
        
        # Operating cash flow
        ocf = cash_flow.loc['Operating Cash Flow'].iloc[0]
        
        # Capital expenditures (money spent on equipment, facilities, etc)
        capex = abs(cash_flow.loc['Capital Expenditure'].iloc[0])
        
        # Free cash flow = what's left after keeping the lights on
        fcf = ocf - capex
        
        # Revenue for growth calculations
        revenue = income_stmt.loc['Total Revenue'].iloc[0]
        
        # Historical revenue growth
        revenue_series = income_stmt.loc['Total Revenue']
        growth_rates = revenue_series.pct_change().dropna()
        avg_growth = growth_rates.median()
        
        # Keep it reasonable - cap between -5% and 15%
        avg_growth = max(min(avg_growth, 0.15), -0.05)
        
        return {
            'ocf': ocf,
            'capex': capex,
            'fcf': fcf,
            'revenue': revenue,
            'revenue_growth': avg_growth
        }
    
    def calculate_purchase_price(self, ebitda):
        """
        Calculate what we're paying for the company.
        
        Purchase Price = EBITDA × Entry Multiple
        Simple multiplication, but this is where the deal starts.
        
        Args:
            ebitda (float): Current EBITDA
            
        Returns:
            dict: Purchase price breakdown
        """
        purchase_price = ebitda * self.entry_multiple
        debt_financing = purchase_price * self.debt_ratio
        equity_investment = purchase_price * self.equity_ratio
        
        return {
            'purchase_price': purchase_price,
            'debt': debt_financing,
            'equity': equity_investment
        }
    
    def project_financials(self, base_ebitda, revenue_growth):
        """
        Project EBITDA and cash flows over the holding period.
        
        We're assuming EBITDA grows with revenue. Not perfect,
        but reasonable for a quick model.
        
        Args:
            base_ebitda (float): Starting EBITDA
            revenue_growth (float): Annual revenue growth rate
            
        Returns:
            list: Projected EBITDA for each year
        """
        projections = []
        current_ebitda = base_ebitda
        
        for year in range(self.holding_period):
            # EBITDA grows with revenue (simplification)
            current_ebitda = current_ebitda * (1 + revenue_growth)
            projections.append(current_ebitda)
        
        return projections
    
    def calculate_debt_schedule(self, initial_debt, ebitda_projections):
        """
        Figure out how we pay down the debt over time.
        
        Here's the key: we use free cash flow to pay down debt each year.
        Less debt = less interest expense = more cash to pay down debt.
        It's a virtuous cycle (hopefully).
        
        Args:
            initial_debt (float): Debt at acquisition
            ebitda_projections (list): Projected EBITDA each year
            
        Returns:
            pd.DataFrame: Year-by-year debt schedule
        """
        schedule = []
        remaining_debt = initial_debt
        
        for year, ebitda in enumerate(ebitda_projections, 1):
            # Interest expense on remaining debt
            interest_expense = remaining_debt * self.interest_rate
            
            # Rough FCF estimate: EBITDA - capex - taxes - interest
            # Using ~40% of EBITDA as FCF (industry average)
            fcf = ebitda * 0.40
            
            # Cash available for debt paydown = FCF - interest
            cash_for_debt = fcf - interest_expense
            
            # Pay down as much debt as we can
            debt_paydown = min(cash_for_debt, remaining_debt)
            remaining_debt = max(0, remaining_debt - debt_paydown)
            
            schedule.append({
                'year': year,
                'beginning_debt': remaining_debt + debt_paydown,
                'ebitda': ebitda,
                'fcf': fcf,
                'interest_expense': interest_expense,
                'debt_paydown': debt_paydown,
                'ending_debt': remaining_debt
            })
        
        return pd.DataFrame(schedule)
    
    def calculate_exit_value(self, exit_ebitda, remaining_debt):
        """
        Calculate what we sell the company for and our returns.
        
        Exit Enterprise Value = Exit EBITDA × Exit Multiple
        Equity Proceeds = EV - Remaining Debt
        
        Then we calculate IRR and MoM to see if we made money.
        
        Args:
            exit_ebitda (float): EBITDA in the exit year
            remaining_debt (float): Debt left at exit
            
        Returns:
            dict: Exit value and returns
        """
        exit_ev = exit_ebitda * self.exit_multiple
        equity_proceeds = exit_ev - remaining_debt
        
        return {
            'exit_ev': exit_ev,
            'remaining_debt': remaining_debt,
            'equity_proceeds': equity_proceeds
        }
    
    def calculate_returns(self, equity_investment, equity_proceeds):
        """
        Calculate IRR (Internal Rate of Return) and MoM (Money on Money).
        
        IRR = annualized return percentage
        MoM = total multiple (2.5x means you got $2.50 back for every $1 invested)
        
        Args:
            equity_investment (float): Initial equity check
            equity_proceeds (float): Cash back at exit
            
        Returns:
            dict: Return metrics
        """
        # Money on Money = Exit Proceeds / Initial Investment
        mom = equity_proceeds / equity_investment if equity_investment > 0 else 0
        
        # IRR calculation: (Exit/Entry)^(1/years) - 1
        irr = (mom ** (1/self.holding_period)) - 1 if mom > 0 else -1
        
        return {
            'mom': mom,
            'irr': irr
        }
    
    def run_lbo(self):
        """
        Run the full LBO analysis from acquisition to exit.
        
        This ties everything together: buy it, run it, sell it, calculate returns.
        
        Returns:
            dict: Complete LBO results
        """
        # Get current financials
        current_ebitda = self.get_current_ebitda()
        cf_metrics = self.get_cash_flow_metrics()
        
        # Calculate purchase
        purchase = self.calculate_purchase_price(current_ebitda)
        
        # Project operations
        ebitda_projections = self.project_financials(
            current_ebitda, 
            cf_metrics['revenue_growth']
        )
        
        # Build debt schedule
        debt_schedule = self.calculate_debt_schedule(
            purchase['debt'], 
            ebitda_projections
        )
        
        # Calculate exit
        exit_ebitda = ebitda_projections[-1]
        remaining_debt = debt_schedule['ending_debt'].iloc[-1]
        exit_value = self.calculate_exit_value(exit_ebitda, remaining_debt)
        
        # Calculate returns
        returns = self.calculate_returns(
            purchase['equity'],
            exit_value['equity_proceeds']
        )
        
        return {
            'ticker': self.ticker,
            'current_ebitda': current_ebitda,
            'purchase': purchase,
            'ebitda_projections': ebitda_projections,
            'debt_schedule': debt_schedule,
            'exit': exit_value,
            'returns': returns,
            'assumptions': {
                'entry_multiple': self.entry_multiple,
                'exit_multiple': self.exit_multiple,
                'debt_ratio': self.debt_ratio,
                'holding_period': self.holding_period,
                'interest_rate': self.interest_rate,
                'revenue_growth': cf_metrics['revenue_growth']
            }
        }
    
    def generate_report(self):
        """
        Generate a formatted LBO analysis report.
        
        Returns:
            str: Formatted report text
        """
        results = self.run_lbo()
        
        report = f"""
{'='*70}
LBO MODEL: {results['ticker']}
{'='*70}
Date: {datetime.now().strftime('%Y-%m-%d')}

TRANSACTION ASSUMPTIONS
-----------------------
Entry Multiple: {results['assumptions']['entry_multiple']:.1f}x EBITDA
Exit Multiple: {results['assumptions']['exit_multiple']:.1f}x EBITDA
Debt Financing: {results['assumptions']['debt_ratio']*100:.0f}%
Equity Financing: {(1-results['assumptions']['debt_ratio'])*100:.0f}%
Interest Rate: {results['assumptions']['interest_rate']*100:.1f}%
Holding Period: {results['assumptions']['holding_period']} years

PURCHASE PRICE
--------------
Current EBITDA: ${results['current_ebitda']:,.0f}
Purchase Price: ${results['purchase']['purchase_price']:,.0f}
  Debt Financing: ${results['purchase']['debt']:,.0f}
  Equity Investment: ${results['purchase']['equity']:,.0f}

PROJECTED EBITDA
----------------
"""
        for i, ebitda in enumerate(results['ebitda_projections'], 1):
            report += f"Year {i}: ${ebitda:,.0f}\n"
        
        report += f"""
DEBT PAYDOWN SCHEDULE
---------------------
{results['debt_schedule'].to_string(index=False, float_format=lambda x: f'${x:,.0f}')}

EXIT VALUE
----------
Exit EBITDA (Year {results['assumptions']['holding_period']}): ${results['ebitda_projections'][-1]:,.0f}
Exit Enterprise Value: ${results['exit']['exit_ev']:,.0f}
Less: Remaining Debt: ${results['exit']['remaining_debt']:,.0f}
Equity Proceeds: ${results['exit']['equity_proceeds']:,.0f}

RETURNS ANALYSIS
----------------
Initial Equity Investment: ${results['purchase']['equity']:,.0f}
Equity Proceeds at Exit: ${results['exit']['equity_proceeds']:,.0f}

Money on Money (MoM): {results['returns']['mom']:.2f}x
Internal Rate of Return (IRR): {results['returns']['irr']*100:.1f}%

INTERPRETATION
--------------
"""
        mom = results['returns']['mom']
        irr = results['returns']['irr']
        
        if irr >= 0.25:
            report += "🔥 Excellent returns! This would be a home run deal for PE.\n"
        elif irr >= 0.20:
            report += "✅ Strong returns. Most PE firms would be happy with this.\n"
        elif irr >= 0.15:
            report += "📊 Decent returns. Probably investable, but not amazing.\n"
        else:
            report += "⚠️  Weak returns. Most PE firms target >20% IRR.\n"
        
        report += f"""
{'='*70}
⚠️  DISCLAIMER: This is educational only. Actual LBO models are way
    more complex (multiple debt tranches, management rollover, etc).
    Not investment advice. Do your own research.
{'='*70}
"""
        return report


def main():
    """
    Example usage: run an LBO analysis on a company.
    """
    print("LBO Model - Example\n")
    print("This models a private equity buyout of a public company.")
    print("We'll assume typical PE deal terms and calculate returns.\n")
    
    ticker = input("Enter stock ticker (e.g., TGT for Target): ").strip().upper()
    
    if not ticker:
        ticker = "TGT"
        print(f"Using default: {ticker} (Target Corporation)")
    
    print("\nRunning LBO analysis...")
    print("(This uses real financials with hypothetical deal terms)\n")
    
    try:
        # Create LBO model with typical PE assumptions
        lbo = LBOModel(
            ticker=ticker,
            entry_multiple=10.0,    # Buying at 10x EBITDA
            exit_multiple=10.0,     # Selling at 10x EBITDA
            debt_ratio=0.65,        # 65% debt, 35% equity
            holding_period=5,       # 5 year hold
            interest_rate=0.06      # 6% interest on debt
        )
        
        report = lbo.generate_report()
        print(report)
        
        # Show sensitivity
        print("\nWant to test different assumptions?")
        print("Try modifying entry_multiple, exit_multiple, or debt_ratio in the code!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("- You have internet connection")
        print("- The ticker is valid")
        print("- The company has financial data available")


if __name__ == "__main__":
    main()
