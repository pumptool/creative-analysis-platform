"""
CSV parsing utilities for quantitative and qualitative data
"""
import pandas as pd
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class CSVParser:
    """Parser for experiment CSV files"""
    
    @staticmethod
    def parse_quantitative_results(file_path: str) -> pd.DataFrame:
        """
        Parse quantitative results CSV
        
        Expected columns:
        - metric
        - segment
        - breakdown
        - filter
        - delta
        - marginOfError
        - ci_95_interval
        - baselineMean
        - testGroupMean
        - baselineSampleSize
        - testGroupSampleSize
        - totalWeight
        - treatment
        
        Args:
            file_path: Path to results CSV
            
        Returns:
            Parsed DataFrame
        """
        try:
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_cols = ['metric', 'segment', 'delta', 'treatment']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Convert numeric columns
            numeric_cols = [
                'delta', 'marginOfError', 'baselineMean', 'testGroupMean',
                'baselineSampleSize', 'testGroupSampleSize', 'totalWeight'
            ]
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Parse confidence intervals if present
            if 'ci_95_interval' in df.columns:
                df['ci_95_lower'] = df['ci_95_interval'].apply(
                    lambda x: CSVParser._parse_interval(x)[0] if pd.notna(x) else None
                )
                df['ci_95_upper'] = df['ci_95_interval'].apply(
                    lambda x: CSVParser._parse_interval(x)[1] if pd.notna(x) else None
                )
            
            logger.info(f"Parsed quantitative results: {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Failed to parse quantitative results: {e}")
            raise
    
    @staticmethod
    def parse_qualitative_comments(file_path: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        Parse qualitative comments CSV
        
        Structure:
        - Metadata columns: response_id, treatment_group, weight
        - Segment flag columns: Binary indicators (TRUE/FALSE, 1/0)
        - Response columns: Open-ended text responses
        
        Args:
            file_path: Path to comments CSV
            
        Returns:
            Tuple of (DataFrame, list of response column names)
        """
        try:
            df = pd.read_csv(file_path)
            
            # Identify column types
            metadata_cols = ['response_id', 'treatment_group', 'weight']
            
            # Detect segment columns (binary indicators)
            segment_cols = []
            response_cols = []
            
            for col in df.columns:
                if col in metadata_cols:
                    continue
                
                # Check if column is binary (segment flag)
                unique_vals = df[col].dropna().unique()
                is_binary = all(
                    val in [True, False, 'TRUE', 'FALSE', 1, 0, '1', '0', '']
                    for val in unique_vals
                )
                
                if is_binary:
                    segment_cols.append(col)
                    # Standardize to boolean
                    df[col] = df[col].apply(CSVParser._to_bool)
                else:
                    # Assume it's a response column
                    response_cols.append(col)
            
            logger.info(
                f"Parsed qualitative comments: {len(df)} responses, "
                f"{len(segment_cols)} segments, {len(response_cols)} questions"
            )
            
            return df, response_cols
            
        except Exception as e:
            logger.error(f"Failed to parse qualitative comments: {e}")
            raise
    
    @staticmethod
    def _parse_interval(interval_str: str) -> Tuple[float, float]:
        """
        Parse confidence interval string like "[0.05, 0.15]"
        
        Args:
            interval_str: Interval string
            
        Returns:
            Tuple of (lower, upper)
        """
        try:
            # Remove brackets and split
            cleaned = interval_str.strip('[]()').replace(' ', '')
            lower, upper = cleaned.split(',')
            return float(lower), float(upper)
        except:
            return None, None
    
    @staticmethod
    def _to_bool(value) -> bool:
        """
        Convert various boolean representations to bool
        
        Args:
            value: Value to convert
            
        Returns:
            Boolean value
        """
        if pd.isna(value) or value == '' or value == 0 or value == '0':
            return False
        if value in [True, 'TRUE', 'True', 1, '1']:
            return True
        return False
    
    @staticmethod
    def get_segment_metrics(
        df: pd.DataFrame,
        metric_name: str,
        segment_name: str = None
    ) -> Dict[str, Any]:
        """
        Extract metrics for a specific segment
        
        Args:
            df: Quantitative results DataFrame
            metric_name: Name of metric (e.g., 'brand_favorability')
            segment_name: Optional segment filter
            
        Returns:
            Dictionary of metric data
        """
        try:
            # Filter by metric
            filtered = df[df['metric'] == metric_name]
            
            # Filter by segment if provided
            if segment_name:
                filtered = filtered[filtered['segment'] == segment_name]
            
            if filtered.empty:
                return {}
            
            # Aggregate results
            results = {}
            for _, row in filtered.iterrows():
                seg = row['segment']
                results[seg] = {
                    'delta': row.get('delta'),
                    'margin_of_error': row.get('marginOfError'),
                    'ci_95': [row.get('ci_95_lower'), row.get('ci_95_upper')],
                    'baseline_mean': row.get('baselineMean'),
                    'test_group_mean': row.get('testGroupMean'),
                    'sample_size': row.get('testGroupSampleSize'),
                    'weight': row.get('totalWeight')
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get segment metrics: {e}")
            return {}
    
    @staticmethod
    def get_comments_by_segment(
        df: pd.DataFrame,
        response_col: str,
        segment_col: str
    ) -> List[str]:
        """
        Get comments for a specific segment
        
        Args:
            df: Qualitative comments DataFrame
            response_col: Name of response column
            segment_col: Name of segment column
            
        Returns:
            List of comments
        """
        try:
            # Filter by segment (where segment column is True)
            filtered = df[df[segment_col] == True]
            
            # Get non-empty responses
            comments = filtered[response_col].dropna().tolist()
            comments = [c for c in comments if str(c).strip()]
            
            logger.info(f"Found {len(comments)} comments for segment {segment_col}")
            return comments
            
        except Exception as e:
            logger.error(f"Failed to get comments by segment: {e}")
            return []
