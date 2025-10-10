import sqlite3, sys, os, hashlib, logging, datetime
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
                    client_path TEXT NOT NULL,
                    cust_id TEXT DEFAULT NULL
                )""")

                query.execute("""
                CREATE TABLE IF NOT EXISTS boards (
                    board_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    board_name TEXT NOT NULL,
                    board_path TEXT NOT NULL,
                    archived INTEGER NOT NULL DEFAULT 0,
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

                # Ensure 'archived' column on boards exists (0/1)
                query.execute("PRAGMA table_info(boards)")
                cols = [r[1] for r in query.fetchall()]
                if 'archived' not in cols:
                    query.execute("ALTER TABLE boards ADD COLUMN archived INTEGER NOT NULL DEFAULT 0")
                    conn.commit()

                # Ensure 'cust_id' column exists on companies (nullable text)
                query.execute("PRAGMA table_info(companies)")
                comp_cols = [r[1] for r in query.fetchall()]
                if 'cust_id' not in comp_cols:
                    query.execute("ALTER TABLE companies ADD COLUMN cust_id TEXT DEFAULT NULL")
                    conn.commit()

                # Ensure 'archived' column on companies exists (0/1)
                if 'archived' not in comp_cols:
                    query.execute("ALTER TABLE companies ADD COLUMN archived INTEGER NOT NULL DEFAULT 0")
                    conn.commit()

                # Ensure at least one admin user exists (seed default admin)
                query.execute("SELECT user_id FROM users WHERE username=?", ("admin",))
                if not query.fetchone():
                    import hashlib
                    pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
                    query.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        ("admin", pw_hash, "admin"),
                    )
                    conn.commit()
                    logger.info("Seeded default admin user 'admin'")

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
    def add_company(self, company_name, client_path, cust_id=None):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "INSERT INTO companies (company_name, client_path, cust_id) VALUES (?, ?, ?)",
                    (company_name, client_path, cust_id),
                )
                conn.commit()

            if not os.path.exists(client_path):
                os.makedirs(client_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to add company: {e}")
            raise

    def get_companies(self):
        # Backwards compatible: by default exclude archived companies from normal lists
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("PRAGMA table_info(companies)")
                cols = [r[1] for r in query.fetchall()]
                includes_archived = False
                # If caller wants archived included they should use get_companies(include_archived=True)
                # Default behaviour: only active companies
                query_str = "SELECT company_id, company_name, client_path, cust_id FROM companies WHERE archived=0" if 'archived' in cols else "SELECT company_id, company_name, client_path, cust_id FROM companies"
                query.execute(query_str)
                return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to get companies: {e}")
            raise

    def get_companies_all(self, include_archived=False):
        """Return companies. If include_archived=True return all companies including archived ones."""
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                if include_archived:
                    query.execute("SELECT company_id, company_name, client_path, cust_id, archived FROM companies")
                else:
                    # return same 4-column shape for compatibility
                    query.execute("SELECT company_id, company_name, client_path, cust_id FROM companies WHERE archived=0")
                return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to get companies (all): {e}")
            raise

    def get_users(self, user_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("SELECT * FROM users")
            return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise

    def archive_company(self, company_id):
        """Archive a company and its boards (mark archived=1)."""
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("UPDATE companies SET archived=1 WHERE company_id=?", (company_id,))
                # also archive boards belonging to the company
                query.execute("UPDATE boards SET archived=1 WHERE company_id=?", (company_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to archive company: {e}")
            raise

    def unarchive_company(self, company_id):
        """Unarchive a company and optionally unarchive its boards."""
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("UPDATE companies SET archived=0 WHERE company_id=?", (company_id,))
                # also unarchive boards that were archived with the company
                query.execute("UPDATE boards SET archived=0 WHERE company_id=?", (company_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to unarchive company: {e}")
            raise

    # ---------------- Board methods ----------------
    def add_board(self, company_id, board_name, board_path):
        if not board_path:
            board_path = ""
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("" \
                "INSERT INTO boards (company_id, board_name, board_path) VALUES (?, ?, ?)",
                    (company_id, board_name, board_path),
                )
                conn.commit()
            if not os.path.exists(board_path):
                os.makedirs(board_path, exist_ok=True)

        except Exception as e:
            logger.error(f"Failed to add board: {e}")
            raise
        
    def get_boards_by_company(self, company_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute(
                    "SELECT board_id, board_name, archived FROM boards WHERE company_id=?",
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

                created_at = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
                query.execute(
                    "INSERT INTO orders (order_number, company_id, board_id, file_path, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                    (order_number, company_id, board_id, file_path, created_at, created_by),
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

    def archive_order(self, order_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("UPDATE orders SET status='Archived' WHERE order_id=?", (order_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to archive order: {e}")
            raise

    def unarchive_order(self, order_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("UPDATE orders SET status='Pending' WHERE order_id=?", (order_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to unarchive order: {e}")
            raise

    def get_archived_orders(self):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("SELECT * FROM orders WHERE status='Archived'")
                return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to get archived orders: {e}")
            raise

    def get_archived_orders_with_username(self):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("""
                    SELECT o.order_number,
                        c.company_name,
                        b.board_name,
                        o.status,
                        o.file_path,
                        o.created_at,
                        u.username
                    FROM orders o
                    LEFT JOIN companies c ON o.company_id = c.company_id
                    LEFT JOIN boards b ON o.board_id = b.board_id
                    LEFT JOIN users u ON o.created_by = u.user_id
                    WHERE o.status = 'Archived'
                    ORDER BY o.created_at DESC
                """)
                return query.fetchall()
        except Exception as e:
            logger.error(f"Faield to get archived orders with usernames: {e}")
            raise

    def archive_board(self, board_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("UPDATE boards SET archived=1 WHERE board_id=?", (board_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to archive board: {e}")
            raise

    def unarchive_board(self, board_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("UPDATE boards SET archived=0 WHERE board_id=?", (board_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to unarchive board: {e}")
            raise

    def get_boards(self, company_id=None, include_archived=False):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                if company_id:
                    if include_archived:
                        query.execute("SELECT board_id, board_name, archived FROM boards WHERE company_id=?", (company_id,))
                    else:
                        query.execute("SELECT board_id, board_name, archived FROM boards WHERE company_id=? AND archived=0", (company_id,))
                else:
                    if include_archived:
                        query.execute("SELECT board_id, board_name, archived FROM boards")
                    else:
                        query.execute("SELECT board_id, board_name, archived FROM boards WHERE archived=0")
                return query.fetchall()
        except Exception as e:
            logger.error(f"Failed to get boards: {e}")
            raise

    def delete_order_permanently(self, order_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("DELETE FROM orders WHERE order_id=?", (order_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to permanently delete order: {e}")
            raise

    def delete_board_permanently(self, board_id):
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                query.execute("DELETE FROM boards WHERE board_id=?", (board_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to permanently delete board: {e}")
            raise

    def delete_company_permanently(self, company_id):
        """Permanently delete a company and all related boards and orders.
        This does a cascading delete within a transaction to avoid FK issues.
        """
        try:
            with self.get_connection() as conn:
                query = conn.cursor()
                # Delete orders referencing company
                query.execute("DELETE FROM orders WHERE company_id=?", (company_id,))
                # Delete boards
                query.execute("DELETE FROM boards WHERE company_id=?", (company_id,))
                # Finally delete company
                query.execute("DELETE FROM companies WHERE company_id=?", (company_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to permanently delete company: {e}")
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
