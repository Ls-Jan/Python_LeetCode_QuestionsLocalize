import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QLabel,QTextEdit
#高版本PyQt5下没有QWebView：https://blog.51cto.com/zhuxianzhong/4086065
#貌似QWebEngineView这小比崽子挺多bug？https://blog.csdn.net/mrbone11/article/details/121076920
#因为只打算加载静态数据，使用QTextEdit绕坑

if True:
	app = QApplication(sys.argv)

	with open('test.html','rb') as f:
		html=f.read().decode()
		# html=f.read().decode('unicode-escape')

	window = QMainWindow()
	window.show()

	lb = QTextEdit()
	window.setCentralWidget(lb)
	lb.setHtml(html)
	# lb.setText(html)
	font=lb.font()
	font.setPixelSize(20)
	lb.setReadOnly(True)
	lb.setFont(font)

	window.resize(800,600)

	lb.setStyleSheet('color:#DDDDDD ;background:#282828')

	sys.exit(app.exec_())




