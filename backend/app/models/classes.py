import pandas as pd
import os
from abc import ABC, abstractmethod
from typing import Dict, Any
from config.config_manager import ConfigManager

config = ConfigManager()
asset_config = config.get_asset_config()

class BaseCryptoData(ABC):
    """
    Base class for all crypto asset data.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        df = pd.read_csv(self.file_path, parse_dates=['timestamp'], index_col='timestamp')
        return self._preprocess_data(df)
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_index()
        df = df.drop_duplicates()
        df = df.dropna()
        return df
    
    @abstractmethod
    def get_summary(self) -> Dict[str, Any]:
        pass

class CryptoAsset(BaseCryptoData):
    """
    Represents a crypto asset with its data and computed metrics.
    """
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.symbol = os.path.basename(file_path).split('.')[0]
        self.config = asset_config  # Store config reference

    def get_summary(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'start_date': self.data.index.min(),
            'end_date': self.data.index.max(),
            'total_rows': len(self.data),
            'price_range': {
                'min': float(self.data['low'].min()),
                'max': float(self.data['high'].max())
            },
            'volume_range': {
                'min': float(self.data['volume'].min()),
                'max': float(self.data['volume'].max())
            }
        }
    
    def compute_returns(self) -> pd.Series:
        return self.data['close'].pct_change().dropna()
    
    def compute_volatility(self) -> pd.Series:
        return self.data['close'].pct_change().dropna().std()
    
    def compute_rsi(self) -> pd.Series:
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        return 100 - 100 / (1 + rs)
    
    def compute_macd(self) -> pd.DataFrame:
        short_ema = self.data['close'].ewm(
            span=self.config['SHORT_WINDOW'], 
            adjust=False
        ).mean()
        long_ema = self.data['close'].ewm(
            span=self.config['LONG_WINDOW'], 
            adjust=False
        ).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(
            span=self.config['SIGNAL_WINDOW'], 
            adjust=False
        ).mean()
        return pd.DataFrame({
            'macd_line': macd_line,
            'signal_line': signal_line
        })
    
    def compute_bollinger_bands(self) -> pd.DataFrame:
        window = self.config['BOLLINGER_WINDOW']
        moving_avg = self.data['close'].rolling(window=window).mean()
        std_dev = self.data['close'].rolling(window=window).std()
        upper_band = moving_avg + (std_dev * self.config['STD_DEV'])
        lower_band = moving_avg - (std_dev * self.config['STD_DEV'])
        return pd.DataFrame({
            'upper_band': upper_band,
            'middle_band': moving_avg,
            'lower_band': lower_band
        })
    
    def compute_stochastic_oscillator(self) -> pd.DataFrame:
        window = self.config['STOCH_WINDOW']
        smooth = self.config['SMOOTH_WINDOW']
        low_14 = self.data['low'].rolling(window=window).min()
        high_14 = self.data['high'].rolling(window=window).max()
        stoch_k = 100 * ((self.data['close'] - low_14) / (high_14 - low_14))
        stoch_d = stoch_k.rolling(window=smooth).mean()
        return pd.DataFrame({
            'stoch_k': stoch_k,
            'stoch_d': stoch_d
        })
    
    def compute_adx(self) -> pd.DataFrame:
        window = self.config['ADX_WINDOW']
        delta_high = self.data['high'].diff()
        delta_low = self.data['low'].diff()
        diff_high = delta_high.where(delta_high > 0, 0)
        diff_low = -delta_low.where(delta_low < 0, 0)
        tr = pd.concat([delta_high, delta_low, diff_high, diff_low], axis=1).abs().max(axis=1)
        up = (self.data['high'] - self.data['high'].shift(1)).where(delta_high > 0, 0)
        down = (-self.data['low'] + self.data['low'].shift(1)).where(delta_low < 0, 0)
        up_move = up.rolling(window=window).mean()
        down_move = down.rolling(window=window).mean()
        di_plus = 100 * up_move / tr
        di_minus = 100 * down_move / tr
        dx = (di_plus - di_minus).abs() / (di_plus + di_minus)
        adx = dx.rolling(window=window).mean()
        return pd.DataFrame({
            'adx': adx,
            'di_plus': di_plus,
            'di_minus': di_minus
        })
    
    def compute_obv(self) -> pd.Series:
        delta = self.data['close'].diff()
        volume = self.data['volume']
        obv = (delta.where(delta > 0, 0) * volume).fillna(0).cumsum()
        return obv
    
    def compute_cci(self) -> pd.Series:
        window = self.config['CCI_WINDOW']
        typical_price = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        moving_average = typical_price.rolling(window=window).mean()
        mean_deviation = (typical_price - moving_average).abs().rolling(window=window).mean()
        cci = (typical_price - moving_average) / (0.015 * mean_deviation)
        return cci
    
