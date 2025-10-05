"""
NLP utilities for qualitative analysis
"""
from transformers import pipeline
from typing import List, Dict, Any
import logging
from collections import Counter
import re

logger = logging.getLogger(__name__)


class NLPAnalyzer:
    """NLP analyzer for qualitative comments"""
    
    def __init__(self):
        try:
            # Initialize sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("Sentiment analyzer initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize sentiment analyzer: {e}")
            self.sentiment_analyzer = None
    
    def analyze_sentiment(self, comments: List[str]) -> Dict[str, Any]:
        """
        Analyze sentiment of comments
        
        Args:
            comments: List of comment strings
            
        Returns:
            Sentiment distribution and scores
        """
        try:
            if not self.sentiment_analyzer or not comments:
                return {
                    "positive": 0.33,
                    "neutral": 0.33,
                    "negative": 0.34,
                    "dominant": "neutral"
                }
            
            # Analyze sentiments (in batches to avoid memory issues)
            batch_size = 50
            all_sentiments = []
            
            for i in range(0, len(comments), batch_size):
                batch = comments[i:i+batch_size]
                # Truncate long comments
                batch = [c[:512] for c in batch]
                sentiments = self.sentiment_analyzer(batch)
                all_sentiments.extend(sentiments)
            
            # Count sentiment labels
            sentiment_counts = Counter(s['label'].lower() for s in all_sentiments)
            total = len(all_sentiments)
            
            # Map to positive/negative/neutral
            positive = sentiment_counts.get('positive', 0) / total
            negative = sentiment_counts.get('negative', 0) / total
            neutral = 1.0 - positive - negative
            
            # Determine dominant sentiment
            dominant = max(
                [('positive', positive), ('negative', negative), ('neutral', neutral)],
                key=lambda x: x[1]
            )[0]
            
            return {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
                "dominant": dominant,
                "scores": all_sentiments
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "positive": 0.33,
                "neutral": 0.33,
                "negative": 0.34,
                "dominant": "neutral"
            }
    
    def extract_keywords(
        self,
        comments: List[str],
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Extract top keywords from comments
        
        Args:
            comments: List of comment strings
            top_n: Number of top keywords to return
            
        Returns:
            List of keyword dictionaries
        """
        try:
            # Combine all comments
            text = ' '.join(comments).lower()
            
            # Remove punctuation and split
            text = re.sub(r'[^\w\s]', ' ', text)
            words = text.split()
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                'would', 'should', 'could', 'may', 'might', 'must', 'can', 'it',
                'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we',
                'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
            }
            
            words = [w for w in words if w not in stop_words and len(w) > 2]
            
            # Count word frequencies
            word_counts = Counter(words)
            
            # Get top N
            top_keywords = word_counts.most_common(top_n)
            
            return [
                {
                    "keyword": word,
                    "count": count,
                    "frequency": count / len(words) if words else 0
                }
                for word, count in top_keywords
            ]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def get_representative_comments(
        self,
        comments: List[str],
        sentiment_filter: str = None,
        limit: int = 5
    ) -> List[str]:
        """
        Get representative comments, optionally filtered by sentiment
        
        Args:
            comments: List of comment strings
            sentiment_filter: Optional sentiment filter ('positive', 'negative', 'neutral')
            limit: Maximum number of comments to return
            
        Returns:
            List of representative comments
        """
        try:
            if not comments:
                return []
            
            # If sentiment filter requested, analyze sentiments
            if sentiment_filter and self.sentiment_analyzer:
                sentiments = self.sentiment_analyzer([c[:512] for c in comments])
                filtered_comments = [
                    comments[i] for i, s in enumerate(sentiments)
                    if s['label'].lower() == sentiment_filter
                ]
                comments = filtered_comments if filtered_comments else comments
            
            # Select diverse comments (simple approach: evenly spaced)
            if len(comments) <= limit:
                return comments
            
            step = len(comments) // limit
            return [comments[i * step] for i in range(limit)]
            
        except Exception as e:
            logger.error(f"Failed to get representative comments: {e}")
            return comments[:limit]
    
    def cluster_comments(
        self,
        comments: List[str],
        num_clusters: int = 5
    ) -> Dict[str, List[str]]:
        """
        Cluster comments into themes (simplified implementation)
        
        For production, use BERTopic or similar
        
        Args:
            comments: List of comment strings
            num_clusters: Number of clusters/themes
            
        Returns:
            Dictionary mapping theme labels to comments
        """
        try:
            # Simplified: Use keyword-based clustering
            keywords = self.extract_keywords(comments, top_n=num_clusters)
            
            clusters = {}
            for kw in keywords:
                keyword = kw['keyword']
                # Find comments containing this keyword
                matching = [c for c in comments if keyword in c.lower()]
                if matching:
                    clusters[keyword] = matching[:10]  # Limit per cluster
            
            return clusters
            
        except Exception as e:
            logger.error(f"Comment clustering failed: {e}")
            return {}
