def _pins_side_prop (_attr, _twinattr, _cmp):
	get = lambda self: getattr(self, _attr)
	def set (self, v):
		twin = getattr(self, _twinattr)
		if getattr(v, _cmp)(twin):
			setattr(self, _attr, twin)
			setattr(self, _twinattr, v)
		else:
			setattr(self, _attr, v)
	return property(fget = get, fset = set)


class Pins:
	__slots__ = '_l', '_t', '_r', '_b'
	def __init__ (self, left = None, top = None, right = None, bottom = None):
		l = t = r = b = 0
		if top is None:
			if left is None:
				pass
			elif isinstance(left, Pins):
				l = left._l
				t = left._t
				r = left._r
				b = left._b
			elif isinstance(left, int|float):
				l = t = r = b = float(left)
		elif right is None:
			l = t = left
			r = b = top
		else:
			l = left
			t = top
			r = right
			b = bottom

		self._l: float = l
		self._t: float = t
		self._r: float = r
		self._b: float = b

	left:   float = _pins_side_prop('_l', '_r', '__gt__')
	right:  float = _pins_side_prop('_r', '_l', '__lt__')
	top:    float = _pins_side_prop('_t', '_b', '__gt__')
	bottom: float = _pins_side_prop('_b', '_t', '__lt__')

	@property
	def width (self):
		return self._r - self._l
	
	@property
	def height (self):
		return self._b - self._t

	def __iter__ (self):
		return (getattr(self, k) for k in self.__slots__)

	def __getitem__ (self, i) -> float:
		return getattr(self, self.__slots__[i])

	def __setitem__ (self, i, v: float):
		setattr(self, self.__slots__[i], v)

	def __repr__ (self):
		return f'{self._l}, {self._t}, {self._r}, {self._b}'

	def extend_corners (self, x, y):
		if x < self._l:
			self._l = x
		if y < self._t:
			self._t = y
		if x > self._r:
			self._r = x
		if y > self._b:
			self._b = y

	def __eq__ (self, other):
		if hasattr(other, '__iter__'):
			return all(a == b for a, b in zip(self, other))
		else:
			return all(a == other for a in self)

	@classmethod
	@property
	def INF (cls):
		return cls(float('inf'), float('-inf'))


if __name__ == '__main__':
	bbox = Pins(-10, -20, 30, 40)
	print(bbox)
	bbox2 = Pins(bbox)
	bbox.left = 50
	print(*bbox, bbox2)

	print(Pins.INF)

