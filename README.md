# Japan Stock Anomaly Analyzer

**AHA Moment:** Instantly backtest common market anomalies (like "Day of Week" or "Month End" effects) across any Japanese stock using live API data, all within a retro-styled web interface!

## What is this?
The Japan Stock Anomaly Analyzer is a web application built with [Reflex](https://reflex.dev/) that allows users to quickly fetch daily quote data for Japanese stocks (via the J-Quants API) and backtest predefined market anomalies. It visualizes the equity curve and provides detailed statistical metrics of the strategy's performance.

## Prerequisites
- Python 3.10+
- A J-Quants API account (Free plan is supported)

## Setup Instructions

1. **Clone the repository** (if you haven't already).

2. **Navigate to the application directory:**
   ```bash
   cd anomaly_analyzer
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: It is recommended to use a virtual environment)*

4. **Configure API Credentials:**
   Create a `.env` file in the `anomaly_analyzer` directory and add your J-Quants API credentials:
   ```env
   MAIL_ADDRESS=your_jquants_email@example.com
   PASSWORD=your_jquants_password
   ```

5. **Run the App:**
   Start the Reflex application:
   ```bash
   reflex run
   ```
   The app will typically start on `http://localhost:3000`.

## How to Use

1. **Enter Target Tickers:** In the sidebar, input one or more comma-separated Japanese stock codes (e.g., `6599, 7713`).
2. **Select Anomaly Type:** Choose an anomaly to test from the dropdown (e.g., `day_of_week` or `month_end`).
3. **Set Slippage:** Adjust the slippage percentage using the slider to simulate real-world trading costs.
4. **Fetch Data:** Click the **Fetch Data** button. The app will download the required daily quotes from the J-Quants API and save them locally. Wait for the processing to finish.
5. **Start Analysis:** Once data is available, click **START ANALYSIS**. The app will run a backtest and display the resulting Equity Curve and Statistical Metrics (Win Rate, Profit Factor, Total Return, etc.).
