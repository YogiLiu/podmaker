import signal
import threading
from typing import Any, Callable

_exit_signals = (
    signal.SIGINT,
    signal.SIGHUP,
    signal.SIGTERM,
)

_lock = threading.Lock()


class ExitSignalError(Exception):
    pass


class ExitSignalRegisterError(Exception):
    pass


class ExitSignal:
    def __init__(self) -> None:
        self._is_received = False
        self._has_listened = False
        self._exit_handlers: list[Callable[[], None]] = []

    def receive(self) -> None:
        with _lock:
            self._is_received = True

    def check(self) -> None:
        with _lock:
            if self._is_received:
                raise ExitSignalError('exit signal received')

    def register(self, handler: Callable[[], None]) -> None:
        with _lock:
            if self._has_listened:
                raise ExitSignalRegisterError('already listened')
            self._exit_handlers.append(handler)

    def _handler(self, *_: Any) -> None:
        self.receive()
        for handler in self._exit_handlers:
            handler()

    def listen(self) -> None:
        with _lock:
            self._has_listened = True
            for sig in _exit_signals:
                signal.signal(sig, self._handler)


exit_signal = ExitSignal()
