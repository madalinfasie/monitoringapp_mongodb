import typing as t
from dataclasses import dataclass, field


@dataclass
class Metric:
    name: str
    train_interval: t.Dict[str, int] = field(default_factory=lambda: {'days': 7})
    train_params: t.Optional[t.Dict[str, t.Any]] = None

    labels: t.Optional[t.Dict[str, str]] = None
