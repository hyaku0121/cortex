import unittest
from unittest.mock import patch, mock_open
import sys
import os
from datetime import datetime, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cortex.notify import NotificationManager, notify_cli

class TestNotify(unittest.TestCase):
    def setUp(self): self.m = NotificationManager()
    @patch("cortex.notify.CONFIG_FILE")
    @patch("builtins.open", new_callable=mock_open, read_data='{"enabled": true}')
    def test_load(self, mf, mp):
        mp.exists.return_value = True
        self.assertTrue(self.m._load_config().enabled)
    @patch("cortex.notify.datetime")
    def test_dnd(self, m_dt):
        m_dt.now.return_value.time.return_value = time(23, 0)
        m_dt.strptime = datetime.strptime
        self.m.config.dnd_start = "22:00"; self.m.config.dnd_end = "08:00"
        self.assertTrue(self.m._is_dnd_active())
    @patch("shutil.which")
    def test_send_console(self, m_which):
        m_which.return_value = None
        with patch.object(self.m, '_is_dnd_active', return_value=False):
            self.assertTrue(self.m.send("T", "M"))

if __name__ == '__main__': unittest.main()
