"""
DCF (Discounted Cash Flow) Valuation Model

A DCF model values a company by projecting its future cash flows and discounting 
them back to present value using the weighted average cost of capital (WACC).

Formula:
    Enterprise Value = Σ(FCF_t / (1 + WACC)^t) + Terminal Value / (1 + WACC)^n
    
Where:
    - FCF = Free Cash Flow
    - WACC = Weighted Average Cost of Capital
    - t = time period
    - n = forecast period (typically 5-10 years)

⚠️ DISCLAIMER: Educational purposes only. Not financial advice.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime


class DCFModel:
    """
    Discounted Cash Flow valuation model.
    
    Attributes:
        ticker (str): Stock ticker symbol
        forecast_years (int): Number of years to project cash flows
        terminal_growth_rate (float): Perpetual growth rate assumption
        wacc (float): Weighted Average Cost of Capital
    """
    
    def __init__(self, ticker, forecast_years=5, terminal_growth_rate=0.025, wacc=0.10):
        """
        Initialize DCF model with company ticker and assumptions.
        
        Args:
            ticker (str): Stock ticker (e.g., 'AAPL')
            forecast_years (int): Years to forecast (default 5)
            terminal_growth_rate (float): Terminal growth rate (default 2.5%)
            wacc (float): Discount rate (default 10%)
        """
        self.ticker = ticker.upper()
        self.forecast_years = forecast_years
        self.terminal_growth_rate = terminal_growth_rate
        self.wacc = wacc
        self.stock = yf.Ticker(self.ticker)
        
    def get_historical_fcf(self):
        """
        Fetch historical Free Cash Flow from financial statements.
        
        Returns:
            pd.Series: Historical FCF values
        """
        cash_flow = self.stock.cashflow
        if 'Free Cash Flow' in cash_flow.index:
            fcf = cash_flow.loc['Free Cash Flow']
        else:
            # Calculate FCF = Operating Cash Flow - Capital Expenditures
            ocf = cash_flow.loc['Operating Cash Flow']
            capex = cash_flow.loc['Capital Expenditure']
            fcf = ocf + capex  # capex is negative
        
        return fcf.sort_index()
    
    def calculate_fcf_growth_rate(self, fcf_historical):
        """
        Calculate average historical FCF growth rate.
        
        Args:
            fcf_historical (pd.Series): Historical FCF values
            
        Returns:
            float: Average growth rate
        """
        if len(fcf_historical) < 2:
            return 0.05  # Default 5% if insufficient data
        
        # Calculate year-over-year growth rates
        growth_rates = fcf_historical.pct_change().dropna()
        
        # Use median to avoid outliers
        median_growth = growth_rates.median()
        
        # Cap growth rate at reasonable levels
        return max(min(median_growth, 0.25), -0.10)  # Between -10% and 25%
    
    def project_fcf(self, base_fcf, growth_rate):
        """
        Project future free cash flows.
        
        Args:
            base_fcf (float): Most recent FCF
            growth_rate (float): Annual growth rate
            
        Returns:
            list: Projected FCF for each year
        """
        projections = []
        current_fcf = base_fcf
        
        for year in range(1, self.forecast_years + 1):
            current_fcf = current_fcf * (1 + growth_rate)
            projections.append(current_fcf)
        
        return projections
    
    def calculate_terminal_value(self, final_fcf):
        """
        Calculate terminal value using perpetuity growth method.
        
        Formula: TV = FCF_final * (1 + g) / (WACC - g)
        
        Args:
            final_fcf (float): Final year projected FCF
            
        Returns:
            float: Terminal value
        """
        return final_fcf * (1 + self.terminal_growth_rate) / (self.wacc - self.terminal_growth_rate)
    
    def discount_cash_flows(self, cash_flows):
        """
        Discount projected cash flows to present value.
        
        Args:
            cash_flows (list): Future cash flows to discount
            
        Returns:
            list: Present values of each cash flow
        """
        pv_cash_flows = []
        
        for t, cf in enumerate(cash_flows, start=1):
            pv = cf / ((1 + self.wacc) ** t)
            pv_cash_flows.append(pv)
        
        return pv_cash_flows
    
    def calculate_enterprise_value(self):
        """
        Calculate enterprise value using DCF method.
        
        Returns:
            dict: Valuation results including EV, equity value, share price
        """
        # Get historical data
        fcf_historical = self.get_historical_fcf()
        base_fcf = fcf_historical.iloc[-1]  # Most recent FCF
        growth_rate = self.calculate_fcf_growth_rate(fcf_historical)
        
        # Project future FCF
        projected_fcf = self.project_fcf(base_fcf, growth_rate)
        
        # Calculate terminal value
        terminal_value = self.calculate_terminal_value(projected_fcf[-1])
        
        # Discount all cash flows
        pv_fcf = self.discount_cash_flows(projected_fcf)
        pv_terminal_value = terminal_value / ((1 + self.wacc) ** self.forecast_years)
        
        # Enterprise value
        enterprise_value = sum(pv_fcf) + pv_terminal_value
        
        # Get balance sheet data for equity value calculation
        balance_sheet = self.stock.balance_sheet
        try:
            cash = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
        except:
            cash = 0
        
        try:
            debt = balance_sheet.loc['Total Debt'].iloc[0]
        except:
            debt = 0
        
        # Equity value = EV + Cash - Debt
        equity_value = enterprise_value + cash - debt
        
        # Get shares outstanding
        info = self.stock.info
        shares_outstanding = info.get('sharesOutstanding', 0)
        
        # Calculate intrinsic value per share
        intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        # Current market price
        current_price = info.get('currentPrice', 0)
        
        # Upside/downside
        upside = ((intrinsic_value_per_share - current_price) / current_price * 100) if current_price > 0 else 0
        
        return {
            'ticker': self.ticker,
            'base_fcf': base_fcf,
            'fcf_growth_rate': growth_rate,
            'projected_fcf': projected_fcf,
            'terminal_value': terminal_value,
            'pv_terminal_value': pv_terminal_value,
            'enterprise_value': enterprise_value,
            'cash': cash,
            'debt': debt,
            'equity_value': equity_value,
            'shares_outstanding': shares_outstanding,
            'intrinsic_value_per_share': intrinsic_value_per_share,
            'current_price': current_price,
            'upside_downside_pct': upside,
            'wacc': self.wacc,
            'terminal_growth_rate': self.terminal_growth_rate
        }
    
    def generate_report(self):
        """
        Generate a formatted valuation report.
        
        Returns:
            str: Formatted report text
        """
        results = self.calculate_enterprise_value()
        
        report = f"""
{'='*60}
DCF VALUATION REPORT: {results['ticker']}
{'='*60}
Date: {datetime.now().strftime('%Y-%m-%d')}

