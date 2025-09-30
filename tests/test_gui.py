import unittest
import tempfile
import os
import sys
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from managers.db_manager import DatabaseManager
from managers.xlsx_manager import XLSXManager
from GUI.standard_user_window import UserWindow


class TestGUIValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure a QApplication exists for widgets
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "db")
        self.db = DatabaseManager(db_path=self.db_path, db_name="test.db")
        self.db.add_user("test_user", "password")
        self.user_id = self.db.authenticate_user("test_user", "password")[0]

        # Company & storage
        self.company_storage = os.path.join(self.test_dir, "Company")
        self.db.add_company("Company", self.company_storage)
        self.company_id = self.db.get_companies()[0][0]

        # XLSX manager to create an order file
        self.xlsx_mgr = XLSXManager(self.db)

        # Create an order file with 3 serials
        self.order_number = "TST-ORDER-1"
        file_path, count = self.xlsx_mgr.create_order_file(
            order_number=self.order_number,
            created_by=self.user_id,
            user_id=self.user_id,
            company_id=self.company_id,
            pass_fail=True,
            pass_fail_timestamp="",
            failure_explanation="",
            fix_explanation="",
            serial_prefix="TST-",
            serial_start=1,
            serial_count=3
        )
        self.file_path = file_path

        # Create the UserWindow (we don't show it)
        self.window = UserWindow("test_user", self.user_id, self.db, self.xlsx_mgr)
        # Stub QMessageBox.warning to avoid modal dialogs during tests
        from PyQt5.QtWidgets import QMessageBox
        self._orig_warning = QMessageBox.warning

        def _test_warning(parent, title, text, *args, **kwargs):
            # store last warning text for inspection and return OK role
            self._last_warning = text
            return QMessageBox.Ok

        QMessageBox.warning = _test_warning

    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except Exception:
            pass
        # Restore QMessageBox.warning
        from PyQt5.QtWidgets import QMessageBox
        if hasattr(self, '_orig_warning') and self._orig_warning:
            QMessageBox.warning = self._orig_warning

    def test_sn_not_found(self):
        # Load the created XLSX file
        self.window.load_xlsx_data(self.file_path)
        # Enter an SN that is not present
        self.window.sn_input.setText("NOT-IN-FILE-000")
        ok = self.window.ensure_sn_is_loaded()
        self.assertFalse(ok)

    def test_sn_found(self):
        # Load the created XLSX file
        self.window.load_xlsx_data(self.file_path)
        # Use an SN that is present (first serial is TST-00001)
        present_sn = "TST-00001"
        self.window.sn_input.setText(present_sn)
        ok = self.window.ensure_sn_is_loaded()
        self.assertTrue(ok)
        self.assertEqual(self.window.current_serial, present_sn)


if __name__ == '__main__':
    unittest.main(verbosity=2)
