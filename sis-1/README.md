# KazRE Invest: AI Listing Enricher

This application is an AI-powered Property Tech tool designed for KazRE Invest's real estate agents. It converts basic, bullet-point property details into engaging, multi-lingual, SEO-optimized real estate listings in seconds.

## Problem Solved (S2P & R2F)
Agents currently spend ~15 minutes per listing writing descriptions manually and rely on poor-quality automated translation. This application reduces that time to single-digit seconds, drastically improving SEO quality and ensuring 3 fully translated variants (English, Russian, Kazakh) are instantly available to copy-paste.

## Prerequisites
- Python 3.9+
- A Google Gemini API Key

## Setup & Running (R2D)
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Create a `.env` file and add your Gemini API Key so you don't have to enter it in the UI every time:
   ```
   GEMINI_API_KEY="your_api_key_here"
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
4. Access the web interface at `http://localhost:8501`.

## Features
- **Multi-lingual Generation:** High-quality localization for English, Russian, and Kazakh markets.
- **FinOps Tracker (D2C):** A sidebar module that monitors how many listings have been generated in the current session, displaying the estimated API cost and total dollars saved compared to legacy processes.
- **Rich Output:** Copy-to-clipboard friendly markdown elements.
