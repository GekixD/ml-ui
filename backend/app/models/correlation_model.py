from typing import List, Dict, Tuple, Optional, Any, Any
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from dataclasses import dataclass
import statsmodels.api as sm
from arch import arch_model

@dataclass
class HestonParams:
    """Parameters for the Heston stochastic volatility model"""
    kappa: float  # Mean reversion rate
    theta: float  # Long-term variance level
    eta: float    # Volatility of volatility
    rho: float    # Correlation between asset returns and volatility
    v0: float     # Initial variance

@dataclass
class ThresholdParams:
    """Parameters for threshold calculation"""
    lambda_param: float  # Sensitivity parameter (1-3)
    min_effect_size: float  # Minimum size for effect to be considered

class CorrelationAnalyzer:
    def __init__(
        self,
        heston_params: Optional[HestonParams] = None,
        threshold_params: Optional[ThresholdParams] = None
    ):
        self.heston_params = heston_params or HestonParams(
            kappa=2.0,    # Mean reversion speed
            theta=0.04,   # Long-term variance
            eta=0.3,      # Volatility of volatility
            rho=-0.7,     # Return-volatility correlation
            v0=0.04      # Initial variance
        )
        self.threshold_params = threshold_params or ThresholdParams(
            lambda_param=2.0,  # Default sensitivity
            min_effect_size=0.02  # 2% minimum effect size
        )

    def estimate_garch_volatility(self, returns: pd.Series) -> pd.Series:
        """Estimate volatility using GARCH(1,1)"""
        model = arch_model(returns, vol='Garch', p=1, q=1)
        results = model.fit(disp='off')
        return pd.Series(
            np.sqrt(results.conditional_volatility),
            index=returns.index
        )

    def simulate_heston_volatility(
        self, 
        sigma_t: float, 
        dt: float = 1/252
    ) -> float:
        """
        Simulate one step of Heston volatility process
        dσ = κ(θ - σ²) + η*σ*dW
        """
        dW = np.random.normal(0, np.sqrt(dt))
        dsigma = (
            self.heston_params.kappa * 
            (self.heston_params.theta - sigma_t**2) * dt +
            self.heston_params.eta * sigma_t * dW
        )
        return max(0, sigma_t + dsigma)  # Ensure non-negative volatility

    def calculate_threshold(
        self,
        price_prev: float,
        sigma_t: float
    ) -> float:
        """Calculate threshold for effect trigger"""
        return self.threshold_params.lambda_param * sigma_t * price_prev

    def detect_heat_wave(
        self,
        returns: pd.Series,
        volatilities: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Detect heat wave effect (autocorrelation in returns)
        """
        if volatilities is None:
            volatilities = self.estimate_garch_volatility(returns)

        # Calculate thresholds
        prices = (1 + returns).cumprod()
        thresholds = pd.Series(
            [self.calculate_threshold(p, v) for p, v in zip(prices, volatilities)],
            index=returns.index
        )

        # Detect effects
        price_changes = returns * prices.shift(1)
        triggers = abs(price_changes) > thresholds
        
        # Analyze consecutive day effects
        heat_wave_days = triggers & (returns * returns.shift(1) > 0)
        
        return {
            'effect_days': heat_wave_days.sum(),
            'total_triggers': triggers.sum(),
            'effect_ratio': heat_wave_days.sum() / max(triggers.sum(), 1),
            'mean_threshold': thresholds.mean(),
            'threshold_std': thresholds.std(),
            'volatility_clusters': self._detect_volatility_clusters(volatilities)
        }

    def detect_meteor_shower(
        self,
        returns1: pd.Series,
        returns2: pd.Series,
        volatilities1: Optional[pd.Series] = None,
        volatilities2: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Detect meteor shower effect (cross-asset return spillovers)
        """
        if volatilities1 is None:
            volatilities1 = self.estimate_garch_volatility(returns1)
        if volatilities2 is None:
            volatilities2 = self.estimate_garch_volatility(returns2)

        # Calculate thresholds
        prices1 = (1 + returns1).cumprod()
        prices2 = (1 + returns2).cumprod()
        
        thresholds1 = pd.Series(
            [self.calculate_threshold(p, v) for p, v in zip(prices1, volatilities1)],
            index=returns1.index
        )
        thresholds2 = pd.Series(
            [self.calculate_threshold(p, v) for p, v in zip(prices2, volatilities2)],
            index=returns2.index
        )

        # Detect effects
        price_changes1 = returns1 * prices1.shift(1)
        price_changes2 = returns2 * prices2.shift(1)
        
        triggers1 = abs(price_changes1) > thresholds1
        triggers2 = abs(price_changes2) > thresholds2

        # Analyze cross-asset effects
        meteor_shower_days = (
            triggers1 & triggers2 & 
            (returns1 * returns2 > 0)
        )

        # Calculate lead-lag relationships
        lead_lag = self._calculate_lead_lag(returns1, returns2, 5)

        return {
            'effect_days': meteor_shower_days.sum(),
            'total_triggers': (triggers1 & triggers2).sum(),
            'effect_ratio': meteor_shower_days.sum() / max((triggers1 & triggers2).sum(), 1),
            'mean_threshold1': thresholds1.mean(),
            'mean_threshold2': thresholds2.mean(),
            'lead_lag_relationship': lead_lag,
            'correlation': returns1.corr(returns2)
        }

    def _detect_volatility_clusters(
        self,
        volatilities: pd.Series,
        threshold_std: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect periods of high volatility clustering"""
        vol_mean = volatilities.mean()
        vol_std = volatilities.std()
        high_vol = volatilities > (vol_mean + threshold_std * vol_std)
        
        clusters = []
        in_cluster = False
        cluster_start = None
        
        for date, is_high in high_vol.items():
            if is_high and not in_cluster:
                in_cluster = True
                cluster_start = date
            elif not is_high and in_cluster:
                clusters.append({
                    'start': cluster_start,
                    'end': date,
                    'duration': (date - cluster_start).days,
                    'mean_vol': volatilities[cluster_start:date].mean()
                })
                in_cluster = False
        
        return clusters

    def _calculate_lead_lag(
        self,
        returns1: pd.Series,
        returns2: pd.Series,
        max_lag: int
    ) -> Dict[str, float]:
        """Calculate lead-lag relationships between assets"""
        correlations = {}
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                corr = returns1.corr(returns2.shift(-lag))
            else:
                corr = returns1.shift(lag).corr(returns2)
            correlations[lag] = corr
        
        return correlations

    def optimize_lambda(
        self,
        returns: pd.Series,
        volatilities: pd.Series,
        target_ratio: float = 0.1
    ) -> float:
        """Optimize lambda parameter to achieve target effect ratio"""
        def objective(lambda_param):
            self.threshold_params.lambda_param = lambda_param
            result = self.detect_heat_wave(returns, volatilities)
            return abs(result['effect_ratio'] - target_ratio)

        result = minimize(
            objective,
            x0=2.0,
            bounds=[(1.0, 3.0)],
            method='L-BFGS-B'
        )
        
        return result.x[0]
