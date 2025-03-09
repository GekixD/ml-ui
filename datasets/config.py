from typing import Dict, List
from pathlib import Path
from dataclasses import dataclass
import yaml

@dataclass
class DatasetConfig:
    """Dataset collection configuration parameters"""
    INTERVAL: str = '1d'
    LIMIT: int = 5 * 365  # 5 years of daily data
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 10
    
    ENDPOINTS: Dict[str, str] = None
    SPOT_SYMBOLS: List[str] = None
    USDT_FUTURES_SYMBOLS: List[str] = None
    COIN_FUTURES_SYMBOLS: List[str] = None
    
    FEATURES: List[str] = None
    NUMERIC_COLUMNS: List[str] = None
    TIMESTAMP_COLUMN: str = 'timestamp'
    
    DATA_DIR: str = 'datasets/data'
    FILE_FORMAT: str = '{symbol}_{market_type}_daily.csv'
    
    RATE_LIMIT_DELAY: int = 1
    RETRY_DELAY: int = 2
    
    def __post_init__(self):
        # Set default values for complex types
        if self.ENDPOINTS is None:
            self.ENDPOINTS = {
                'spot': 'https://api.binance.com/api/v3/klines',
                'usdtm': 'https://fapi.binance.com/fapi/v1/klines',
                'coinm': 'https://dapi.binance.com/dapi/v1/klines'
            }
        
        if self.SPOT_SYMBOLS is None:
            self.SPOT_SYMBOLS = [
                'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT',
                'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT'
            ]
        
        if self.USDT_FUTURES_SYMBOLS is None:
            self.USDT_FUTURES_SYMBOLS = [
                'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'LTCUSDT', 'ADAUSDT'
            ]
        
        if self.COIN_FUTURES_SYMBOLS is None:
            self.COIN_FUTURES_SYMBOLS = ['BTCUSD', 'ETHUSD']
            
        if self.FEATURES is None:
            self.FEATURES = [
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ]
            
        if self.NUMERIC_COLUMNS is None:
            self.NUMERIC_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
    
    def validate(self):
        """Validate configuration settings"""
        if not all(self.ENDPOINTS.values()):
            raise ValueError("Invalid API endpoints configuration")
        
        if not all([self.SPOT_SYMBOLS, self.USDT_FUTURES_SYMBOLS, self.COIN_FUTURES_SYMBOLS]):
            raise ValueError("Trading symbols not properly configured")
        
        if not all(isinstance(x, str) for x in self.FEATURES):
            raise ValueError("Invalid features configuration")
        
        if not all(col in self.FEATURES for col in self.NUMERIC_COLUMNS):
            raise ValueError("Numeric columns must be subset of features")

    def get_error_messages(self) -> Dict[str, str]:
        """Get error message templates"""
        return {
            'fetch_error': "Error fetching {market_type} data for {symbol}: {error}",
            'retry_message': "Retrying {symbol} ({attempt}/{max_retries})...",
            'success_message': "Successfully saved {symbol} {market_type} data to {file_path}"
        }

# Create singleton instance
dataset_config = DatasetConfig()
dataset_config.validate()