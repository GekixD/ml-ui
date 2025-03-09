import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Literal
from config import dataset_config

def create_data_directory():
    data_dir = Path(dataset_config.DATA_DIR)
    data_dir.mkdir(exist_ok=True)
    return data_dir

def get_klines_data(
    symbol: str, 
    interval: str = dataset_config.INTERVAL, 
    limit: int = dataset_config.LIMIT,
    market_type: Literal['spot', 'usdtm', 'coinm'] = 'spot'
) -> Optional[pd.DataFrame]:
    """
    Fetch klines (candlestick) data from Binance.
    
    Args:
        symbol: Trading pair symbol
        interval: Kline interval
        limit: Number of records to fetch
        market_type: 'spot', 'usdtm' (USDT-M futures), or 'coinm' (COIN-M futures)
    """
    
    base_url = dataset_config.ENDPOINTS[market_type]
    
    try:
        response = requests.get(
            base_url,
            params={'symbol': symbol, 'interval': interval, 'limit': limit},
            timeout=dataset_config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data, columns=dataset_config.FEATURES)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Convert price and volume columns to float
        for col in dataset_config.NUMERIC_COLUMNS:
            df[col] = df[col].astype(float)
            
        return df
        
    except requests.exceptions.RequestException as e:
        print(dataset_config.ERROR_MESSAGES['fetch_error'].format(market_type=market_type, symbol=symbol, error=str(e)))
        return None

def fetch_and_save_data(symbols: list, market_type: str, data_dir: Path):
    """Fetch and save data for a list of symbols."""
    for symbol in symbols:
        print(f"Fetching {market_type} data for {symbol}...")
        
        retries = 0
        while retries < dataset_config.MAX_RETRIES:
            df = get_klines_data(symbol, market_type=market_type)
            
            if df is not None:
                # Save to data directory
                file_path = data_dir / dataset_config.FILE_FORMAT.format(symbol=symbol, market_type=market_type)
                df.to_csv(file_path, index=False)
                print(dataset_config.ERROR_MESSAGES['success_message'].format(symbol=symbol, market_type=market_type, file_path=file_path))
                break
                
            retries += 1
            if retries < dataset_config.MAX_RETRIES:
                print(dataset_config.ERROR_MESSAGES['retry_message'].format(symbol=symbol, attempt=retries+1, max_retries=dataset_config.MAX_RETRIES))
                time.sleep(dataset_config.RETRY_DELAY)  # Wait before retry
        
        # Rate limiting
        time.sleep(dataset_config.RATE_LIMIT_DELAY)  # Respect Binance's rate limits

def main():
    data_dir = create_data_directory()
    
    # Fetch spot data
    print("\nFetching spot market data...")
    fetch_and_save_data(dataset_config.SPOT_SYMBOLS, 'spot', data_dir)
    
    # Fetch USDT-M futures data
    print("\nFetching USDT-M futures data...")
    fetch_and_save_data(dataset_config.USDT_FUTURES_SYMBOLS, 'usdtm', data_dir)
    
    # Fetch COIN-M futures data
    print("\nFetching COIN-M futures data...")
    fetch_and_save_data(dataset_config.COIN_FUTURES_SYMBOLS, 'coinm', data_dir)
    
    print("\nAll data collection completed!")

if __name__ == "__main__":
    main()