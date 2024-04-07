
import sys
from PyQt5.QtWidgets import QApplication,QTableWidget,QHeaderView,QSizePolicy,QAbstractItemView,QMainWindow,QSplitter
from PyQt5.QtCore import QPoint,Qt

from XJ.Widgets.XJQ_ListWidget import XJQ_ListWidget
from XJ.Widgets.XJQ_ListWidgetItem import XJQ_ListWidgetItem
from XJ.Widgets.XJQ_PageNavigation import XJQ_PageNavigation
from XJ.Widgets.XJQ_PureColorIcon import XJQ_PureColorIcon

import sys
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout
from XJ_LeetCode import Manager

class XJQ_QuestionList(QWidget):
	config={
		'icons':{
			'favorite':XJQ_PureColorIcon('./Icons/收藏.png',size=(24,24),fg=(255,0,255,192)),
			'finish':XJQ_PureColorIcon('./Icons/对勾.png',size=(24,24),fg=(0,255,0,192)),
			'hasCache':XJQ_PureColorIcon('./Icons/文件袋.png',size=(24,24),fg=(0,255,255,192)),
			'questionDownload':XJQ_PureColorIcon('./Icons/云下载.png',size=(40,40),fg=(255,255,0,192)),
			'questionError':XJQ_PureColorIcon('./Icons/云错误.png',size=(40,40),fg=(255,0,0,192)),
		},
		'difficultyColor':{
			'easy':'rgba(255,160,0,128)',
			'normal':'rgba(255,0,0,128)',
			'hard':'rgba(0,0,255,128)',
		}
	}
	def __init__(self,sqlPath:str='./data',imgPath:str='./data/img'):
		'''
			sqlPath为数据库路径，
			imgPath为图片缓存路径
		'''
		super().__init__()
		lc=Manager(sqlPath,imgPath)
		lv=XJQ_ListWidget()
		pn=XJQ_PageNavigation()

		pn.Set_PerCountList([10,20,30,40,50,60,70,80,90,100])
		pn.changed.connect(lambda start,count:print(start,start+count-1))
		lv.currentRowChanged.connect(lambda row:print(row,lv.currentIndex()))

		# pn.resize(250,50)
		pn.setStyleSheet('''
			color:#FF0000;
			background:#222222;
			margin:0;
		''')

		self.__lc=lc
		self.__lv=lv
		self.__pn=pn
		self.config={key:item.copy() for key,item in self.config.items()}
		self.__filters={
			'keywords':[],#题目搜索，支持模糊搜索
			'tags':[],#题目标签，支持多标签
			'difficulty':None,#题目难易度
			'finish':None,#题目完成标记
			'accessable':None,#仅显示可用的题目
		}
	def UpdateList(self):
		self.__lc.Update_QuestionsList()
	def ChangeTotal(self):
	def Set_Filter(self,keywords:list=[]):
		'''
			设置筛选器
		'''
		
		rst=__lc.Get_QuestionsList(start,count,)
		self.__lc.Get_QuestionsCount()

	@staticmethod
	def __TransFilterLst(filters:dict):
		'''
			将筛选项转化为筛选列表以便塞进XJ_LeetCode.Get_QuestionsList里头
		'''
		filters={
			'keywords':[],#题目搜索，支持模糊搜索
			'tags':[],#题目标签，支持多标签
			'difficulty':None,#题目难易度
			'finish':None,#题目完成标记
			'accessable':None,#仅显示可用的题目
		}		
		sss='INSTR(tags,"哈希")'
		


if __name__=='__main__':
	lst=[
		'detect-capital',
		# 'minimum-time-to-make-array-sum-at-most-x',
		'missing-ranges',
		'add-two-numbers',
	]
	print("START")
	# print(lc.Get_QuestionCount())
	# exit()
	# print(lc.KKK())
	# exit()
	start,count=0,100
	# rst=lc.Get_QuestionsList(start,count)
	rst=lc.Get_QuestionsList(start,count,'INSTR(tags,"哈希")')
	rst=lc.Get_CacheSet(False,True)
	# rst=lc.Get_CacheSet(True,False)
	# rst=lc.Get_QuestionsList(start,count,'id="3"','INSTR(tags,"哈希")')
	# rst=lc.Get_QuestionsList(start,count,'id="3"','id="4"')
	# rst=lc.Get_QuestionsList(start,count,'INSTR(title,"多")','INSTR(tags,"哈希")','difficulty="简单"')


	# for item in rst:
	# 	print(item)
	# print('\n\n')

	rst=lc.Get_QuestionCode(lst[-1],loadFromDB=False)
	for lang in rst:
		print(lang)
		print(rst[lang])
		print()

	exit()

	# cont=lc.Get_QuestionContent(lst[-1])
	cont=lc.Get_QuestionContent(lst[-1],loadFromDB=False)
	# with open('test2.html','w',encoding='utf-8') as f:
		# f.write(cont)
	soup = BeautifulSoup(cont,'html.parser')
	print(soup)
	print('\n\n')
	exit()

	# rst=lc.Get_QuestionCode(lst[-1])
	rst=lc.Get_QuestionCode(lst[-1],loadFromDB=False)
	for lang in rst:
		print(lang)
		print(rst[lang])
		print()
	print('\n\n')


	def __SetRange(self,start:int,count:int):
		pn.Set_DataCount(2936)
	def __Set
	def 
	def Set_CurrentPage(self,page:int,index:int=None):
		'''
			设置当前页。如果指定index那么将跳转到对应数据所在页
		'''
		self.__pn.Set_CurrPage(page,index)
	def __Set_ListItemInfo(self,row:int,question:str,name_diffculty:str,tags:list,name_extra:list):
		'''
			设置指定单元格的信息，
			设置的属性分别是题目名、难度(名称)、标签列表、图标(名称)
		'''
		item=self.__lv.indexWidget(self.__lv.model().index(row,0))
		item.Opt_Change(title=question,tags=tags,itemColor=self.config[name_diffculty],extraIcons=[self.config['icons'][name] for name in name_extra])
	def __Set_ListLength(self,count:int):
		'''
			调整列表长度
		'''
		diff=self.__lv.count()-count
		while(diff>0):#列表过长
			self.__lv.Opt_RemoveRow(0)
			diff-=1
		while(diff<0):#列表过短
			item=XJQ_ListWidgetItem('')
			self.__lv.Opt_AppendWidget(item)
			diff+=1





