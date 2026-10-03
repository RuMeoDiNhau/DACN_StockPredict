#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests cho ứng dụng Stock AI Predictor
"""

import os
import sys
import tempfile
import unittest

import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch

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
        self.temp_dir = tempfile.TemporaryDirectory()

        class TestConfig(TestingConfig):
            DATABASE_PATH = os.path.join(self.temp_dir.name, "test.db")

        self.app = create_app(TestConfig)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.temp_dir.cleanup()

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

    def test_symbol_detail_page_uses_existing_template(self):
        rows = pd.DataFrame([{
            'Date': pd.Timestamp('2024-01-02'),
            'Open': 100.0,
            'High': 105.0,
            'Low': 99.0,
            'Close': 104.0,
            'Volume': 1000.0,
            'Symbol': 'VHM',
        }])
        with patch.object(self.app.state.db, 'get_stock_data', return_value=rows), \
             patch.object(self.app.state.db, 'get_predictions', return_value=pd.DataFrame()):
            response = self.client.get('/symbol/VHM')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Dữ liệu OHLCV gần nhất', response.text)

    def test_api_stock_data_uses_normalized_schema(self):
        rows = pd.DataFrame([
            {
                'Date': pd.Timestamp('2024-01-02'),
                'Open': 100.0,
                'High': 105.0,
                'Low': 99.0,
                'Close': 104.0,
                'Volume': 1000.0,
                'Symbol': 'VHM',
            }
        ])
        with patch.object(self.app.state.db, 'get_stock_data', return_value=rows):
            response = self.client.get('/api/stocks/VHM')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(
            list(payload['data'][0]),
            ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol'],
        )
        self.assertEqual(payload['data'][0]['Date'], '2024-01-02T00:00:00')

    def test_endpoint_error_statuses_and_market_status(self):
        self.assertEqual(self.client.get('/api/stocks/NOPE').status_code, 404)
        self.assertEqual(self.client.get('/api/stocks/!').status_code, 422)
        self.assertEqual(self.client.get('/symbol/NOPE').status_code, 404)
        market = self.client.get('/api/market-status')
        self.assertEqual(market.status_code, 200)
        self.assertEqual(market.json()['timezone'], 'Asia/Ho_Chi_Minh')


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
