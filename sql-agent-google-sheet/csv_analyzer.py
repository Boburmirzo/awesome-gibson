try:
    import pandas as pd
    import chardet
except ImportError as e:
    raise ImportError(
        f"Required packages not installed: {e}. Please run: pip install pandas chardet"
    )

from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CSVAnalyzer:
    """Analyzes CSV files and extracts structure information"""

    def __init__(self, max_size_mb: int = 50, supported_encodings: List[str] = None):
        self.max_size_mb = max_size_mb
        self.supported_encodings = supported_encodings or ["utf-8", "latin-1", "cp1252"]

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a CSV file and return structure information"""
        try:
            # Check file size
            file_size = Path(file_path).stat().st_size / (1024 * 1024)  # MB
            if file_size > self.max_size_mb:
                raise ValueError(
                    f"File size ({file_size:.2f}MB) exceeds maximum allowed size ({self.max_size_mb}MB)"
                )

            # Detect encoding
            encoding = self._detect_encoding(file_path)

            # Read and analyze CSV
            df = pd.read_csv(
                file_path, encoding=encoding, nrows=1000
            )  # Sample first 1000 rows

            analysis = {
                "file_info": {
                    "path": file_path,
                    "filename": Path(file_path).name,
                    "file_stem": Path(file_path).stem,
                    "size_mb": file_size,
                    "encoding": encoding,
                    "estimated_rows": self._estimate_total_rows(file_path, encoding),
                },
                "structure": {
                    "columns": list(df.columns),
                    "column_count": len(df.columns),
                    "sample_row_count": len(df),
                    "data_types": self._analyze_data_types(df),
                    "nullable_columns": self._find_nullable_columns(df),
                    "unique_constraints": self._find_unique_constraints(df),
                    "sample_data": df.head(5).to_dict("records"),
                },
                "recommendations": self._generate_recommendations(df),
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing CSV file: {str(e)}")
            raise

    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        with open(file_path, "rb") as f:
            raw_data = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            detected_encoding = result["encoding"]

            # Prefer supported encodings
            if detected_encoding in self.supported_encodings:
                return detected_encoding

            # Try supported encodings
            for encoding in self.supported_encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as test_file:
                        test_file.read(1000)
                        return encoding
                except UnicodeDecodeError:
                    continue

            # Fallback to detected encoding
            return detected_encoding or "utf-8"

    def _estimate_total_rows(self, file_path: str, encoding: str) -> int:
        """Estimate total number of rows in the file"""
        try:
            with open(file_path, "r", encoding=encoding) as f:
                # Count lines more efficiently
                line_count = sum(1 for _ in f) - 1  # Subtract header
                return line_count
        except Exception:
            return -1  # Unknown

    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze data types for each column"""
        type_analysis = {}

        for column in df.columns:
            series = df[column].dropna()  # Remove null values for analysis

            analysis = {
                "pandas_dtype": str(df[column].dtype),
                "null_count": df[column].isnull().sum(),
                "null_percentage": (df[column].isnull().sum() / len(df)) * 100,
                "unique_count": df[column].nunique(),
                "recommended_sql_type": self._recommend_sql_type(series),
                "sample_values": series.head(3).tolist() if len(series) > 0 else [],
            }

            # Additional analysis based on type
            if pd.api.types.is_numeric_dtype(series):
                analysis.update(
                    {
                        "min_value": series.min(),
                        "max_value": series.max(),
                        "has_decimals": any(series % 1 != 0),
                    }
                )
            elif pd.api.types.is_string_dtype(series):
                analysis.update(
                    {
                        "max_length": series.str.len().max() if len(series) > 0 else 0,
                        "avg_length": series.str.len().mean() if len(series) > 0 else 0,
                    }
                )

            type_analysis[column] = analysis

        return type_analysis

    def _recommend_sql_type(self, series: pd.Series) -> str:
        """Recommend SQL data type based on pandas series"""
        if len(series) == 0:
            return "TEXT"

        if pd.api.types.is_integer_dtype(series):
            max_val = series.max()
            min_val = series.min()

            if min_val >= 0:
                if max_val <= 255:
                    return "TINYINT UNSIGNED"
                elif max_val <= 65535:
                    return "SMALLINT UNSIGNED"
                elif max_val <= 4294967295:
                    return "INT UNSIGNED"
                else:
                    return "BIGINT UNSIGNED"
            else:
                if min_val >= -128 and max_val <= 127:
                    return "TINYINT"
                elif min_val >= -32768 and max_val <= 32767:
                    return "SMALLINT"
                elif min_val >= -2147483648 and max_val <= 2147483647:
                    return "INT"
                else:
                    return "BIGINT"

        elif pd.api.types.is_float_dtype(series):
            return "DECIMAL(10,2)"

        elif pd.api.types.is_bool_dtype(series):
            return "BOOLEAN"

        elif pd.api.types.is_datetime64_any_dtype(series):
            return "DATETIME"

        else:  # String types
            max_length = series.astype(str).str.len().max()
            if max_length <= 255:
                return f"VARCHAR({max_length})"
            elif max_length <= 65535:
                return "TEXT"
            else:
                return "LONGTEXT"

    def _find_nullable_columns(self, df: pd.DataFrame) -> List[str]:
        """Find columns that can be nullable"""
        nullable_cols = []
        for column in df.columns:
            if df[column].isnull().any():
                nullable_cols.append(column)
        return nullable_cols

    def _find_unique_constraints(self, df: pd.DataFrame) -> List[str]:
        """Find columns that could be unique constraints"""
        unique_cols = []
        for column in df.columns:
            if df[column].nunique() == len(df.dropna(subset=[column])):
                unique_cols.append(column)
        return unique_cols

    def _generate_recommendations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate recommendations for database design"""
        recommendations = {
            "primary_key_candidates": [],
            "index_candidates": [],
            "normalization_opportunities": [],
            "data_quality_issues": [],
        }

        # Find primary key candidates
        for column in df.columns:
            if df[column].nunique() == len(df) and not df[column].isnull().any():
                recommendations["primary_key_candidates"].append(column)

        # Find index candidates (high cardinality, frequently queried)
        for column in df.columns:
            unique_ratio = df[column].nunique() / len(df)
            if 0.1 < unique_ratio < 0.9:  # Good selectivity
                recommendations["index_candidates"].append(column)

        # Data quality issues
        for column in df.columns:
            null_percentage = (df[column].isnull().sum() / len(df)) * 100
            if null_percentage > 50:
                recommendations["data_quality_issues"].append(
                    f"Column '{column}' has {null_percentage:.1f}% null values"
                )

        return recommendations


class DataValidator:
    """Validates data before import"""

    @staticmethod
    def validate_data_consistency(
        df: pd.DataFrame, analysis: Dict[str, Any]
    ) -> List[str]:
        """Validate data consistency against analysis"""
        issues = []

        # Check for data type consistency
        for column, type_info in analysis["structure"]["data_types"].items():
            if column in df.columns:
                # Check for unexpected nulls in non-nullable columns
                if column not in analysis["structure"]["nullable_columns"]:
                    null_count = df[column].isnull().sum()
                    if null_count > 0:
                        issues.append(
                            f"Column '{column}' has {null_count} unexpected null values"
                        )

        return issues

    @staticmethod
    def prepare_data_for_import(
        df: pd.DataFrame, analysis: Dict[str, Any]
    ) -> pd.DataFrame:
        """Prepare DataFrame for database import"""
        prepared_df = df.copy()

        # Handle data type conversions based on analysis
        for column, type_info in analysis["structure"]["data_types"].items():
            if column in prepared_df.columns:
                sql_type = type_info["recommended_sql_type"]

                # Convert to appropriate pandas dtype
                if "INT" in sql_type.upper() or "BIGINT" in sql_type.upper():
                    prepared_df[column] = pd.to_numeric(
                        prepared_df[column], errors="coerce"
                    )
                    if "UNSIGNED" not in sql_type.upper():
                        prepared_df[column] = prepared_df[column].astype("Int64")
                elif "DECIMAL" in sql_type.upper() or "FLOAT" in sql_type.upper():
                    prepared_df[column] = pd.to_numeric(
                        prepared_df[column], errors="coerce"
                    )
                elif "BOOLEAN" in sql_type.upper():
                    prepared_df[column] = prepared_df[column].astype("boolean")
                elif "DATETIME" in sql_type.upper():
                    prepared_df[column] = pd.to_datetime(
                        prepared_df[column], errors="coerce"
                    )

        return prepared_df
