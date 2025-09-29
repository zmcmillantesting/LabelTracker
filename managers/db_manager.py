import sqlite3, sys, os, hashlib, logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class DatabaseManager:
    def __init__(self, db_path=r"P:\EMS_TR_PATH\LabelTrackingApplication", db_name="EMSTrackingData.db"):
        self.db_path = resource_path(db_path)
        self.db_name = db_name
        self.full_db_path = os.path.join(self.db_path, self.db_name)

        os.makedirs(self.db_path, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.full_db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def init_db(self):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()

                query.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")

                query.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL UNIQUE,
                    client_path TEXT NOT NULL
                )""")

                query.execute("""
                CREATE TABLE IF NOT EXISTS boards (
                    board_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    board_name TEXT NOT NULL,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                )""")

                query.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT NOT NULL,
                    company_id INTEGER NOT NULL,
                    board_id INTEGER,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    file_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    FOREIGN KEY (board_id) REFERENCES boards(board_id),
                    FOREIGN KEY (created_by) REFERENCES users(user_id)
                )""")

                conn.commit()

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    # ---------------- User methods ----------------
    def add_user(self, username, password, role="user"):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, pw_hash, role),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
            raise

    def authenticate_user(self, username, password):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "SELECT user_id, username, role FROM users WHERE username=? AND password_hash=?",
                    (username, pw_hash),
                )
                return query.fetchone()
        except Exception as e:
            logger.error(f"Failed to authenticate user: {e}")
            raise

    # ---------------- Company methods ----------------
    def add_company(self, company_name, client_path):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "INSERT INTO companies (company_name, client_path) VALUES (?, ?)",
                    (company_name, client_path),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add company: {e}")
            raise

    def get_companies(self):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("SELECT company_id, company_name, client_path FROM companies")
                return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to get companies: {e}")
            raise

    # ---------------- Board methods ----------------
    def add_board(self, company_id, board_name):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "INSERT INTO boards (company_id, board_name) VALUES (?, ?)",
                    (company_id, board_name),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add board: {e}")
            raise

    def get_boards_by_company(self, company_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "SELECT board_id, board_name FROM boards WHERE company_id=?",
                    (company_id,),
                )
                return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch boards for company {company_id}: {e}")
            raise

    # ---------------- Order methods ----------------
    def add_order(self, order_number, company_id, board_id, file_path, created_by):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "INSERT INTO orders (order_number, company_id, board_id, file_path, created_by) VALUES (?, ?, ?, ?, ?)",
                    (order_number, company_id, board_id, file_path, created_by),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add order: {e}")
            raise

    def update_order_status(self, order_id, status):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "UPDATE orders SET status=? WHERE order_id=?", (status, order_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            raise

    def get_orders(self, company_id=None):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                if company_id:
                    query.execute("SELECT * FROM orders WHERE company_id=?", (company_id,))
                else:
                    query.execute("SELECT * FROM orders")
                return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            raise
