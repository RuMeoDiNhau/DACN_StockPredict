#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests cho ứng dụng Stock AI Predictor
"""

import os
import sys
import unittest

from fastapi.testclient import TestClient

# Thêm project root vào Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.settings import TestingConfig
from data.collector import DataCollector
from data.processor import DataProcessor
from utils.helpers import validate_stock_symbol, format_currency


class TestBasicFunctionality(unittest.TestCase):
    """
    Test các chức năng cơ bản
    """

    def setUp(self):
        """
        Thiết lập test environment
        """
        self.app = create_app(TestingConfig)
        self.client = TestClient(self.app)

    def test_app_creation(self):
        """
        Test tạo FastAPI app
        """
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.title == "StockPredict")

    def test_home_page(self):
        """
        Test trang chủ
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_api_symbols(self):
        """
        Test API lấy danh sách symbols
        """
        response = self.client.get('/api/symbols')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('symbols', data)
        self.assertIsInstance(data['symbols'], list)


class TestDataCollector(unittest.TestCase):
    """
    Test DataCollector
    """

    def setUp(self):
        self.collector = DataCollector()

    def test_get_available_symbols(self):
        """
        Test lấy danh sách symbols
        """
        symbols = self.collector.get_available_symbols()
        self.assertIsInstance(symbols, list)
        self.assertGreater(len(symbols), 0)
        self.assertIn('VHM', symbols)


class TestDataProcessor(unittest.TestCase):
    """
    Test DataProcessor
    """

    def setUp(self):
        self.processor = DataProcessor()

    def test_processor_initialization(self):
        """
        Test khởi tạo processor
        """
        self.assertIsNotNone(self.processor)
        self.assertIsInstance(self.processor.scalers, dict)


class TestHelperFunctions(unittest.TestCase):
    """
    Test các helper functions
    """

    def test_validate_stock_symbol(self):
        """
        Test validate mã cổ phiếu
        """
        self.assertTrue(validate_stock_symbol('VHM'))
        self.assertTrue(validate_stock_symbol('FPT'))
        self.assertTrue(validate_stock_symbol('VCB'))

        self.assertFalse(validate_stock_symbol(''))
        self.assertFalse(validate_stock_symbol('AB'))
        self.assertFalse(validate_stock_symbol('TOOLONG'))

    def test_format_currency(self):
        """
        Test format tiền tệ
        """
        self.assertEqual(format_currency(1000000), '1,000,000 ₫')
        self.assertEqual(format_currency(50000), '50,000 ₫')
        self.assertEqual(format_currency(100.5, 'USD'), '100.50 USD')


if __name__ == '__main__':
    unittest.main(verbosity=2)