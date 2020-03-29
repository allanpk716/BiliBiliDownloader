# -*- coding: utf-8 -*-
'''作者：mcfx
链接：https://www.zhihu.com/question/381784377/answer/1099438784
来源：知乎
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
'''
class ABV:
	def __init__(self):
		super().__init__()
		self.table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
		self.tr={}
		for index in range(58):
			self.tr[self.table[index]]=index
		self.s=[11,10,3,8,4,6]
		self.xor=177451812
		self.add=8728348608
	# B2A
	def dec(self, x):
		r = 0
		for index in range(6):
			r+=self.tr[x[self.s[index]]]*58**index
		return (r-self.add)^self.xor
	# A2B
	def enc(self, x):
		x = (x^self.xor) + self.add
		r=list('BV1  4 1 7  ')
		for index in range(6):
			r[self.s[index]]=self.table[x//58**index%58]
		return ''.join(r)