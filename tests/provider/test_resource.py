import multiprocessing
import unittest

from podmaker.rss import Resource
from podmaker.util import ExitSignalError, exit_signal

parent, child = multiprocessing.Pipe()


def exit_signal_tester() -> None:
    class Tester(Resource[None]):
        def get(self) -> None:
            return None

    t = Tester()
    exit_signal.receive()
    try:
        t.get()
    except BaseException as e:
        child.send(e)
    else:
        child.send(None)


class TestResource(unittest.TestCase):
    def test_exit_signal(self) -> None:
        p = multiprocessing.Process(target=exit_signal_tester)
        p.start()
        p.join()
        self.assertIsInstance(parent.recv(), ExitSignalError)
