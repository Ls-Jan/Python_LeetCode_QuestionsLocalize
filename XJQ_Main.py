

#requests使用：https://zhuanlan.zhihu.com/p/140372568
#LeetCode题库爬取：https://www.cnblogs.com/ZhaoxiCheung/p/9333476.html

import requests
import json
import os
import re
from XJ_LeetCode import XJ_LeetCode
from bs4 import BeautifulSoup





	def Get_QuestionsList(self,
					   start:int=-1,
					   count:int=-1,
					   onlyCount:bool=False,
					   *,
					   keywords:list=[],
					   tags:list=[],
					   difficulty:str=None,
					   finish:bool=None,
					   favorite:bool=None,
					   accessible:bool=None):
		'''
			读取题目列表，传入conditions以指定筛选项(筛选项是AND连接)。
			返回[{'questionSlug':XXX,...,'hasContent':True,'hasCode':True},...]

			指定筛选项：
				keywords:题目搜索，支持模糊搜索
				tags:题目标签，支持多标签
				difficulty:题目难易度(可选值为“简单”、“中等”、“困难”)
				finish:题目完成标记
				accessable:仅显示可用的题目
		'''
		tableLst='list'
		tableQuestion='question'
		conditions=[]
		if(keywords):
			conditions.append(' OR '.join([f'INSTR({tableLst}.title,{key})' for key in keywords]))
		if(tags):
			conditions.append(' OR '.join([f'INSTR({tableLst}.tags,{tag})' for tag in tags]))
		if(difficulty!=None):
			conditions.append(f'INSTR({tableLst}.difficulty,{difficulty})')
		if(accessible!=None):
			conditions.append(f'{tableLst}.invisible=={str(not accessible)}')
		colsOrigin=self.__config.tables[tableLst]
		colsRename=[f'{tableLst}.{col}' for col in colsOrigin]
		colsExtra=[f'has{key.capitalize()}' for key in self.__config.tables[tableQuestion][1:]]




		lst=self.__sql.Get_RowsData(tableLst,*conditions,
							  conditionsLink='AND',
							  cols=colsRename+colsExtra,
							  joinTableName='temp',
							  onlyCount=onlyCount,
							  leftJoinCondition=f'{tableQuestion}.{colsOrigin[0]}=={tableLst}.{colsOrigin[0]}')
		if(count<0):
			count=len(lst)
		rst=[]
		for row in lst[start:start+count]:
			row=self.__TransRowData(colsOrigin+colsExtra,row)
			row['tags']=eval(row['tags'])
			rst.append(row)
		return rst

class XJQ_Main(QMainWindow):
	def __init__(self):
		self.__sider=XJQ_ListView()
		self.__sider
		Get_WidList
		spt=QSplitter(Qt.Horizontal)
		spt.addWidget(self.__sider)
		
		self.setCentralWidget(spt)


if __name__=='__main__':
	app = QApplication(sys.argv)

	sys.exit(app.exec_())
