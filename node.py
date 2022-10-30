from typing import Self

def node_link_prop (*, attr=None, getv=None, setv=None):
	if attr is not None:
		if getv is None:
			getv = lambda self: getattr(self, attr)
		if setv is None:
			setv = lambda self, v: setattr(self, attr, v)
	return property(getv, setv)

def _attr_or_call (thing, default, attr):
	if thing is None:
		return default
	if isinstance(thing, str):
		return attr
	elif callable(thing):
		return thing


class Node:
	__slots__ = '_pr', '_nx'
	def __init__ (self):
		self._pr = self._nx = self

	prev: Self = node_link_prop(attr='_pr')
	next: Self = node_link_prop(attr='_nx')

	def insert_before (self, node: Self):
		'''
		...prev - +node+ - self - next...
		'''
		node.next = self
		node.prev = self.prev
		self.prev.next = node
		self.prev = node
		return node

	def insert_after (self, node: Self):
		'''
		...prev - self - +node+ - next...
		'''
		node.prev = self
		node.next = self.next
		self.next.prev = node
		self.next = node
		return node

	def delete (self):
		'''
		(...prev - self - next...) becomes (...prev - next...)
		'''
		self.prev.next = self.next
		self.next.prev = self.prev
		self.next = self.prev = self

	def __iter__ (self):
		return walk(self)

	def walk (head, key=None, start=None, sentinel=None):
		'''
		if start is passed the same obj as head, or True,
		chain will skip head as the first node
		'''
		nextv = _attr_or_call(
			key,
			lambda self: getattr(self, 'next'),
			lambda self: getattr(self, key),
		)
		
		if (isinstance(start, bool) and start) or (start is head):
			start = nextv(head)
		elif start is None:
			start = head
		
		getend = _attr_or_call(
			sentinel,
			lambda self: (self is None) or (self is head),
			lambda self: (self is None) or (self is getattr(head, sentinel))
		)

		n = start
		while True:
			yield n
			if getend(n:=nextv(n)):
				break

	def chain_length (self) -> int:
		i = 0
		n = self
		while True:
			i += 1
			if (n:=n.next) is None or (n is self):
				return i


def walk (start, as_head = False, *, getv = None):
	if getv is None:
		getv = lambda self: self.next
	elif isinstance(getv, str):
		s = getv
		getv = lambda self: getattr(self, s)

	n = start
	if as_head:
		while ((n := getv(n)) is not start) and (n is not None):
			yield n
	else:
		while True:
			yield n
			if ((n := getv(n)) is start) or (n is None):
				break


def delete (self, prev='prev', next='next'):
	'''
	prev and next are the attribute keys for the respective prev/next nodes.
	defaults to.. well, "prev" and "next". duh.
	TODO: allow prev/next to also be callables for more complex shit
	'''
	nprev = getattr(self, prev)
	nnext = getattr(self, next)

	setattr(nprev, next, nnext)
	setattr(nnext, prev, nprev)


def __main ():
	class TN(Node):
		def __init__ (self, key = 'None'):
			super().__init__()
			self.key: str = key

	a = TN('A haha')
	b = TN('B wow!!!')
	
	a.insert_after(b)
	c = b.insert_after(TN('C'))
	c.insert_after(TN('D'))
	a.insert_before(TN('E'))

	for n in a.walk(sentinel=lambda self: self is c.next):
		print(n.key)


if __name__ == '__main__':
	__main()