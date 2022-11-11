from ds_ordered import Ordered

def __main ():
	f = Ordered[str]()
	f.insert('haha')
	f.insert('wow!!!')

	l = f.to_list()
	print(l)


	s = f.search('haha').item
	print(s)


if __name__ == '__main__':
	__main()
