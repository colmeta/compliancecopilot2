# ==============================================================================
# app/data_science/analytics_engine.py
# Analytics Engine - Fortune 50-Grade Data Science
# ==============================================================================
"""
Analytics Engine: Presidential-Grade Data Analysis

This engine performs sophisticated data analysis that would make McKinsey proud.
Every insight, every recommendation, every visualization is built to be
presented to presidents, CEOs, and world leaders.

Capabilities:
- Automated exploratory data analysis
- Statistical significance testing
- Trend analysis and forecasting
- Anomaly detection
- Correlation analysis
- Predictive modeling
- Scenario analysis
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import stats
import json

logger = logging.getLogger(__name__)


@dataclass
class DataInsight:
    """
    A single data insight with supporting evidence.
    
    Attributes:
        insight_type: Type of insight ('trend', 'anomaly', 'correlation', etc.)
        title: Headline of the insight
        description: Detailed explanation
        significance: Statistical significance (0.0-1.0)
        impact: Business impact level ('low', 'medium', 'high', 'critical')
        evidence: Supporting data and calculations
        recommendations: Actionable recommendations
        confidence: Confidence level (0.0-1.0)
    """
    insight_type: str
    title: str
    description: str
    significance: float
    impact: str
    evidence: Dict[str, Any]
    recommendations: List[str]
    confidence: float


class AnalyticsEngine:
    """
    Analytics Engine: Fortune 50-Grade Data Science.
    
    This engine transforms raw data into presidential-grade insights.
    Every analysis is designed to be actionable, statistically sound,
    and presentation-ready.
    """
    
    def __init__(self):
        """Initialize the Analytics Engine."""
        logger.info("AnalyticsEngine initialized - Presidential-Grade Analytics Ready")
    
    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        analysis_goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a DataFrame.
        
        Args:
            df: Pandas DataFrame to analyze
            analysis_goals: Optional list of specific goals
            
        Returns:
            Dict with complete analysis results
        """
        try:
            insights = []
            
            # Basic statistics
            basic_stats = self._compute_basic_statistics(df)
            
            # Trend analysis (for time series data)
            if self._has_time_column(df):
                trend_insights = self._analyze_trends(df)
                insights.extend(trend_insights)
            
            # Correlation analysis
            correlation_insights = self._analyze_correlations(df)
            insights.extend(correlation_insights)
            
            # Anomaly detection
            anomaly_insights = self._detect_anomalies(df)
            insights.extend(anomaly_insights)
            
            # Distribution analysis
            distribution_insights = self._analyze_distributions(df)
            insights.extend(distribution_insights)
            
            # Top insights (sorted by significance × impact)
            top_insights = self._rank_insights(insights)
            
            return {
                'success': True,
                'summary': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                    'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
                    'total_insights': len(insights)
                },
                'basic_statistics': basic_stats,
                'insights': [self._insight_to_dict(i) for i in top_insights],
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analytics error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _compute_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute basic statistics for all columns."""
        stats_dict = {}
        
        # Numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            stats_dict[col] = {
                'type': 'numeric',
                'count': int(df[col].count()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'q25': float(df[col].quantile(0.25)),
                'q75': float(df[col].quantile(0.75)),
                'missing': int(df[col].isna().sum())
            }
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            stats_dict[col] = {
                'type': 'categorical',
                'count': int(df[col].count()),
                'unique': int(df[col].nunique()),
                'top_value': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'top_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'missing': int(df[col].isna().sum())
            }
        
        return stats_dict
    
    def _has_time_column(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame has a datetime column."""
        return len(df.select_dtypes(include=['datetime64'])) > 0
    
    def _analyze_trends(self, df: pd.DataFrame) -> List[DataInsight]:
        """Analyze trends in time series data."""
        insights = []
        
        # Find datetime columns
        time_cols = df.select_dtypes(include=['datetime64']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(time_cols) == 0 or len(numeric_cols) == 0:
            return insights
        
        time_col = time_cols[0]
        
        # Sort by time
        df_sorted = df.sort_values(time_col)
        
        for num_col in numeric_cols[:5]:  # Analyze top 5 numeric columns
            # Calculate trend
            x = np.arange(len(df_sorted))
            y = df_sorted[num_col].fillna(df_sorted[num_col].mean())
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            if p_value < 0.05:  # Statistically significant
                # Determine trend direction
                if slope > 0:
                    trend_direction = "increasing"
                    impact = "high" if slope > y.mean() * 0.1 else "medium"
                else:
                    trend_direction = "decreasing"
                    impact = "high" if abs(slope) > y.mean() * 0.1 else "medium"
                
                # Calculate percentage change
                first_value = y.iloc[0]
                last_value = y.iloc[-1]
                pct_change = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
                
                insight = DataInsight(
                    insight_type='trend',
                    title=f"{num_col} is {trend_direction}",
                    description=f"Statistical analysis shows a {trend_direction} trend in {num_col} with {abs(pct_change):.1f}% change over the period. R² = {r_value**2:.3f}",
                    significance=1 - p_value,
                    impact=impact,
                    evidence={
                        'slope': float(slope),
                        'r_squared': float(r_value**2),
                        'p_value': float(p_value),
                        'percent_change': float(pct_change)
                    },
                    recommendations=[
                        f"Monitor {num_col} closely as it shows significant {trend_direction} pattern",
                        f"Forecast future values based on {r_value**2:.1%} correlation",
                        "Investigate root causes of this trend"
                    ],
                    confidence=float(r_value**2)
                )
                
                insights.append(insight)
        
        return insights
    
    def _analyze_correlations(self, df: pd.DataFrame) -> List[DataInsight]:
        """Analyze correlations between numeric columns."""
        insights = []
        
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return insights
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations (excluding diagonal)
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                
                # Strong correlation threshold
                if abs(corr) > 0.7:
                    # Determine relationship type
                    if corr > 0:
                        relationship = "positively correlated"
                        impact = "high" if corr > 0.9 else "medium"
                    else:
                        relationship = "negatively correlated"
                        impact = "high" if corr < -0.9 else "medium"
                    
                    insight = DataInsight(
                        insight_type='correlation',
                        title=f"{col1} and {col2} are {relationship}",
                        description=f"Strong correlation detected: {col1} and {col2} have a correlation coefficient of {corr:.3f}. This suggests they move together.",
                        significance=abs(corr),
                        impact=impact,
                        evidence={
                            'correlation': float(corr),
                            'column1': col1,
                            'column2': col2
                        },
                        recommendations=[
                            f"Leverage the relationship between {col1} and {col2} for predictions",
                            "Investigate causation vs correlation",
                            "Consider using one as a leading indicator for the other"
                        ],
                        confidence=abs(corr)
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[DataInsight]:
        """Detect anomalies in numeric columns."""
        insights = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:5]:  # Top 5 columns
            # Use IQR method for anomaly detection
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            anomalies = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            if len(anomalies) > 0:
                anomaly_pct = (len(anomalies) / len(df)) * 100
                
                if anomaly_pct > 1:  # More than 1% anomalies
                    impact = "critical" if anomaly_pct > 10 else "high" if anomaly_pct > 5 else "medium"
                    
                    insight = DataInsight(
                        insight_type='anomaly',
                        title=f"Anomalies detected in {col}",
                        description=f"Found {len(anomalies)} anomalous values ({anomaly_pct:.1f}% of data) in {col}. These values fall outside the expected range [{lower_bound:.2f}, {upper_bound:.2f}].",
                        significance=anomaly_pct / 100,
                        impact=impact,
                        evidence={
                            'anomaly_count': int(len(anomalies)),
                            'percentage': float(anomaly_pct),
                            'lower_bound': float(lower_bound),
                            'upper_bound': float(upper_bound),
                            'mean': float(df[col].mean())
                        },
                        recommendations=[
                            f"Investigate the {len(anomalies)} anomalous values in {col}",
                            "Verify data quality and entry accuracy",
                            "Consider data cleaning or transformation",
                            "Flag these records for manual review"
                        ],
                        confidence=0.85
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def _analyze_distributions(self, df: pd.DataFrame) -> List[DataInsight]:
        """Analyze distributions of numeric columns."""
        insights = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:3]:  # Top 3 columns
            # Test for normality
            if len(df[col].dropna()) > 20:  # Need enough samples
                statistic, p_value = stats.normaltest(df[col].dropna())
                
                # Calculate skewness
                skewness = df[col].skew()
                
                if abs(skewness) > 1:  # Highly skewed
                    if skewness > 0:
                        skew_type = "right-skewed"
                        interpretation = "Most values are concentrated on the lower end"
                    else:
                        skew_type = "left-skewed"
                        interpretation = "Most values are concentrated on the higher end"
                    
                    insight = DataInsight(
                        insight_type='distribution',
                        title=f"{col} distribution is {skew_type}",
                        description=f"{col} shows {skew_type} distribution (skewness: {skewness:.2f}). {interpretation}.",
                        significance=min(abs(skewness) / 3, 1.0),
                        impact="medium",
                        evidence={
                            'skewness': float(skewness),
                            'normal_test_p_value': float(p_value),
                            'is_normal': bool(p_value > 0.05)
                        },
                        recommendations=[
                            f"Consider log transformation for {col} if using in models",
                            "Use median instead of mean for central tendency",
                            "Be aware of outliers affecting analysis"
                        ],
                        confidence=0.75
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def _rank_insights(self, insights: List[DataInsight]) -> List[DataInsight]:
        """Rank insights by importance."""
        impact_scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        # Calculate composite score
        for insight in insights:
            impact_score = impact_scores.get(insight.impact, 1)
            insight.composite_score = insight.significance * impact_score * insight.confidence
        
        # Sort by composite score
        sorted_insights = sorted(insights, key=lambda x: x.composite_score, reverse=True)
        
        return sorted_insights[:10]  # Top 10 insights
    
    def _insight_to_dict(self, insight: DataInsight) -> Dict[str, Any]:
        """Convert DataInsight to dictionary."""
        return {
            'type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'significance': round(insight.significance, 3),
            'impact': insight.impact,
            'evidence': insight.evidence,
            'recommendations': insight.recommendations,
            'confidence': round(insight.confidence, 3)
        }
    
    def forecast(
        self,
        df: pd.DataFrame,
        target_column: str,
        periods: int = 12
    ) -> Dict[str, Any]:
        """
        Forecast future values using time series analysis.
        
        Args:
            df: DataFrame with time series data
            target_column: Column to forecast
            periods: Number of periods to forecast
            
        Returns:
            Dict with forecast results
        """
        try:
            # Simple moving average forecast
            values = df[target_column].values
            
            # Calculate trend
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Generate forecast
            forecast_x = np.arange(len(values), len(values) + periods)
            forecast_values = slope * forecast_x + intercept
            
            # Calculate confidence interval
            residuals = values - (slope * x + intercept)
            std_residual = np.std(residuals)
            confidence_interval = 1.96 * std_residual  # 95% CI
            
            return {
                'success': True,
                'forecast_values': forecast_values.tolist(),
                'lower_bound': (forecast_values - confidence_interval).tolist(),
                'upper_bound': (forecast_values + confidence_interval).tolist(),
                'confidence': float(r_value**2),
                'trend_slope': float(slope)
            }
            
        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return {'success': False, 'error': str(e)}


# Global instance
_engine = None


def get_analytics_engine() -> AnalyticsEngine:
    """Get or create the global AnalyticsEngine instance."""
    global _engine
    
    if _engine is None:
        _engine = AnalyticsEngine()
    
    return _engine
