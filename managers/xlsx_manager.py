import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from datetime import datetime
from managers.db_manager import DatabaseManager


class XLSXManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _generate_serial_numbers(self, prefix="CUSTID-ORDNO-", start=1, count=100):
        """Generate serial numbers like CUSTID-ORDNO-00001, CUSTID-ORDNO-00002..."""
        return [f"{prefix}{str(i).zfill(5)}" for i in range(start, start + count)]

    def create_order_file(self, order_number, created_by, user_id, company_id, pass_fail, 
                         pass_fail_timestamp, failure_explanation, fix_explanation, 
                         board_id=None, serial_prefix="CUSTID-ORDNO-", serial_start=1, serial_count=50):
        """Create a new XLSX file for an order and save it in the board-level folder."""

        # 1. Validate board_id is provided
        if not board_id:
            raise ValueError("board_id is required to create order file")

        # 2. Get board details from DB (includes board_path)
        board = self.db.get_board_by_id(board_id)
        if not board:
            raise ValueError(f"Board {board_id} not found")
        
        board_path = board[3]  # board_path from database

        # 3. Ensure board folder exists
        os.makedirs(board_path, exist_ok=True)

        # 4. Build full file path (saved inside board folder)
        filename = f"{order_number}.xlsx"
        file_path = os.path.join(board_path, filename)

        # 5. Generate workbook
        wb = Workbook()
        ws = wb.active
        ws.title = f"{order_number} Tracking"

        # 6. Write headers
        headers = ["User ID", "Company ID", "Board ID", "Serial Number", "pass/fail", 
                  "pass/fail timestamp", "if failed explanation", "if fixed explanation"]
        ws.append(headers)

        # Format headers (bold and centered)
        for col in ws[1]:
            col.font = Font(bold=True)
            col.alignment = Alignment(horizontal="center", vertical="center")

        # 7. Add serial numbers with proper data alignment
        serials = self._generate_serial_numbers(prefix=serial_prefix, start=serial_start, count=serial_count)
        
        for sn in serials:
            # Create row data that matches the headers exactly
            row_data = [
                user_id,                    # User ID
                company_id,                 # Company ID  
                board_id,                   # Board ID
                sn,                         # Serial Number
                "Pass" if pass_fail else "Fail",  # pass/fail
                pass_fail_timestamp,        # pass/fail timestamp
                failure_explanation if not pass_fail else None,  # if failed explanation (None if passed)
                fix_explanation if not pass_fail else None       # if fixed explanation (None if passed)
            ]
            ws.append(row_data)

        # 8. Format explanation columns (wrap text)
        failure_explanation_col = 7  # "if failed explanation" column
        fix_explanation_col = 8      # "if fixed explanation" column
        
        for row in range(2, len(serials) + 2):  # Start from row 2 (skip header)
            ws.cell(row=row, column=failure_explanation_col).alignment = Alignment(wrap_text=True)
            ws.cell(row=row, column=fix_explanation_col).alignment = Alignment(wrap_text=True)

        # 9. Auto-size columns
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            # Set minimum width and add padding
            ws.column_dimensions[col_letter].width = max(max_length + 2, 10)

        # 10. Save file
        wb.save(file_path)

        # 11. Register order in DB
        self.db.add_order(order_number, company_id, board_id, file_path, created_by)

        return file_path, len(serials)