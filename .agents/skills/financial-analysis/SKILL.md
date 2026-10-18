---
name: financial-analysis
description: "Comprehensive financial, equity, and market analysis skill. Covers fundamental valuation (DCF, P/E, P/B, EV/EBITDA, ROE, ROCE), financial statement analysis (Balance Sheet, Income Statement, Cash Flows), technical indicators (RSI, MACD, Moving Averages, Bollinger Bands), IPO analysis (DRHP/RHP review, valuation multiples, subscription metrics), and portfolio risk metrics (Sharpe, Sortino, Beta, Max Drawdown). Activate whenever performing stock market research, valuation modeling, or fintech analytics."
version: 1.0.0
triggers:
  - financial analysis
  - stock analysis
  - valuation
  - balance sheet
  - income statement
  - cash flow
  - ipo analysis
  - fundamental analysis
  - technical analysis
  - trading strategy
  - financial metrics
---

# Financial Analysis & Valuation Skill

This skill provides institutional-grade analytical frameworks for corporate finance, equity valuation, market data analysis, and IPO evaluation.

## 1. Fundamental Equity & Financial Statement Analysis

### Three-Statement Integration
- **Income Statement**: Revenue growth, Gross/EBITDA/Net Margins, Operating leverage, EPS dilution.
- **Balance Sheet**: Working capital dynamics, Net Debt, Capital Structure, Asset turnover, Tangible book value.
- **Cash Flow Statement**: Operating Cash Flow (CFO), Free Cash Flow to Firm (FCFF), Free Cash Flow to Equity (FCFE), Capital expenditures (CapEx) quality.

### Key Financial Ratios & Benchmarks
- **Profitability**: Return on Equity (ROE = Net Profit / Equity), Return on Capital Employed (ROCE = EBIT / Capital Employed), ROIC.
- **Valuation Multiples**: Price-to-Earnings (P/E), Price-to-Book (P/B), EV/EBITDA, EV/Sales, PEG Ratio.
- **Solvency & Liquidity**: Current Ratio, Quick Ratio, Debt-to-Equity (D/E), Interest Coverage Ratio (EBIT / Interest Expense).
- **Efficiency**: Days Sales Outstanding (DSO), Inventory Turnover, Cash Conversion Cycle (CCC).

---

## 2. Valuation Methodologies

### Discounted Cash Flow (DCF) Model
1. **Forecast Horizon**: Project 5-10 years of Unlevered Free Cash Flows (UFCF).
2. **WACC Calculation**: 
   $$WACC = \left(\frac{E}{V} \times Re\right) + \left(\frac{D}{V} \times Rd \times (1 - T)\right)$$
   Where $Re = Rf + \beta \times ERP$.
3. **Terminal Value (TV)**:
   - Gordon Growth: $TV = \frac{UFCF_{n} \times (1 + g)}{WACC - g}$
   - Exit Multiple: $TV = EBITDA_n \times Multiple$
4. **Enterprise Value to Equity Value Bridge**:
   $$\text{Implied Equity Value} = \text{PV of FCF} + \text{PV of TV} + \text{Cash} - \text{Total Debt} - \text{Minority Interest}$$

---

## 3. Technical Market Analysis & Indicators

- **Trend Following**: Simple & Exponential Moving Averages (20, 50, 200 EMA), Golden Cross / Death Cross.
- **Momentum & Oscillators**: Relative Strength Index (RSI - 14 period, 30/70 thresholds), MACD (12, 26, 9) signal line crossovers.
- **Volatility**: Bollinger Bands (20-day SMA, +/- 2 standard deviations), Average True Range (ATR).
- **Volume & Support/Resistance**: Volume Weighted Average Price (VWAP), On-Balance Volume (OBV), Pivot Points.

---

## 4. IPO & Capital Markets Analysis (Bluestock Domain)

- **Prospectus (DRHP / RHP) Deconstruction**: Promoter background, object of the offer, fresh issue vs. offer for sale (OFS).
- **Valuation Comparison**: Pre-money vs. post-money valuation, comparative P/E against listed industry peers.
- **Subscription Dynamics**: QIB, NII/HNI, and Retail subscription tracking.
- **Grey Market Premium (GMP)**: Estimated listing gains vs. fundamental valuation safety margin.

---

## 5. Quantitative Risk & Portfolio Metrics

- **Sharpe Ratio**: $\frac{R_p - R_f}{\sigma_p}$
- **Sortino Ratio**: Excess return over downside deviation.
- **Maximum Drawdown (MDD)**: Peak-to-trough decline over a defined investment window.
- **Beta ($\beta$)**: Measure of systematic risk relative to the benchmark index (e.g., NIFTY 50 / S&P 500).
