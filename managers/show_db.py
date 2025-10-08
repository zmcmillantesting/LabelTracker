from db_manager import DatabaseManager
import pprint

def main():
    db = DatabaseManager()  # uses default path/name in db_manager.py

    print("\n=== USERS ===")
    with db.get_connection() as conn:
        for row in conn.execute("SELECT * FROM users"):
            print(row)

    print("\n=== COMPANIES ===")
    with db.get_connection() as conn:
        for row in conn.execute("SELECT * FROM companies"):
            print(row)

    print("\n=== BOARDS ===")
    with db.get_connection() as conn:
        for row in conn.execute("SELECT * FROM boards"):
            print(row)

    print("\n=== ORDERS ===")
    with db.get_connection() as conn:
        for row in conn.execute("SELECT * FROM orders"):
            print(row)

    print("\n=== Board IDs===")
    with db.get_connection() as conn:
        for row in conn.execute("SELECT board_name FROM boards"):
            print(row)

if __name__ == "__main__":
    main()
