from typing import Dict, List, Optional
from app.core.aws_connection import aws_client


class ToneAnalyzer:
    """Service for analyzing tone/sentiment using AWS Comprehend."""
    
    def __init__(self):
        """Initialize the ToneAnalyzer with AWS Comprehend client."""
        self.comprehend_client = aws_client.get_comprehend_client()
    
    def analyze_sentiment(self, text: str, language_code: str = 'en') -> Dict:
        """
        Analyze the sentiment of a given text.
        
        Args:
            text: The text to analyze
            language_code: Language code (default: 'en')
        
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            response = self.comprehend_client.detect_sentiment(
                Text=text,
                LanguageCode=language_code
            )
            return response
        except Exception as e:
            raise Exception(f"Error analyzing sentiment: {str(e)}")
    
    def analyze_tone(self, text: str, language_code: str = 'en') -> Dict:
        """
        Analyze the tone/emotions of a given text.
        
        Args:
            text: The text to analyze
            language_code: Language code (default: 'en')
        
        Returns:
            Dictionary containing tone analysis results
        """
        try:
            response = self.comprehend_client.detect_entities(
                Text=text,
                LanguageCode=language_code
            )
            return response
        except Exception as e:
            raise Exception(f"Error analyzing tone: {str(e)}")
    
    def analyze_key_phrases(self, text: str, language_code: str = 'en') -> Dict:
        """
        Extract key phrases from a given text.
        
        Args:
            text: The text to analyze
            language_code: Language code (default: 'en')
        
        Returns:
            Dictionary containing key phrases
        """
        try:
            response = self.comprehend_client.detect_key_phrases(
                Text=text,
                LanguageCode=language_code
            )
            return response
        except Exception as e:
            raise Exception(f"Error analyzing key phrases: {str(e)}")
    
    def batch_analyze_sentiment(self, texts: List[str], language_code: str = 'en') -> List[Dict]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            language_code: Language code (default: 'en')
        
        Returns:
            List of dictionaries containing sentiment analysis results
        """
        results = []
        try:
            for text in texts:
                result = self.analyze_sentiment(text, language_code)
                results.append(result)
            return results
        except Exception as e:
            raise Exception(f"Error in batch analysis: {str(e)}")
