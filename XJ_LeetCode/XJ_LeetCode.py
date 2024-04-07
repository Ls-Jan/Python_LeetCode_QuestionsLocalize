
from .Crawler import Crawler
from .Filter import Filter
from .Jointer import Jointer

from XJ.Structs.XJ_SQLite import XJ_SQLite
from Config import Config
import os
import json

__all__=['XJ_LeetCode']

class XJ_LeetCode:
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
	def Update_QuestionsList(self,updateCall=lambda count:print(f'当前已读取数据[{count}]'),successCall=lambda:print('读取完毕'),failCall=lambda:print('联网读取失败'),reload:bool=True):
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
		if(success):
			successCall()
		else:
			failCall()
	def Get_QuestionContent(self,questionSlug:str,*,loadFromDB:bool=True):
		'''
			请求题目内容(字符串)，请求失败则返回None。
			题目中出现的图片数据将保存到指定的本地路径中。
		'''
		table='question'
		if(loadFromDB):
			lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
			if(lst):
				row=self.__TransRowData(self.__config.tables[table],lst[0])
				data=row['content']
				if(data):
					return data
			else:
				self.__sql.Opt_AppendRow(table,[questionSlug,None,None])
				self.__sql.Opt_Commit()
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
			self.__sql.Set_RowsData(table,f'questionSlug=="{questionSlug}"',content=data.encode())
			self.__sql.Opt_Commit()
			return data
		return None
	def Get_QuestionCode(self,questionSlug:str,*,loadFromDB:bool=True):
		'''
			获取题目的代码片段codeSnippets，请求失败则返回None。
			返回的是{lang<str>:code<str>}。
		'''
		table='question'
		if(loadFromDB):
			lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
			if(lst):
				row=self.__TransRowData(self.__config.tables[table],lst[0])
				data=row['code']
				if(data):
					return json.loads(data)
			else:
				self.__sql.Opt_AppendRow(table,[questionSlug,None,None])
				self.__sql.Opt_Commit()
		data=self.__config.Get_QuestionCode(questionSlug)
		if(data):
			self.__sql.Set_RowsData(table,f'questionSlug=="{questionSlug}"',code=json.dumps(data))
			self.__sql.Opt_Commit()
		return data
	# def Get_CacheSet(self,questionContent:bool=True,questionCode:bool=True):
	# 	'''
	# 		【该函数无实际作用】
	# 		获取有缓存的题目(questionSlug)集合。
	# 	'''
	# 	table='question'
	# 	condition=' AND '.join([f'{col} IS NOT NULL' for col,flag in {'content':questionContent,'code':questionCode}.items() if flag])
	# 	lst=self.__sql.Get_RowsData(table,condition,cols=['questionSlug'])
	# 	return set(map(lambda item:item[0],lst))
	def Get_QuestionRecord(self,questionSlug:str):
		'''
			获取题目记录，如果没记录则返回None
		'''
		table='record'
		lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
		if(lst):
			row=self.__TransRowData(self.__config.tables[table],lst[0])
			row['finish']=bool(row['finish'])
			row['favorite']=bool(row['favorite'])
			row['codePath']=json.loads(row['codePath'])
			return row
		return None
	def Upt_QuestionRecord(self,questionSlug:str,finish:bool=None,favorite:bool=None,codePaths:dict={}):
		'''
			更新题目记录。
			finish：完成标记
			favorite:收藏标记
			filePath:{编程语言:导出的文件路径}
		'''
		table='record'
		if(not self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')):
			self.__sql.Opt_AppendRow(table,[questionSlug,False,False,json.dumps({})])
		changeField={}
		if(finish!=None):
			changeField['finish']=finish
		if(favorite!=None):
			changeField['favorite']=favorite
		if(codePaths):
			codePath=self.Get_QuestionRecord(questionSlug)['code']
			for lang,path in codePaths.items():
				codePath.pop(lang,None)
				if(path!=None):
					codePath[lang]=path
			changeField['codePath']=json.dumps(codePath)
		self.__sql.Set_RowsData(table,f'questionSlug=="{questionSlug}"',**changeField)
		self.__sql.Opt_Commit()
	def __TransRowData(self,cols:list,rowData:dict):
		'''
			将数据库中读取到的行内容转换为字典
		'''
		return {cols[i]:rowData[i] for i in range(len(cols))}



