# Crypto Analytics Platform

A full-stack **cryptocurrency analytics platform** that aggregates market data from multiple sources, performs advanced technical and on-chain analysis, and applies **LSTM-based time series forecasting** to predict future price movements.

## Project Overview
This project is designed as an end-to-end crypto analytics system that:
- collects real-time and historical cryptocurrency data
- analyzes market behavior using technical indicators
- performs on-chain wallet activity analysis
- applies deep learning (LSTM) models for price prediction

The goal of the project is to demonstrate practical usage of **data aggregation, analysis, and machine learning** in a real-world financial domain.

## Data Sources
- **CoinGecko API** – market data (prices, volume, market cap, historical OHLC)
- **Binance API** – real-time trading data and candlestick information
- **On-chain data** – wallet activity, transaction volume, and movement patterns

##  Features
###  Market Data Analysis
- Price tracking for multiple cryptocurrencies
- Volume and market capitalization analysis
- Historical OHLC data processing

###  Technical Indicators
- SMA, EMA
- RSI
- MACD

###  On-Chain Analytics
- Wallet inflow and outflow analysis
- Transaction frequency monitoring
- Detection of abnormal wallet movements
- Basic whale activity insights

###  LSTM Price Prediction
- Time-series preprocessing
- LSTM neural network for price forecasting
- Train / validation split and evaluation
- Overfitting detection based on accuracy and loss comparison

##  Technologies Used
- **Python**
- **FastAPI**
- **TensorFlow / Keras**
- **Pandas & NumPy**
- **Scikit-learn**
- **Docker & Docker Compose**
- **REST APIs**

##  System Architecture
- Data collection services (CoinGecko, Binance)
- Analysis microservices (technical & on-chain)
- ML service for LSTM forecasting
- Web/API layer for visualization and access
  
The diagram below illustrates the overall architecture of the Crypto Analytics Platform, including data collection services, analysis pipelines, machine learning components, and API layers.

![System Architecture Diagram](dija.png)


Each component is containerized and orchestrated using **Docker Compose**.

##  Getting Started

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Internet connection (API access)

### Run with Docker
```bash
docker-compose up --build
