from collections.abc import Iterator
from typing import Self


def _node_link_prop (*, attr=None, getv=None, setv=None):
	if attr is not None:
		if getv is None:
			getv = lambda self: getattr(self, attr)
		if setv is None:
			setv = lambda self, v: setattr(self, attr, v)
	return property(getv, setv)

def _head_link_prop (a, b):
	def setv (self, node):
		nx = getattr(getattr(self, a), a)
		setattr(node, a, nx)
		setattr(node, b, self)
		setattr(nx, b, node)
		setattr(self, a, node)
	return _node_link_prop(attr=a, setv=setv)


class Node:
	__slots__ = '_prev_node', '_next_node'
	def __init__ (self):
		self._prev_node = self._next_node = self

	prev: Self = _node_link_prop(attr=__slots__[0])
	next: Self = _node_link_prop(attr=__slots__[1])

	start: Self = _head_link_prop('next', 'prev')
	'''
	`.start` and `.end` are for "dummy header nodes". That is, they're the
	start of a doubly linked list, but don't contribute to the list's data.

	This saves you the headache of having to keep track of the first and last
	nodes yourself, as well as checking whether a node's next/prev is `None`
	or not before inserting them into a chain and so on.

	Assigning to `.start` or `.end` is equivelent to `self.set_right(new_start)` and
	`self.set_left(new_end) respectively
	'''

	end: Self = _head_link_prop('prev', 'next')
	'See `.start`'

	def __iter__ (self) -> Iterator[Self]:
		n = self
		while True:
			yield n
			if (n := n.next) is None or n is self:
				break

	def __reversed__ (self) -> Iterator[Self]:
		n = self
		while True:
			yield n
			if (n := n.prev) is None or n is self:
				break

	def __add__ (self, other: Self) -> Self:
		"""
		`(self + other) == other`

		The new chain is `... - self - other - next - ...`
		"""
		other.prev = self
		other.next = self.next
		self.next.prev = other
		self.next      = other
		return other

	def __pos__ (self) -> Iterator[Self]:
		"""
		A forwards-marching head iterator, IE in the chain:
		`a - b - c`, `for n in +a:` will yield `b, c`, but not `a`
		"""
		n = self
		while not (((n:=n.next) is None) or (n is self)):
			yield n

	def __neg__ (self) -> Iterator[Self]:
		"""
		The same as `+a`, except in reverse; in the chain `a - b - c` you
		will get `c, b` but not `a`
		"""
		n = self
		while not (((n:=n.prev) is None) or (n is self)):
			yield n


	def set_left (self, node: Self) -> Self:
		'''
		changes the chain `... - ... - self` to `... - node - self` and returns
		the node that was replaced
		'''
		old = self.prev

		node.prev = old.prev
		node.next = self
		old.prev.next = node
		self.prev = node
		return old

	def set_right (self, node: Self) -> Self:
		'''
		same as `.set_left`, but for with the chain `self - ... - ...` to
		`self - node - ...`
		'''
		old = self.next

		node.next = old.next
		node.prev = self
		old.next.prev = node
		self.next = node
		return old

	def insert_left (self, node: Self) -> Self:
		'''
		...prev - +node+ - self - next...
		'''
		node.next = self
		node.prev = self.prev
		self.prev.next = node
		self.prev = node
		return node

	def insert_right (self, node: Self) -> Self:
		'''
		...prev - self - +node+ - next...
		'''
		node.prev = self
		node.next = self.next
		self.next.prev = node
		self.next = node
		return node

	def remove_from_chain (self, clear_self = False):
		'''
		(...prev - self - next...) becomes (...prev - next...)
		'''
		self.prev.next = self.next
		self.next.prev = self.prev
		if clear_self:
			self.next = self.prev = self

	def replace_in_chain (self, other: Self, clear_self = False):
		"""
		Replaces the node `self` with `other`.

		IE, `abc` and `d`, `b.replace(d)` creates `adb`
		"""
		l = other.prev = self.prev
		r = other.next = self.next

		l.next = other
		r.prev = other

		if clear_self:
			self.next = self.prev = self

	def chain_length (self, head = False) -> int:
		return sum(1 for _ in (+self if head else self))


	def splice_start_start (a, d: Self) -> Self:
		'''
		`abc`, `def`: given `a, d`, creates `abcdef`
		'''
		c = a.prev
		f = d.prev

		c.next, f.next = d, a
		a.prev, d.prev = f, c

		return a

	def splice_start_end (a, f: Self) -> Self:
		'''
		`abc`, `def`: given `a, f`, creates `abcdef`
		'''
		d = f.next
		c = a.prev
		
		c.next, f.next = d, a
		a.prev, d.prev = f, c

		return a

	def splice_end_start (c, d: Self) -> Self:
		'''
		`abc`, `def`: given `c, d`, creates `abcdef`
		'''
		a = c.next
		f = d.prev

		c.next, f.next = d, a
		a.prev, d.prev = f, c

		return f

	def splice_end_end (c, f: Self) -> Self:
		'''
		`abc`, `def`: given `c, f`, creates `abcdef`
		'''
		a = c.next
		d = f.next

		c.next, f.next = d, a
		a.prev, d.prev = f, c
		return f


	def walk (self,
	          start = None,
	          step  = None,
	          stop  = None,
	          chain_safe = False) -> Iterator[Self]:
		"""
		`start`: If omitted, is set to `self` by default. if set to `...`,
		`start` will be set to whatever the next node in the chain should be,
		IE `.next`.

		`chain_safe`: Will assure whatever the next node was at the time
		the loop started stays that way.
		
		IE if you change the chain and the `.next` property is altered, whatever
		`node` had at the start of the loop as its `.next` will be the next node.

		The loop will stop once `stop` has been reached/satisfied, or if `step(node)`
		results in `None` for some reason.
		"""

		if step is None:
			step = 'next'
		if isinstance(step, str):
			get_next = lambda n: getattr(n, step)
		elif isinstance(step, property):
			get_next = lambda n: step.fget(n)
		elif callable(step):
			get_next = step
		
		if start is None:
			start = self
		elif start is ...:
			start = get_next(self)

		if stop is None:
			is_end = lambda n: n is self
		elif isinstance(stop, str):
			is_end = lambda n: n is getattr(self, stop)
		elif isinstance(stop, property):
			is_end = lambda n: n is stop.fget(self)
		elif callable(stop):
			is_end = stop

		node = start
		if chain_safe:
			node_next = node
			while True:
				node_next = get_next(node)
				yield node
				node = node_next
				if node is None or is_end(node):
					break
		else:
			while True:
				yield node
				if (node:=get_next(node)) is None or is_end(node):
					break


