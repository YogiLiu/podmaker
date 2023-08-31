import unittest
from unittest import mock

from podmaker.util import retry


class TestRetry(unittest.TestCase):
    def test_no_exception(self) -> None:
        spy = mock.Mock(return_value=1)
        func = retry(3)(spy)
        self.assertEqual(1, func())
        self.assertEqual(1, spy.call_count)

    def test_retry_success(self) -> None:
        spy = mock.Mock(side_effect=[Exception, 1])
        func = retry(3)(spy)
        self.assertEqual(1, func())
        self.assertEqual(2, spy.call_count)

    def test_retry_failed(self) -> None:
        spy = mock.Mock(side_effect=Exception)
        func = retry(3)(spy)
        self.assertRaises(Exception, func)
        self.assertEqual(4, spy.call_count)

    def test_specify_exception(self) -> None:
        spy = mock.Mock(side_effect=ValueError)
        func = retry(3, catch=TypeError)(spy)
        self.assertRaises(ValueError, func)
        self.assertEqual(1, spy.call_count)

        spy = mock.Mock(side_effect=ValueError)
        func = retry(3, catch=ValueError)(spy)
        self.assertRaises(ValueError, func)
        self.assertEqual(4, spy.call_count)
