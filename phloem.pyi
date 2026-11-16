# Types for the `phloem` package: what editors and type checkers see.

from os import PathLike
from types import TracebackType
from typing import List, Literal, Mapping, Optional, Sequence, Tuple, Type, TypedDict, Union

from typing_extensions import NotRequired

__version__: str

Route = Literal["local", "direct"]

TimeBasis = str
"""`"source"` (the device's own clock), `"host"` (this machine's clock) or
`"backdated:<anchor_us>"` (a recording whose first instant is `anchor_us`)."""

Scalar = Union[float, int, bool, str]
"""One reading. A `str` is allowed in `log_now`, `log` and `explicit` only."""

class ChannelDeclaration(TypedDict):
    path: str
    archetype: NotRequired[str]
    unit: NotRequired[str]

class CodeColumn(TypedDict, total=False):
    """A converter's raw codes, read as `code * scale + offset`. Exactly one of
    `i16` or `i32`; `None` in the list is a missing reading."""

    i16: List[Optional[int]]
    i32: List[Optional[int]]
    scale: float
    offset: float

Column = Union[
    List[float],
    List[int],
    List[bool],
    List[Optional[float]],
    List[Optional[int]],
    List[Optional[bool]],
    CodeColumn,
]
"""One channel's values in a uniform frame: a list, all the same type; `None`
is a missing reading."""

Columns = Mapping[str, Column]
"""path -> column; at run time a `dict`."""
Sample = Tuple[str, Optional[int], Scalar]
"""`(path, t_ns, value)`; `t_ns=None` places the value at the frame's time."""

class UnsentError(RuntimeError):
    """Data the cloud never confirmed (the direct route). Raised by `close()`,
    and by a `with` block that finished, when anything sent was not
    acknowledged. Its message says how much and why."""

class UniformStream:
    """A fixed-rate sender that cannot step backwards: anchored once, every
    frame placed where the last one ended. Made by `Client.stream(...)` or
    `FrameWriter.stream(...)`."""

    def push(self, columns: Columns, now_ns: Optional[int] = None) -> int:
        """Write the next frame and return its first instant (ns)."""
    @property
    def next_t0_ns(self) -> Optional[int]:
        """Where the next frame starts; `None` before a host stream's first push."""
    @property
    def reanchors(self) -> int:
        """Times the stream fell behind the host clock past its tolerance and
        was re-anchored forward, each skipped span stated as a gap."""

class Client:
    """A program's connection to Phloem: to the daemon on this machine, or
    straight to the cloud with an API key. `phloem.connect(...)` makes one."""

    def __init__(
        self,
        producer: str,
        path: Optional[Union[str, PathLike[str]]] = None,
        clock_id: Optional[str] = None,
        *,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        route: Optional[Route] = None,
        buffer_bytes: Optional[int] = None,
        drop_when_full: bool = False,
        close_timeout_s: Optional[float] = None,
    ) -> None: ...
    @property
    def route(self) -> Route:
        """Which way the data goes."""
    @property
    def permit(self) -> str:
        """The input this connection publishes under."""
    def log_now(self, path: str, value: Scalar) -> None:
        """One reading, stamped with this machine's clock as the call is made."""
    def log(self, path: str, t_ns: int, time_basis: TimeBasis, value: Scalar) -> None:
        """One reading at its own instant, on the stated time basis."""
    def log_many(
        self,
        path: str,
        time_basis: TimeBasis,
        times_ns: Sequence[int],
        values: Sequence[float],
    ) -> None:
        """Many readings of one channel; `times_ns` and `values` are the same length."""
    def declare(self, channels: List[ChannelDeclaration]) -> None: ...
    def uniform(
        self,
        t0_ns: int,
        time_basis: TimeBasis,
        columns: Columns,
        step_hz: Optional[float] = None,
        step_ns: Optional[int] = None,
    ) -> None:
        """A fixed-rate frame starting at `t0_ns`. Give one of `step_hz` or `step_ns`."""
    def explicit(self, time_basis: TimeBasis, samples: List[Sample]) -> None:
        """A frame of readings each at its own instant."""
    def gap(
        self,
        paths: Sequence[str],
        frontier_ns: int,
        detail: str,
        at_least_samples: Optional[int] = None,
    ) -> None:
        """State a hole on `paths` whose good data stopped at `frontier_ns`."""
    def stream(
        self,
        channels: Sequence[str],
        time_basis: TimeBasis,
        step_hz: Optional[float] = None,
        step_ns: Optional[int] = None,
        anchor_ns: Optional[int] = None,
        drift_tolerance_ns: Optional[int] = None,
    ) -> UniformStream: ...
    def flush(self) -> None: ...
    def close(self) -> None:
        """End the stream, flush and close. On the direct route this waits for
        the cloud and raises `UnsentError` when anything was not confirmed."""
    def __enter__(self) -> "Client": ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        _exc: Optional[BaseException] = None,
        _tb: Optional[TracebackType] = None,
    ) -> None: ...

class FrameWriter:
    """The encoder alone, writing to memory. Same methods as `Client`;
    `bytes()` returns what was written."""

    def __init__(self) -> None: ...
    def hello(self, producer: str, sdk: str, clock_id: Optional[str] = None) -> None: ...
    def declare(self, channels: List[ChannelDeclaration]) -> None: ...
    def uniform(
        self,
        t0_ns: int,
        time_basis: TimeBasis,
        columns: Columns,
        step_hz: Optional[float] = None,
        step_ns: Optional[int] = None,
    ) -> None: ...
    def explicit(self, time_basis: TimeBasis, samples: List[Sample]) -> None: ...
    def gap(
        self,
        paths: Sequence[str],
        frontier_ns: int,
        detail: str,
        at_least_samples: Optional[int] = None,
    ) -> None: ...
    def stream(
        self,
        channels: Sequence[str],
        time_basis: TimeBasis,
        step_hz: Optional[float] = None,
        step_ns: Optional[int] = None,
        anchor_ns: Optional[int] = None,
        drift_tolerance_ns: Optional[int] = None,
    ) -> UniformStream: ...
    def end(self) -> None: ...
    def bytes(self) -> bytes: ...

def connect(
    name: str,
    *,
    api_key: Optional[str] = None,
    url: Optional[str] = None,
    route: Optional[Route] = None,
    path: Optional[Union[str, PathLike[str]]] = None,
    clock_id: Optional[str] = None,
    buffer_bytes: Optional[int] = None,
    drop_when_full: bool = False,
    close_timeout_s: Optional[float] = None,
) -> Client:
    """Open a client. With an API key (`api_key=` or `PHLOEM_API_KEY`) and its
    workspace URL (`url=` or `PHLOEM_URL`) the data goes straight to the cloud
    as the program `name`; with none it goes to the Phloem on this machine."""

def default_socket_path() -> str:
    """Where the local daemon's SDK door is, by the daemon's own rule."""
