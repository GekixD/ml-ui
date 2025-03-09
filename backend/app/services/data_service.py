import pandas as pd
from pathlib import Path
from typing import List, Dict

class DataService:
    def __init__(self, data_directory: str = "data"):
        self.data_directory = Path(data_directory)
        self.available_datasets = self._scan_data_directory()
    
    def _scan_data_directory(self) -> Dict[str, Path]:
        return {
            f.stem: f for f in self.data_directory.glob("*.csv")
        }
    
    def get_available_datasets(self) -> List[str]:
        return list(self.available_datasets.keys())
    
    def read_dataset(self, dataset_name: str) -> pd.DataFrame:
        if dataset_name not in self.available_datasets:
            raise ValueError(f"Dataset {dataset_name} not found")
        return pd.read_csv(self.available_datasets[dataset_name])
    
    def get_columns(self, dataset_name: str) -> List[str]:
        df = self.read_dataset(dataset_name)
        return df.columns.tolist() 