ASSUMPTIONS
-----------
WACC (Discount Rate): {results['wacc']*100:.2f}%
Terminal Growth Rate: {results['terminal_growth_rate']*100:.2f}%
Forecast Period: {self.forecast_years} years

CASH FLOW ANALYSIS
------------------
Base FCF (Most Recent): ${results['base_fcf']:,.0f}
Historical Growth Rate: {results['fcf_growth_rate']*100:.2f}%

Projected FCF:
"""
        for i, fcf in enumerate(results['projected_fcf'], 1):
            report += f"  Year {i}: ${fcf:,.0f}\n"
        
        report += f"""
VALUATION
---------
Terminal Value: ${results['terminal_value']:,.0f}
PV of Terminal Value: ${results['pv_terminal_value']:,.0f}
Enterprise Value: ${results['enterprise_value']:,.0f}

EQUITY VALUE CALCULATION
------------------------
Enterprise Value: ${results['enterprise_value']:,.0f}
(+) Cash: ${results['cash']:,.0f}
(-) Debt: ${results['debt']:,.0f}
= Equity Value: ${results['equity_value']:,.0f}

PER SHARE VALUATION
-------------------
Shares Outstanding: {results['shares_outstanding']:,.0f}
Intrinsic Value per Share: ${results['intrinsic_value_per_share']:.2f}
Current Market Price: ${results['current_price']:.2f}
Upside/(Downside): {results['upside_downside_pct']:.2f}%

{'='*60}
⚠️  DISCLAIMER: This is for educational purposes only.
    Not financial advice. Always do your own research.
{'='*60}
"""
        return report


def main():
    """
    Example usage of the DCF model.
    """
    # Example: Value Apple Inc.
    print("DCF Valuation Model - Example\n")
    
    ticker = input("Enter stock ticker (e.g., AAPL): ").strip().upper()
    
    if not ticker:
        ticker = "AAPL"
        print(f"Using default ticker: {ticker}")
    
    print("\nRunning DCF analysis...\n")
    
    try:
        dcf = DCFModel(ticker=ticker, forecast_years=5, wacc=0.10, terminal_growth_rate=0.025)
        report = dcf.generate_report()
        print(report)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have an internet connection and the ticker is valid.")


if __name__ == "__main__":
    main()
