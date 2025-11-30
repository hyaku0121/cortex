import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cortex.cleanup import CleanupEngine, cleanup_cli

class TestCleanup(unittest.TestCase):
    def setUp(self): self.engine = CleanupEngine()
    def test_scan(self):
        self.engine.scan()
        self.assertTrue(len(self.engine.items) > 0)
    def test_exec(self):
        with patch('rich.console.Console.print'):
            self.engine.scan()
            freed = self.engine.execute_cleanup(dry_run=True)
            self.assertTrue(freed > 0)
    @patch('cortex.cleanup.CleanupEngine')
    @patch('rich.console.Console.print')
    def test_cli(self, m_p, m_cls):
        m_cls.return_value.items = []
        cleanup_cli(dry_run=True)
        m_p.assert_called()

if __name__ == '__main__': unittest.main()
