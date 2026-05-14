"""
Excel Parser Service
Reads .xlsx / .csv files and returns structured data with column info.
"""
import io
from typing import Any, Dict, List, Tuple

import pandas as pd
import numpy as np


def parse_file(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Parse an uploaded file (xlsx or csv) into a DataFrame.
    Returns (dataframe, list_of_column_names).
    """
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "csv":
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif ext in ("xlsx", "xls"):
        # openpyxl is generally better for .xlsx
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: .{ext}. Please upload .xlsx or .csv")

    # Strip whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]

    # Drop completely empty rows
    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df, list(df.columns)


def dataframe_to_records(df: pd.DataFrame, mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Convert DataFrame to list of dicts using the canonical column mapping.
    Optimized version using vectorized operations.
    """
    # Create a result df with row indices starting at 2
    result_df = pd.DataFrame({"_row": df.index + 2})
    
    # Map columns vectorized
    for canonical, excel_col in mapping.items():
        if excel_col and excel_col in df.columns:
            # Copy the column
            result_df[canonical] = df[excel_col]
        else:
            result_df[canonical] = None

    # Replace all nan forms with None (cleaner for JSON)
    # Using mask/replace is faster than iterrows
    result_df = result_df.replace({np.nan: None})
    
    return result_df.to_dict(orient="records")
