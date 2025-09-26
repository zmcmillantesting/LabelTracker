# tests/test_logger.py
import unittest
import tempfile
import os
import logging
import shutil

from utils.logger import setup_logging


class TestLogger(unittest.TestCase):
    def setUp(self):
        # Temp dir for logs
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, "test_app.log")

        self.logger = logging.getLogger("test_logger")

        # Properly close existing handlers
        for h in self.logger.handlers:
            h.close()
        self.logger.handlers.clear()

        file_handler = logging.FileHandler(self.log_file, mode="w", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

    def tearDown(self):
        for h in self.logger.handlers:
            h.close()
        self.logger.handlers.clear()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_log_info_message(self):
        """Test that INFO messages are written to the log file"""
        test_message = "This is an info log test"
        self.logger.info(test_message)

        with open(self.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(test_message, content)
        self.assertIn("INFO", content)

    def test_log_error_message(self):
        """Test that ERROR messages are written to the log file"""
        test_message = "This is an error log test"
        try:
            raise ValueError("Fake error")
        except ValueError as e:
            self.logger.error(test_message, exc_info=e)

        with open(self.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(test_message, content)
        self.assertIn("ERROR", content)
        self.assertIn("ValueError", content)

    def test_setup_logging_creates_file(self):
        """Test that setup_logging configures the logger and creates a log file in logs/"""
        test_message = "Logger setup test"

        # Call your real setup_logging
        app_logger = setup_logging()
        app_logger.info(test_message)

        # Logs directory should exist
        expected_dir = os.path.join(os.getcwd(), "logs")
        self.assertTrue(os.path.isdir(expected_dir))

        # Find the latest app_*.log file
        log_files = [f for f in os.listdir(expected_dir) if f.startswith("app_") and f.endswith(".log")]
        self.assertGreater(len(log_files), 0, "No log files were created in logs/")

        latest_log = max(
            (os.path.join(expected_dir, f) for f in log_files),
            key=os.path.getctime
        )

        # Ensure our test message was written
        with open(latest_log, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(test_message, content)
        self.assertIn("INFO", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
