'''
Unit test for app.py
'''
import unittest
import app


class TestApp:
    def test_code(self):
        assert 20000 == app.min_cases


if __name__ == '__main__':
    unittest.main()
