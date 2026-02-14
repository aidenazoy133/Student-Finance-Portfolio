"""
Comparable Company Analysis (Comps)

This is probably the most common valuation method on Wall Street.
The idea is simple: if similar companies trade at certain multiples,
your target company should too. It's like pricing a house by looking
at what neighbors' houses sold for.

Pretty straightforward but the tricky part is picking the RIGHT comps.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional


class CompAnalysis:
    """
    Runs a comparable company analysis.
    
    The basic workflow:
    1. Get financial data for comp companies
    2. Calculate their trading multiples (P/E, EV/EBITDA, etc.)
    3. Apply those multiples to your target company
    4. Get a valuation range
    """
    
    def __init__(self, target_ticker: str, comp_tickers: List[str]):
        """
        Initialize with your target company and a list of comps.
        
        Args:
            target_ticker: The company you're valuing (e.g., 'AAPL')
            comp_tickers: List of similar companies (e.g., ['MSFT', 'GOOGL'])
        """
        self.target_ticker = target_ticker
        self.comp_tickers = comp_tickers
        self.target_data = None
        self.comp_data = None
        
    def fetch_data(self):
        """
        Pull financial data from Yahoo Finance.
        
        This grabs key metrics like market cap, P/E, EV/EBITDA, etc.
        yfinance makes this pretty easy but sometimes data is missing
        so we need to handle that.
        """
        print(f"Fetching data for {self.target_ticker} and {len(self.comp_tickers)} comps...")
        
        # Get target company data
        target = yf.Ticker(self.target_ticker)
        self.target_data = self._extract_metrics(target, self.target_ticker)
        
        # Get comp company data
        comp_metrics = []
        for ticker in self.comp_tickers:
            try:
                comp = yf.Ticker(ticker)
                metrics = self._extract_metrics(comp, ticker)
                comp_metrics.append(metrics)
            except Exception as e:
                print(f"⚠️  Couldn't fetch {ticker}: {e}")
                # Skip this comp if data is broken
                continue
        
        self.comp_data = pd.DataFrame(comp_metrics)
        print(f"✓ Got data for {len(self.comp_data)} comps")
        
    def _extract_metrics(self, ticker_obj, ticker_name: str) -> Dict:
        """
        Pull out the metrics we care about from a yfinance Ticker object.
        
        Returns a dict with all the key multiples and financial metrics.
        Some of these might be None if data isn't available.
        """
        info = ticker_obj.info
        
        # Basic info
        metrics = {
            'ticker': ticker_name,
            'company': info.get('shortName', ticker_name),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
        }
        
        # Market data
        metrics['market_cap'] = info.get('marketCap')
        metrics['enterprise_value'] = info.get('enterpriseValue')
        metrics['price'] = info.get('currentPrice')
        
        # Valuation multiples - these are the important ones
        metrics['pe_ratio'] = info.get('trailingPE')
        metrics['forward_pe'] = info.get('forwardPE')
        metrics['peg_ratio'] = info.get('pegRatio')
        metrics['price_to_book'] = info.get('priceToBook')
        metrics['price_to_sales'] = info.get('priceToSalesTrailing12Months')
        metrics['ev_to_revenue'] = info.get('enterpriseToRevenue')
        metrics['ev_to_ebitda'] = info.get('enterpriseToEbitda')
        
        # Growth & profitability metrics
        metrics['revenue_growth'] = info.get('revenueGrowth')
        metrics['profit_margin'] = info.get('profitMargins')
        metrics['roe'] = info.get('returnOnEquity')
        
        # Financial health
        metrics['debt_to_equity'] = info.get('debtToEquity')
        metrics['current_ratio'] = info.get('currentRatio')
        
        return metrics
    
    def calculate_multiples(self) -> pd.DataFrame:
        """
        Calculate summary statistics for the comp group.
        
        This gives us mean, median, min, max for each multiple.
        Usually we use median because it's less affected by outliers.
        """
        if self.comp_data is None:
            raise ValueError("Need to fetch_data() first!")
        
        # Columns we want to analyze (the actual multiples)
        multiple_cols = [
            'pe_ratio', 'forward_pe', 'peg_ratio', 
            'price_to_book', 'price_to_sales',
            'ev_to_revenue', 'ev_to_ebitda'
        ]
        
        # Calculate stats for each multiple
        stats = []
        for col in multiple_cols:
            # Drop NaN values before calculating stats
            values = self.comp_data[col].dropna()
            
            if len(values) == 0:
                # No data available for this multiple
                stats.append({
                    'multiple': col,
                    'mean': None,
                    'median': None,
                    'min': None,
                    'max': None,
                    'std': None,
                    'count': 0
                })
            else:
                stats.append({
                    'multiple': col,
                    'mean': values.mean(),
                    'median': values.median(),
                    'min': values.min(),
                    'max': values.max(),
                    'std': values.std(),
                    'count': len(values)
                })
        
        return pd.DataFrame(stats)
    
    def value_target(self, method: str = 'median') -> Dict:
        """
        Value the target company using comp multiples.
        
        Args:
            method: 'mean', 'median', 'min', or 'max' - which comp stat to use
        
        Returns:
            Dict with implied valuations from each multiple
        
        The tricky part: different multiples can give wildly different values.
        That's why you usually look at a range and use judgment.
        """
        if self.target_data is None or self.comp_data is None:
            raise ValueError("Need to fetch_data() first!")
        
        stats = self.calculate_multiples()
        valuations = {'method': method, 'valuations': {}}
        
        # For each multiple, apply it to the target's metric
        for _, row in stats.iterrows():
            multiple_name = row['multiple']
            comp_multiple = row[method]
            
            if comp_multiple is None or pd.isna(comp_multiple):
                continue
            
            # Figure out what metric to multiply by
            # This is a bit messy but it's how the mapping works
            if multiple_name == 'pe_ratio':
                # Need EPS to get market cap
                eps = self.target_data.get('price') / self.target_data.get('pe_ratio') if self.target_data.get('pe_ratio') else None
                if eps:
                    implied_price = comp_multiple * eps
                    valuations['valuations']['PE'] = {
                        'implied_price': implied_price,
                        'comp_multiple': comp_multiple,
                        'current_price': self.target_data.get('price')
                    }
            
            elif multiple_name == 'price_to_book':
                # Need book value per share
                bvps = self.target_data.get('price') / self.target_data.get('price_to_book') if self.target_data.get('price_to_book') else None
                if bvps:
                    implied_price = comp_multiple * bvps
                    valuations['valuations']['P/B'] = {
                        'implied_price': implied_price,
                        'comp_multiple': comp_multiple,
                        'current_price': self.target_data.get('price')
                    }
            
            elif multiple_name == 'ev_to_ebitda':
                # This one's at enterprise value level, not equity
                target_ev_ebitda = self.target_data.get('ev_to_ebitda')
                if target_ev_ebitda:
                    # Implied EV based on comp multiple
                    target_ebitda = self.target_data.get('enterprise_value') / target_ev_ebitda
                    implied_ev = comp_multiple * target_ebitda
                    valuations['valuations']['EV/EBITDA'] = {
                        'implied_ev': implied_ev,
                        'comp_multiple': comp_multiple,
                        'current_ev': self.target_data.get('enterprise_value')
                    }
        
        return valuations
    
    def generate_report(self) -> str:
        """
        Create a readable summary report.
        
        This is what you'd put in a presentation or email.
        """
        if self.target_data is None:
            return "No data available. Run fetch_data() first."
        
        report = []
        report.append("=" * 60)
        report.append(f"COMPARABLE COMPANY ANALYSIS: {self.target_ticker}")
        report.append("=" * 60)
        report.append("")
        
        # Target company overview
        report.append("TARGET COMPANY:")
        report.append(f"  {self.target_data['company']} ({self.target_ticker})")
        report.append(f"  Sector: {self.target_data['sector']}")
        report.append(f"  Industry: {self.target_data['industry']}")
        report.append(f"  Current Price: ${self.target_data.get('price', 'N/A'):.2f}" if self.target_data.get('price') else "  Current Price: N/A")
        report.append(f"  Market Cap: ${self.target_data.get('market_cap', 0)/1e9:.2f}B" if self.target_data.get('market_cap') else "  Market Cap: N/A")
        report.append("")
        
        # Comp group summary
        report.append("COMP GROUP:")
        report.append(f"  {len(self.comp_data)} comparable companies")
        for _, comp in self.comp_data.iterrows():
            report.append(f"  - {comp['ticker']}: {comp['company']}")
        report.append("")
        
        # Multiple analysis
        report.append("TRADING MULTIPLES (Comp Group Median):")
        stats = self.calculate_multiples()
        for _, row in stats.iterrows():
            if row['median'] and not pd.isna(row['median']):
                report.append(f"  {row['multiple']}: {row['median']:.2f}x")
        report.append("")
        
        # Valuation summary
        report.append("IMPLIED VALUATION (using median comps):")
        try:
            valuations = self.value_target('median')
            current_price = self.target_data.get('price', 0)
            
            for metric, data in valuations['valuations'].items():
                if 'implied_price' in data:
                    implied = data['implied_price']
                    upside = ((implied / current_price) - 1) * 100 if current_price else 0
                    report.append(f"  {metric}: ${implied:.2f} ({upside:+.1f}% vs current)")
                elif 'implied_ev' in data:
                    implied = data['implied_ev']
                    current = data['current_ev']
                    upside = ((implied / current) - 1) * 100 if current else 0
                    report.append(f"  {metric}: ${implied/1e9:.2f}B EV ({upside:+.1f}% vs current)")
        except Exception as e:
            report.append(f"  Could not calculate: {e}")
        
        report.append("")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def export_to_excel(self, filename: str):
        """
        Export the analysis to Excel for further work.
        
        Pretty useful for presentations or when your boss wants to tweak assumptions.
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Comp data
            self.comp_data.to_excel(writer, sheet_name='Comp_Companies', index=False)
            
            # Summary stats
            stats = self.calculate_multiples()
            stats.to_excel(writer, sheet_name='Multiple_Stats', index=False)
            
            # Target data as DataFrame
            target_df = pd.DataFrame([self.target_data])
            target_df.to_excel(writer, sheet_name='Target_Company', index=False)
        
        print(f"✓ Exported to {filename}")


def example_usage():
    """
    Example: Value Square (SQ) using fintech comps.
    
    This is a realistic scenario - valuing a fintech company
    using other payment processors and fintechs as comps.
    """
    print("Example: Valuing Square (SQ) using fintech comps\n")
    
    # Define target and comps
    target = 'SQ'
    comps = ['PYPL', 'ADYEY', 'FIS', 'FISV']  # PayPal, Adyen, Fiserv, etc.
    
    # Run the analysis
    analysis = CompAnalysis(target, comps)
    analysis.fetch_data()
    
    # Print report
    print(analysis.generate_report())
    
    # Could also export to Excel
    # analysis.export_to_excel('sq_comp_analysis.xlsx')


if __name__ == '__main__':
    example_usage()
