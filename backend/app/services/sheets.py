"""Google Sheets API connector for manual sellers."""

import logging
import json
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class GoogleSheetsConnector:
    """Connect to Google Sheets for order/product data (manual sellers)."""

    def __init__(self, credentials_json: str = "", spreadsheet_id: str = ""):
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        if credentials_json or settings.GOOGLE_SHEETS_CREDENTIALS_JSON:
            self._init_client(credentials_json or settings.GOOGLE_SHEETS_CREDENTIALS_JSON)

    def _init_client(self, credentials_json: str):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            creds_dict = json.loads(credentials_json)
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly",
            ]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            self.client = gspread.authorize(credentials)
            logger.info("Google Sheets client initialized")
        except Exception as e:
            logger.warning(f"Google Sheets init failed: {e}")

    async def get_orders(self, sheet_name: str = "Orders") -> list:
        if not self.client or not self.spreadsheet_id:
            return self._mock_orders()
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            records = sheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"Sheets get_orders error: {e}")
            return []

    async def get_products(self, sheet_name: str = "Products") -> list:
        if not self.client or not self.spreadsheet_id:
            return self._mock_products()
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            records = sheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"Sheets get_products error: {e}")
            return []

    async def search_order(self, query: str, sheet_name: str = "Orders") -> list:
        orders = await self.get_orders(sheet_name)
        return [o for o in orders if query.lower() in str(o).lower()]

    async def add_order(self, order_data: dict, sheet_name: str = "Orders") -> bool:
        if not self.client or not self.spreadsheet_id:
            logger.info(f"[MOCK] Would add order: {order_data}")
            return True
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            sheet.append_row(list(order_data.values()))
            return True
        except Exception as e:
            logger.error(f"Sheets add_order error: {e}")
            return False

    def _mock_orders(self) -> list:
        return [
            {"Order ID": "S001", "Customer": "Priya Sharma", "Phone": "+919876543210",
             "Product": "Gold Jhumka Set", "Amount": "2499", "Status": "Shipped",
             "Tracking": "DTDC123456"},
            {"Order ID": "S002", "Customer": "Anita Patel", "Phone": "+919887654321",
             "Product": "Silver Anklet", "Amount": "899", "Status": "Preparing"},
        ]

    def _mock_products(self) -> list:
        return [
            {"Name": "Gold Jhumka Set", "Price": "2499", "Stock": "8", "Category": "Earrings"},
            {"Name": "Silver Anklet", "Price": "899", "Stock": "15", "Category": "Anklets"},
            {"Name": "Pearl Necklace", "Price": "3999", "Stock": "3", "Category": "Necklaces"},
            {"Name": "Kundan Choker", "Price": "5499", "Stock": "2", "Category": "Necklaces"},
        ]
