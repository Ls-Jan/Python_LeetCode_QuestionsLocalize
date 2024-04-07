
from XJ.Structs.XJ_SQLite import XJ_SQLite
from Config import Config
from threading import Thread


import os
import json

__all__=['Crawler']

class Crawler:
	'''
		用于抓取力扣题库并保存到本地sql中。
	'''
	def __init__(self,sqlPath:str,imgPath:str,*,sqlName:str='LeetCode',config:Config=Config()):
		'''
			sqlPath为数据库路径，
			imgPath为图片缓存路径，
			sqlName为数据库名称，默认是LeetCode，
			config为数据配置，如不指定则采用默认配置。
		'''
		if(not os.path.exists(imgPath)):
			os.makedirs(imgPath)
		if(not os.path.exists(sqlPath)):
			os.makedirs(sqlPath)
		sqlPath=os.path.join(sqlPath,f'{sqlName}.db')
		sqlPath=os.path.realpath(sqlPath)
		if(not os.path.exists(sqlPath)):
			open(sqlPath,'wb').close()
		self.__sql=XJ_SQLite(sqlPath)
		self.__imgPath=imgPath
		self.__config=config
		for table,cols in config.tables.items():
			self.__sql.Opt_CreateTable(table,cols,table=='record')
		self.__sql.Opt_Commit()
		self.__successCall=lambda:print('读取完毕')
		self.__failCall=lambda:print('联网读取失败')
	def Set_Callback(self,successCall=None,failCall=None):
		'''
			设置数据更新时调用的回调函数
		'''
		if(successCall):
			self.__successCall=successCall
		if(failCall):
			self.__failCall=failCall
	def Update_QuestionsList(self,updateCall=lambda count:print(f'当前已读取数据[{count}]'),reload:bool=True):
		'''
			加载题目列表，如果reload为真则从头开始读取，为假时读取剩余部分
		'''
		table='list'
		self.__sql.Opt_CreateTable(table,self.__config.tables[table],reload)
		self.__sql.Opt_Commit()
		start=0 if reload else self.Get_QuestionsCount()
		count=100
		success=True
		while(True):
			lst=self.__config.Get_QuestionList(start,count)
			if(lst==None):
				success=False
				break
			for row in lst:
				self.__sql.Opt_AppendRow(table,row)
			self.__sql.Opt_Commit()
			start+=len(row)
			if(len(row)==count):
				updateCall(start)
			else:
				break
		self.__successCall() if success else self.__failCall()
	def Update_QuestionContent(self,questionSlug:str,forceLoad:bool=False):
		'''
			请求题目内容(字符串)，如果forceLoad为真则直接重新请求一遍数据。
			题目中出现的图片数据将保存到指定的本地路径中。
		'''
		table='question'
		success=True
		lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
		if(not lst):
			self.__sql.Opt_AppendRow(table,[questionSlug,None,None])
			self.__sql.Opt_Commit()
			forceLoad=True
		if(forceLoad):
			rst=self.__config.Get_QuestionContent(questionSlug)
			if(rst):
				cont,imgMap=rst
				imgPath=f'./{self.__imgPath}/{questionSlug}-'
				for i in range(len(imgMap)):#将图片保存为本地，同时将cont中的url图片资源改为本地
					tag,url,img=imgMap[i]
					path=imgPath+os.path.split(url)[1]
					cont=cont.replace(tag,tag.replace(url,path))
					with open(path,'wb') as f:
						f.write(img)
				self.__sql.Set_RowsData(table,f'questionSlug=="{questionSlug}"',content=cont.encode())
				self.__sql.Opt_Commit()
			else:
				success=False
		self.__successCall() if success else self.__failCall()
	def Update_QuestionCode(self,questionSlug:str,forceLoad:bool=False):
		'''
			请求题目的代码片段codeSnippets，如果forceLoad为真则直接重新请求一遍数据。
		'''
		table='question'
		success=True
		lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
		if(not lst):
			self.__sql.Opt_AppendRow(table,[questionSlug,None,None])
			self.__sql.Opt_Commit()
			forceLoad=True
		if(forceLoad):
			codeNape=self.__config.Get_QuestionCode(questionSlug)
			if(codeNape):
				self.__sql.Set_RowsData(table,f'questionSlug=="{questionSlug}"',code=json.dumps(codeNape))
				self.__sql.Opt_Commit()
			else:
				success=False
		self.__successCall() if success else self.__failCall()





