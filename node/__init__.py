from dxd_node import Node


def _main ():
	class TNode(Node):
		def __init__ (self, value: str = ''):
			super().__init__()
			self.value = value
		def __str__ (self):
			return self.value

	head = TNode('0   head')
	end = head + TNode('1 A Haha') + TNode('2 B Wow!!!') + TNode('3 C 292202')
	end = end + TNode('4 D') + TNode('5 E')

	end = Node.splice_end_end(TNode('6 F') + TNode('7 G'), end)
	print(end, '\n')

	for n in head:
		print(n)

if __name__ == '__main__':
	_main()
