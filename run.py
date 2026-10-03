#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local entry point for the separated StockPredict MVP."""

import uvicorn

from backend.app.main import create_app
from config.settings import Config


def main() -> None:
    """Run the FastAPI REST API and its static frontend on localhost."""
    uvicorn.run(create_app(), host=Config.HOST, port=Config.PORT, log_level="info")


if __name__ == '__main__':
    main()
