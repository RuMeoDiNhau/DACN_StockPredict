#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent cho phân tích tin tức và sentiment chứng khoán
"""

import openai
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import re

from utils.logger import setup_logger
from config.settings import Config

logger = setup_logger(__name__)

class AIAgent:
    """
    AI Agent để phân tích tin tức và tạo insights
    """
    
    def __init__(self):
        """
        Khởi tạo AI Agent
        """
        self.openai_key = Config.OPENAI_API_KEY
        self.enabled = Config.ENABLE_AI_AGENT
        
        # Setup OpenAI nếu có API key
        if self.openai_key and self.openai_key != 'your-openai-api-key-here':
            openai.api_key = self.openai_key
            self.llm_enabled = True
        else:
            self.llm_enabled = False
            logger.warning("⚠️ OpenAI API key chưa được cấu hình")
        
        logger.info("🤖 Khởi tạo AI Agent thành công")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Phân tích sentiment của văn bản
        
        Args:
            text: Văn bản cần phân tích
        
        Returns:
            Dict chứa kết quả sentiment
        """
        try:
            if not text:
                return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
            
            # Sử dụng TextBlob cho sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Phân loại sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Tính confidence dựa trên độ subjectivity
            confidence = subjectivity
            
            return {
                'sentiment': sentiment,
                'score': polarity,
                'confidence': confidence,
                'subjectivity': subjectivity
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi phân tích sentiment: {str(e)}")
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}