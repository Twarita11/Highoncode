import pandas as pd
import os
from functools import lru_cache
from typing import Dict

class DataManager:
    def __init__(self):
        self._cache: Dict[str, pd.DataFrame] = {}
    
    @lru_cache(maxsize=1)
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load CSV data from the specified path with caching."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        df = pd.read_csv(file_path)
        self._cache[file_path] = df
        return df
    
    def get_data(self, file_path: str) -> pd.DataFrame:
        """Get data with fallback to loading if not cached."""
        if file_path in self._cache:
            return self._cache[file_path]
        return self.load_data(file_path)
    
    def save_data(self, df: pd.DataFrame, file_path: str):
        """Save DataFrame to CSV."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)

# Global instance
data_manager = DataManager()

def load_data(file_path):
    """Legacy function for backward compatibility."""
    return data_manager.load_data(file_path)

def save_data(df, file_path):
    """Legacy function for backward compatibility."""
    data_manager.save_data(df, file_path)
