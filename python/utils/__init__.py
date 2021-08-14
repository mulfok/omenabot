__all__ = (
	'DoubleIO',
	"BufferIO",
)

from types import TracebackType

from . import misc

from typing import io, Iterable, AnyStr, Optional, Type, Iterator


class DoubleIO(io.TextIO):

	def __init__(self, one, other=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.one: io.IO = one
		self.other: io.IO = other
		self.doub = True
		self.orig = True

	def writable(self) -> bool:
		return self.one.writable() and self.orig or self.other.writable() and self.doub

	def write(self, s):
		res = False
		if self.one and self.orig:
			res = self.one.write(s)
		if self.other and self.doub:
			res = max(self.other.write(s), res)
		return res

	def readable(self) -> bool:
		return self.orig and self.one.readable() or self.doub and self.other.readable() or None

	def read(self, *args, **kwargs):
		return self.orig and self.one.read(*args, **kwargs) or self.doub and self.other.read(*args, **kwargs) or None

	def double(self, doub=True, *, orig=True):
		self.doub = doub
		self.orig = orig

	def getvalue(self):
		return self.orig and self.one.getvalue() or self.doub and self.other.getvalue() or None

	def setvalue(self):
		return self.orig and self.one.setvalue() or self.doub and self.other.setvalue() or None

class BufferIO(io.TextIO):
	buffer: str = ""
	cur: int = 0

	def __next__(self) -> AnyStr:
		pass

	def __iter__(self) -> Iterator[AnyStr]:
		pass

	def __exit__(self, t: Optional[Type[BaseException]], value: Optional[BaseException],
	             traceback: Optional[TracebackType]) -> Optional[bool]:
		pass

	def setvalue(self, s):
		self.buffer = s

	def getvalue(self):
		return self.buffer

	def fileno(self) -> int:
		pass

	def flush(self) -> None:
		pass

	def isatty(self) -> bool:
		pass

	def read(self, n: int = ...) -> AnyStr:
		pass

	def readline(self, limit: int = ...) -> AnyStr:
		pass

	def readlines(self, hint: int = ...) -> list[AnyStr]:
		pass

	def seek(self, offset: int, whence: int = ...) -> int:
		pass

	def seekable(self) -> bool:
		pass

	def tell(self) -> int:
		pass

	def truncate(self, size: Optional[int] = ...) -> int:
		pass

	def write(self, s) -> int:
		self.buffer += s
		return len(s)

	def writelines(self, lines: Iterable[AnyStr]) -> None:
		pass

	def close(self) -> None:
		pass

	def readable(self) -> bool:
		return True

	def writable(self) -> bool:
		return True
