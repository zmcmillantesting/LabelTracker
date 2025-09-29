# tests/test_database.py
import unittest
import tempfile
import os
import shutil
from managers.db_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_db")
        self.db = DatabaseManager(db_path=self.db_path, db_name="test_data.db")

    def tearDown(self):
        # Clean up temporary directory
        db_file = os.path.join(self.db_path, "test_data.db")
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except PermissionError:
                pass
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_database(self):
        """Test database initialization creates required tables"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

            self.assertIn("users", tables)
            self.assertIn("companies", tables)
            self.assertIn("boards", tables)
            self.assertIn("orders", tables)

    def test_user_operations(self):
        """Test user add and authentication"""
        # Add a user
        self.db.add_user("testuser", "password123", role="admin")

        # Authenticate with correct password
        user = self.db.authenticate_user("testuser", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "testuser")
        self.assertEqual(user[2], "admin")

        # Wrong password should fail
        user = self.db.authenticate_user("testuser", "wrongpass")
        self.assertIsNone(user)

    def test_company_operations(self):
        """Test company add and fetch"""
        self.db.add_company("Test Company", "C:/Clients/TestCompany")
        companies = self.db.get_companies()

        self.assertEqual(len(companies), 1)
        self.assertEqual(companies[0][1], "Test Company")
        self.assertEqual(companies[0][2], "C:/Clients/TestCompany")

    def test_board_operations(self):
        """Test board add and fetch"""
        # Add company first
        self.db.add_company("Test Company", "C:/Clients/TestCompany")
        companies = self.db.get_companies()
        company_id = companies[0][0]

        # Add a board
        self.db.add_board(company_id, "MainBoard")
        boards = self.db.get_boards_by_company(company_id)

        self.assertEqual(len(boards), 1)
        self.assertEqual(boards[0][1], "MainBoard")

    def test_order_operations(self):
        """Test order add, update, and fetch"""
        # Add company + board + user
        self.db.add_company("Test Company", "C:/Clients/TestCompany")
        companies = self.db.get_companies()
        company_id = companies[0][0]

        self.db.add_board(company_id, "MainBoard")
        boards = self.db.get_boards_by_company(company_id)
        board_id = boards[0][0]

        self.db.add_user("orderuser", "pass123")
        user = self.db.authenticate_user("orderuser", "pass123")
        user_id = user[0]

        # Add order
        self.db.add_order("ORD12345", company_id, board_id, "C:/Clients/TestCompany/ORD12345.xlsx", created_by=user_id)

        orders = self.db.get_orders(company_id)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0][1], "ORD12345")

        # Update order status
        order_id = orders[0][0]
        self.db.update_order_status(order_id, "Complete")

        updated_orders = self.db.get_orders(company_id)
        self.assertEqual(updated_orders[0][4], "Complete")  # status column


if __name__ == "__main__":
    unittest.main(verbosity=2)
