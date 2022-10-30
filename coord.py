from math import sqrt
from typing import Self


class CoordBase:
	ALT_NAMES = ''
	def __init__ (self):
		for k in self.__slots__:
			setattr(self, k, 0.0)

	def _combr_init (self, other) -> bool:
		if hasattr(other, '__iter__'):
			for k, j in zip(self.__slots__, other):
				setattr(self, k, j)
			return True
		return False

	def _coname (self):
		return ', '.join(str(k) for k in self)

	def __getitem__ (self, i) -> float:
		return getattr(self, self.__slots__[i])
	def __setitem__ (self, i, v):
		setattr(self, self.__slots__[i], v)
	
	def __eq__ (a, b):
		if hasattr(b, '__iter__'):
			return all(i == j for i, j in zip(a, b))
		else:
			return all(i == b for i in a)
	
	def __neg__ (self):
		return self.__class__(-v for v in self)

	def __iter__ (self):
		return (float(getattr(self, k)) for k in self.__slots__)

	def dist_l1 (self, other) -> float:
		return sum(abs(i-j) for i, j in zip(self, other))

	def length_squared (self) -> float:
		return sum(k ** 2 for k in self)

	def length (self) -> float:
		return sqrt(self.length_squared())

	def _inv_mag (self) -> float:
		mag = self.length_squared()
		if mag == 0.0:
			return 0.0
		return 1.0 / sqrt(mag)

	def normalize (self):
		'Normalizes the coord in-place'
		mag = self._inv_mag()
		self.set(k * mag for k in self)

	@property
	def normalized (self):
		mag = self._inv_mag()
		return self.__class__(k * mag for k in self)

	def dot (self, other) -> float:
		return sum(a * b for a, b in zip(self, other))

	def set (self, other):
		if self._combr_init(other):
			pass
		elif isinstance(other, float|int):
			self.x = self.y = self.z = float(other)
		elif other is None:
			self.x = self.y = self.z = 0.0
		return self

	@classmethod
	@property
	def ZERO (cls) -> Self:
		return cls(0.0)

	@classmethod
	@property
	def ONE (cls) -> Self:
		return cls(1.0)


class Co2 (CoordBase):
	__slots__ = 'x', 'y'
	ALT_NAMES = 'st', 'uv'
	def __init__ (self, x = None, y = None):
		super().__init__()
		if x is None:
			return
		if y is None:
			self.set(x)
			return
		self.x = float(x)
		self.y = float(y)

	def __le__ (a, b):
		return (a.x < b.x) or (a.x == b.x and a.y <= b.y)

	def __repr__ (self):
		return f'{__class__.__name__}({self._coname()})'

	@property
	def yx (self):
		'This should be replaced with proper swizzling'
		return Co2(self.y, self.x)


class Co3 (CoordBase):
	__slots__ = 'x', 'y', 'z'
	ALT_NAMES = 'stp', 'uvw'
	def __init__ (self, x = None, y = None, z = None):
		super().__init__()
		if x is None:
			return

		if y is None:
			self.set(x)
			return

		if z is None:
			z = 0.0

		self.x = float(x)
		self.y = float(y)
		self.z = float(z)

	def __repr__ (self):
		return f'{__class__.__name__}({self._coname()})'

	def cross (d1, d2: Self):
		return Co3(d1.y*d2.z - d1.z*d2.y,
		           d1.z*d2.x - d1.x*d2.z,
		           d1.x*d2.y - d1.y*d2.x)


if __name__ == '__main__':
	c1 = Co2(1, 1).normalized
	c2 = Co2(1, 1)
	c2.normalize()
	print(c1.dot(c2))

	c3 = Co3(c1)
	print(c3, Co3(c3))

	print(Co2(c3))

	print(Co2(1.0))
	print(Co3((10, 20, 30, 40)) == (10, 20, 30))
	print(Co3((10, 20, 30, 40)) == (10, 210, 30))
	print(Co3((10, 20, 30, 40)) == (10, 20, 30, 999))
	print(Co2.ZERO, Co2.ONE)
	print(Co3.ZERO, Co3.ONE)
