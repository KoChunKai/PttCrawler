# coding=UTF-8
import telnetlib
import sys
import time
import io
import operator

tn = telnetlib.Telnet('ptt.cc')
f = open('data.txt', 'a')
data = []
userIP = {}
class Ptt:

	def __init__(self, account, password):
		self.account = account
		self.password = password

	def getContent(self):
		time.sleep(2)
		return tn.read_very_eager().decode('big5','ignore')

	def login(self):
		print(u'登入中...')
		content = self.getContent()
		if u'請輸入代號' in content:
			tn.write((self.account+"\r\n").encode('big5'))
			content = self.getContent()
			tn.write((self.password+"\r\n").encode('big5'))
			content = self.getContent()
			self.anykey(content)
			print(u'登入成功')

	def anykey(self, content):
		if u'任意鍵' in content:
			tn.write("\r\n".encode('big5') )

	def checkPage(self, content):
		#print(content)
		if u'文章網址:' in content:
			#print("有在文章網址")
			self.paser(content)
			#return content
		else:
			#print("沒有在文章網址")
			self.changePage()
			self.checkPage(self.getContent())

	def goBoard(self, BoardName):
		tn.write("s".encode('big5'))
		tn.write(BoardName.encode('big5'))
		tn.write("\r\n".encode('big5'))
		time.sleep(1)
		self.anykey(self.getContent())
		time.sleep(1)

	def moveUp(self):
		tn.write(chr(107).encode("ascii"))#k 上篇
		time.sleep(1)

	def moveDown(self):
		tn.write(chr(106).encode("ascii"))#j 下篇
		time.sleep(1)

	def changePage(self):
		tn.write("\x06".encode("ascii"))#^f 下一頁
		time.sleep(1)

	def exitPage(self):
		tn.write(chr(113).encode("ascii"))#q 離開
		time.sleep(1)

	def read(self):
		tn.write(chr(114).encode("ascii"))#r 閱讀
		time.sleep(2)

	def paser(self, content):
		buf = io.StringIO(content)
		lastline = None
		for line in buf.readlines():
			lastline = line = line.strip()
			line = line.split(':')[0]
			if u'噓 ' in line or u'推 ' in line or u'→' in line:
				line = self.replaceASCII(line)
				if line not in data:
					data.append(line)
					print(line)
		if u'100%' not in lastline:
			#print("還沒100%")
			self.changePage()
			self.paser(self.getContent())
		else:
			self.exitPage()

	def replaceASCII(self, strdata):
		try:
			#print(strdata)
			x = strdata.encode("big5")
			x = x.split(b'33m')[1]
			x = x.split(b'\x1b[')[0]
			#print(x)
			return x.decode("utf-8")
		except UnicodeEncodeError:
			print("UnicodeEncodeError:"+strdata)
			return ""
		except IndexError:
			print("IndexError:"+strdata)
			return ""
		except UnicodeDecodeError:
			print("UnicodeDecodeError:"+strdata)
			return ""

	def goUserList(self):
		tn.write("\x15".encode("ascii"))#^u 去用戶列表
		time.sleep(1)

	def searchPage(self):
		tn.write(chr(81).encode("ascii"))#Q 收尋頁面
		time.sleep(1)

	def searchUser(self, Id):
		tn.write(Id.encode('big5'))
		tn.write("\r\n".encode('big5'))
		time.sleep(1)
		self.paserUserIP(Id, self.getContent())

	def paserUserIP(self, Id, content):
		buf = io.StringIO(content)
		for line in buf.readlines():
			if u'《上次故鄉》' in line:
				line = line.split(u'《上次故鄉》')[1]
				u = {Id:line}
				#f.write(Id + ":" + line)
				print(u)
				userIP.update(u);
		self.anykey(content)

p = Ptt("account", "password")
p.login()
p.goBoard("Gossiping")
#tn.write("205537\r\n".encode("big5"))#指定去某篇
tn.write(chr(90).encode("ascii"))#Z 推文數
tn.write("50\r\n".encode("big5"))#20推
for i in range(1, 3, +1):
	print("第"+str(i)+"篇")
	p.read()
	p.checkPage(p.getContent())
	p.moveUp()
p.goUserList()
for x in data:
	p.searchPage()
	p.searchUser(x)

x = sorted(userIP.items(), key=operator.itemgetter(1))
i = -1;
for d in x:
	if i != -1:
		if d[1] == x[i][1]:
			print(d)
			print(x[i])
			f.write(x[i][0] + ":" + x[i][1])
			f.write(d[0] + ":" + d[1])
	i = i + 1