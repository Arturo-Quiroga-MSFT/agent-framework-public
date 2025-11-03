"""Evaluation metrics for MAF agent responses."""

import re
from typing import List, Dict
from datetime import datetime


class AgentEvaluator:
    """Evaluation metrics for MAF agent quality assessment."""
    
    def evaluate_response(self, response: str, expected_topics: List[str] = None) -> Dict:
        """Evaluate agent response quality.
        
        Args:
            response: The agent's response text
            expected_topics: List of topics that should be covered
            
        Returns:
            Dictionary of evaluation metrics
        """
        expected_topics = expected_topics or []
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "length": len(response),
            "word_count": len(response.split()),
            "topic_coverage": self._check_topic_coverage(response, expected_topics),
            "has_citations": self._check_citations(response),
            "has_numbers": self._check_numbers(response),
            "has_structure": self._check_structure(response),
            "sentiment_neutral": self._check_sentiment(response),
            "overall_score": 0.0
        }
        
        # Calculate overall score (weighted average)
        weights = {
            "topic_coverage": 0.35,
            "has_citations": 0.25,
            "has_numbers": 0.20,
            "has_structure": 0.10,
            "sentiment_neutral": 0.10
        }
        
        metrics["overall_score"] = (
            metrics["topic_coverage"] * weights["topic_coverage"] +
            (1.0 if metrics["has_citations"] else 0.0) * weights["has_citations"] +
            (1.0 if metrics["has_numbers"] else 0.0) * weights["has_numbers"] +
            (1.0 if metrics["has_structure"] else 0.0) * weights["has_structure"] +
            (1.0 if metrics["sentiment_neutral"] else 0.0) * weights["sentiment_neutral"]
        )
        
        return metrics
    
    def _check_topic_coverage(self, response: str, topics: List[str]) -> float:
        """Check what percentage of expected topics are covered.
        
        Args:
            response: Response text
            topics: List of expected topics
            
        Returns:
            Coverage percentage (0.0 to 1.0)
        """
        if not topics:
            return 1.0
        
        response_lower = response.lower()
        covered = sum(1 for topic in topics if topic.lower() in response_lower)
        return covered / len(topics)
    
    def _check_citations(self, response: str) -> bool:
        """Check if response includes citations or sources.
        
        Args:
            response: Response text
            
        Returns:
            True if citations are present
        """
        citation_patterns = [
            r'\d{4}',  # Years (e.g., 2025)
            r'according to',
            r'source:',
            r'https?://',
            r'reported by',
            r'as of',
            r'data from'
        ]
        return any(re.search(pattern, response, re.IGNORECASE) 
                  for pattern in citation_patterns)
    
    def _check_numbers(self, response: str) -> bool:
        """Check if response includes quantitative data.
        
        Args:
            response: Response text
            
        Returns:
            True if numbers/data are present
        """
        # Look for numbers, percentages, currencies
        number_patterns = [
            r'\d+\.?\d*\s*%',  # Percentages
            r'\$\d+',           # Currency
            r'\d+\.?\d*',       # Numbers
        ]
        return any(re.search(pattern, response) for pattern in number_patterns)
    
    def _check_structure(self, response: str) -> bool:
        """Check if response has good structure (paragraphs, bullets, etc.).
        
        Args:
            response: Response text
            
        Returns:
            True if well-structured
        """
        # Check for multiple paragraphs or list items
        has_paragraphs = response.count('\n\n') >= 1
        has_lists = bool(re.search(r'[-•*]\s', response))
        has_numbering = bool(re.search(r'\d+\.\s', response))
        
        return has_paragraphs or has_lists or has_numbering
    
    def _check_sentiment(self, response: str) -> bool:
        """Check if response maintains neutral, analytical tone.
        
        Args:
            response: Response text
            
        Returns:
            True if tone is appropriate
        """
        # Simple heuristic: avoid overly emotional language
        emotional_words = [
            'amazing', 'terrible', 'awful', 'fantastic', 
            'horrible', 'love', 'hate', 'stupid', 'brilliant'
        ]
        response_lower = response.lower()
        return not any(word in response_lower for word in emotional_words)
    
    def get_quality_label(self, score: float) -> str:
        """Get quality label based on score.
        
        Args:
            score: Overall score (0.0 to 1.0)
            
        Returns:
            Quality label string
        """
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
