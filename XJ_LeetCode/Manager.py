
from .Crawler import Crawler
from .Filter import Filter,FilterNape
from .Jointer import Jointer

import os
import json

__all__=['Manager']

class Manager:
	'''
		LeetCode的题库管理
	'''
	def __init__(self,crawler:Crawler):
		'''
			需传入配置好的Crawler对象
		'''
		self.__crawler=crawler
		self.__sql=crawler.Get_SQL()
		self.__config=crawler.Get_Config()
		self.__filter=Filter(self.__sql)
		self.__jointer=Jointer(self.__sql)
	def Get_Crawler(self):
		'''
			返回Crawler对象
		'''
		return self.__crawler
	def Get_QuestionList(self,*filterNapes:FilterNape):
		'''
			传入筛选项，并返回筛选后的题目列表。
			返回的题目列表将除了包含原本的config.tables['list']还包含额外的三列信息['finish','favorite','hasCache']。
			需提前调用Crawler.Update_QuestionList。
		'''
		if(not filterNapes):
			filterNapes=[FilterNape.List()]
		self.__filter.Opt_Clear()
		for nape in filterNapes:
			self.__filter.Opt_Append(nape)
		self.__filter.Opt_Start()

		filterTable=self.__filter.Get_ReslutTableName()
		if(filterTable):
			self.__jointer.Opt_Clear()
			self.__jointer.Opt_Append(filterTable,None,[],"LEFT")
			self.__jointer.Opt_Append('list',f'{filterTable}.questionSlug==list.questionSlug',list(map(lambda key:f'list.{key}',self.__config.tables['list'])),"LEFT")
			self.__jointer.Opt_Append('record',f'{filterTable}.questionSlug==record.questionSlug',['record.finish IS NOT NULL AND record.finish==TRUE AS finish','record.favorite IS NOT NULL AND record.favorite==TRUE AS favorite'],"LEFT")
			self.__jointer.Opt_Append('question',f'{filterTable}.questionSlug==question.questionSlug',['question.content IS NOT NULL AND question.code IS NOT NULL AS hasCache'],"LEFT")
			rst=self.__jointer.Opt_Start()
			return rst
		else:
			return []
	def Get_QuestionContent(self,questionSlug:str):
		'''
			请求题目内容(字符串)，无数据则返回None。
			需提前调用Crawler.Update_QuestionContent。
		'''
		table='question'
		lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
		if(lst):
			row=self.__TransRowData(self.__config.tables[table],lst[0])
			data=row['content']
			if(data):
				return data
		return None
	def Get_QuestionCode(self,questionSlug:str):
		'''
			获取题目的代码片段codeSnippets，返回{lang<str>:code<str>}，无数据则返回None。
			需提前调用Crawler.Update_QuestionCode。
		'''
		table='question'
		lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
		if(lst):
			row=self.__TransRowData(self.__config.tables[table],lst[0])
			data=row['code']
			if(data):
				return json.loads(data)
		return None
	def Get_QuestionRecord(self,questionSlug:str):
		'''
			获取题目记录，无数据则返回None
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
	def Get_QuestionTime(self,questionSlug:str):
		'''
			获取题目时间，返回[(start<int>,stop<int>),...]，无数据则返回None
		'''
		table='time'
		lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
		if(lst):
			lst=list(map(lambda item:tuple(item[1:]),lst))
			return lst
		return None
	def Upt_QuestionRecord(self,questionSlug:str,finish:bool=None,favorite:bool=None,codePaths:dict={}):
		'''
			更新题目记录。
			finish：完成标记
			favorite:收藏标记
			codePaths:{编程语言:导出的文件路径}
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
	def Upt_QuestionTime(self,questionSlug:str,start:int,stop:int):
		'''
			追加一条时间记录
		'''
		table='time'
		self.__sql.Opt_AppendRow(table,[questionSlug,start,stop])
	def __TransRowData(self,cols:list,rowData:dict):
		'''
			将数据库中读取到的行内容转换为字典
		'''
		return {cols[i]:rowData[i] for i in range(len(cols))}



