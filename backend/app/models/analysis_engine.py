from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from pathlib import Path
from .correlation_model import CorrelationAnalyzer, HestonParams, ThresholdParams
from ..services.data_service import DataService

class AnalysisEngine:
    """
    Engine to coordinate data flow and analysis between data sources and correlation model.
    """
    def __init__(
        self,
        data_service: Optional[DataService] = None,
        correlation_analyzer: Optional[CorrelationAnalyzer] = None
    ):
        self.data_service = data_service or DataService()
        self.correlation_analyzer = correlation_analyzer or CorrelationAnalyzer()
        
    def prepare_asset_data(
        self,
        dataset_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Prepare asset data for analysis by loading and preprocessing.
        
        Returns:
            Tuple of (returns, volatilities)
        """
        # Load data
        df = self.data_service.read_dataset(dataset_name)
        
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
        # Filter date range if specified
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
            
        # Calculate returns
        returns = df['close'].pct_change().dropna()
        
        # Estimate volatilities
        volatilities = self.correlation_analyzer.estimate_garch_volatility(returns)
        
        return returns, volatilities
    
    def analyze_heat_wave(
        self,
        dataset_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze heat wave effect for a single asset"""
        # Get data
        returns, volatilities = self.prepare_asset_data(
            dataset_name,
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        # Update analyzer parameters if provided
        if params and 'lambda_param' in params:
            self.correlation_analyzer.threshold_params.lambda_param = params['lambda_param']
            
        # Perform analysis
        results = self.correlation_analyzer.detect_heat_wave(returns, volatilities)
        
        # Add metadata
        results.update({
            'dataset': dataset_name,
            'start_date': returns.index[0].strftime('%Y-%m-%d'),
            'end_date': returns.index[-1].strftime('%Y-%m-%d'),
            'data_points': len(returns),
            'parameters': {
                'lambda': self.correlation_analyzer.threshold_params.lambda_param,
                'min_effect_size': self.correlation_analyzer.threshold_params.min_effect_size
            }
        })
        
        return results
    
    def analyze_meteor_shower(
        self,
        dataset1_name: str,
        dataset2_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze meteor shower effect between two assets"""
        # Get data for both assets
        returns1, volatilities1 = self.prepare_asset_data(
            dataset1_name,
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        returns2, volatilities2 = self.prepare_asset_data(
            dataset2_name,
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        # Align the time series
        returns1, returns2 = returns1.align(returns2, join='inner')
        volatilities1, volatilities2 = volatilities1.align(volatilities2, join='inner')
        
        # Update analyzer parameters if provided
        if params and 'lambda_param' in params:
            self.correlation_analyzer.threshold_params.lambda_param = params['lambda_param']
        
        # Perform analysis
        results = self.correlation_analyzer.detect_meteor_shower(
            returns1, returns2, volatilities1, volatilities2
        )
        
        # Add metadata
        results.update({
            'datasets': {
                'asset1': dataset1_name,
                'asset2': dataset2_name
            },
            'start_date': returns1.index[0].strftime('%Y-%m-%d'),
            'end_date': returns1.index[-1].strftime('%Y-%m-%d'),
            'data_points': len(returns1),
            'parameters': {
                'lambda': self.correlation_analyzer.threshold_params.lambda_param,
                'min_effect_size': self.correlation_analyzer.threshold_params.min_effect_size
            }
        })
        
        return results
    
    def batch_analyze(
        self,
        dataset_names: List[str],
        analysis_type: str = 'both',
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform batch analysis on multiple assets.
        
        Args:
            dataset_names: List of dataset names to analyze
            analysis_type: 'heat_wave', 'meteor_shower', or 'both'
            params: Optional parameters for analysis
        """
        results = {
            'heat_wave': {},
            'meteor_shower': {},
            'summary': {
                'total_assets': len(dataset_names),
                'time_period': {
                    'start': None,
                    'end': None
                }
            }
        }
        
        # Heat wave analysis
        if analysis_type in ['heat_wave', 'both']:
            for dataset in dataset_names:
                results['heat_wave'][dataset] = self.analyze_heat_wave(
                    dataset, params
                )
                
        # Meteor shower analysis
        if analysis_type in ['meteor_shower', 'both']:
            for i, dataset1 in enumerate(dataset_names):
                for dataset2 in dataset_names[i+1:]:
                    pair_key = f"{dataset1}_vs_{dataset2}"
                    results['meteor_shower'][pair_key] = self.analyze_meteor_shower(
                        dataset1, dataset2, params
                    )
        
        # Update summary
        all_dates = []
        for analysis in results['heat_wave'].values():
            all_dates.extend([
                pd.to_datetime(analysis['start_date']),
                pd.to_datetime(analysis['end_date'])
            ])
        
        if all_dates:
            results['summary']['time_period'] = {
                'start': min(all_dates).strftime('%Y-%m-%d'),
                'end': max(all_dates).strftime('%Y-%m-%d')
            }
            
        return results
