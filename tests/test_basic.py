#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline endpoint tests for the separated FastAPI/SQLite web MVP."""

import os
import sys
import tempfile
import unittest

import pandas as pd
from fastapi.testclient import TestClient

# Thêm project root vào Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import create_app
from config.settings import TestingConfig
from data.collector import DataCollector
from data.processor import DataProcessor
from utils.helpers import validate_stock_symbol, format_currency


class TestWebMvpEndpoints(unittest.TestCase):
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
        self.app.state.db.upsert_stock_data(pd.DataFrame([
            {'Date': '2024-01-02', 'Open': 100, 'High': 105, 'Low': 99, 'Close': 104, 'Volume': 1000, 'Symbol': 'VHM'},
            {'Date': '2024-01-03', 'Open': 104, 'High': 106, 'Low': 103, 'Close': 105, 'Volume': 1100, 'Symbol': 'VHM'},
        ]))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True, 'service': 'stockpredict-api'})

    def test_api_symbols(self):
        response = self.client.get('/api/symbols')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True, 'symbols': ['VHM']})

    def test_api_stock_data_uses_normalized_schema(self):
        response = self.client.get('/api/stocks/vhm?limit=2')
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
        self.assertEqual(self.client.get('/api/stocks/VHM?limit=0').status_code, 422)
        self.assertEqual(self.client.get('/api/stocks/VHM?limit=91').status_code, 422)
        market = self.client.get('/api/market-status')
        self.assertEqual(market.status_code, 200)
        self.assertEqual(market.json()['timezone'], 'Asia/Ho_Chi_Minh')

    def test_frontend_routes_are_static_and_direct(self):
        home = self.client.get('/')
        detail = self.client.get('/symbol/VHM')
        self.assertEqual(home.status_code, 200)
        self.assertEqual(detail.status_code, 200)
        self.assertIn('StockPredict MVP', home.text)
        self.assertIn('Dữ liệu OHLCV từ SQLite qua REST API', detail.text)
        self.assertNotIn('VHM</td>', detail.text)


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
