"""
OpenAI API client for text generation and summarization
"""
from openai import OpenAI
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI GPT-4 API"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"
    
    def summarize_comments(
        self,
        comments: List[str],
        segment: str,
        max_length: int = 200
    ) -> str:
        """
        Generate concise summary of qualitative comments for a segment
        
        Args:
            comments: List of comment strings
            segment: Segment name
            max_length: Maximum word count for summary
            
        Returns:
            Concise summary text
        """
        try:
            # Limit to first 50 comments to avoid token limits
            sample_comments = comments[:50]
            
            prompt = f"""
            Summarize the following audience feedback for the "{segment}" segment.
            Focus on:
            1. Common themes
            2. Emotional reactions
            3. Specific creative elements mentioned
            
            Comments:
            {chr(10).join(f"- {c}" for c in sample_comments)}
            
            Provide a concise summary in {max_length} words or less.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a marketing insights analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Comment summarization failed: {e}")
            raise
    
    def generate_recommendation_justification(
        self,
        creative_element: str,
        quant_data: Dict[str, Any],
        qual_themes: List[str],
        segment: str
    ) -> str:
        """
        Generate clear, actionable justification for a recommendation
        
        Args:
            creative_element: The element being recommended for change
            quant_data: Quantitative metrics
            qual_themes: Qualitative themes
            segment: Audience segment
            
        Returns:
            Justification text
        """
        try:
            prompt = f"""
            Generate a concise justification for the following creative recommendation:
            
            Segment: {segment}
            Creative Element: {creative_element}
            
            Quantitative Evidence:
            - Metric: {quant_data.get('metric', 'N/A')}
            - Impact: {quant_data.get('delta', 0):.2%} change
            - Confidence Interval: {quant_data.get('ci_95', 'N/A')}
            
            Qualitative Themes:
            {chr(10).join(f"- {theme}" for theme in qual_themes)}
            
            Write a 2-3 sentence justification that:
            1. States the problem clearly
            2. References both data sources
            3. Explains why this change will improve performance
            
            Use professional but accessible language for marketing stakeholders.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative strategy consultant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Justification generation failed: {e}")
            raise
    
    def generate_executive_summary(
        self,
        experiment_data: Dict[str, Any]
    ) -> str:
        """
        Create executive summary for experiment results
        
        Args:
            experiment_data: Dictionary with experiment metrics and findings
            
        Returns:
            Executive summary text
        """
        try:
            prompt = f"""
            Create an executive summary for this creative pre-testing experiment:
            
            Video: {experiment_data.get('title', 'Untitled')}
            
            Key Findings:
            - Overall brand favorability: {experiment_data.get('overall_favorability', 0):.2%}
            - Overall purchase intent: {experiment_data.get('overall_intent', 0):.2%}
            - Top performing segment: {experiment_data.get('top_segment', 'N/A')}
            - Weakest performing segment: {experiment_data.get('weak_segment', 'N/A')}
            
            Top 3 Recommendations:
            {chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(experiment_data.get('top_recommendations', [])))}
            
            Write a 150-word executive summary suitable for C-suite presentation.
            Include:
            1. Overall performance assessment
            2. Key opportunities
            3. Recommended next steps
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a marketing executive."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            raise
    
    def extract_themes_from_comments(
        self,
        comments: List[str],
        num_themes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract main themes from comments using GPT-4
        
        Args:
            comments: List of comment strings
            num_themes: Number of themes to extract
            
        Returns:
            List of theme dictionaries
        """
        try:
            sample_comments = comments[:100]  # Limit for token management
            
            prompt = f"""
            Analyze the following comments and extract the top {num_themes} themes.
            For each theme, provide:
            1. A short label (2-4 words)
            2. Key keywords associated with the theme
            3. Estimated prevalence (0-1)
            
            Comments:
            {chr(10).join(f"- {c}" for c in sample_comments)}
            
            Return as JSON array with format:
            [
                {{
                    "theme_label": "string",
                    "keywords": ["word1", "word2"],
                    "prevalence": 0.0-1.0
                }}
            ]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in qualitative data analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get("themes", [])
            
        except Exception as e:
            logger.error(f"Theme extraction failed: {e}")
            return []
