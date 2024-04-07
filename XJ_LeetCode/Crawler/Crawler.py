
from ..Config import Config
from XJ.Structs.XJ_SQLite import XJ_SQLite

import os
import re
import json
import requests
from threading import Thread

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
		self.__updateCall=lambda count:print(f'当前已读取数据[{count}]')
		self.__successCall=lambda:print('读取完毕')
		self.__failCall=lambda:print('联网读取失败')
		self.__th=None
	def Get_Config(self):
		'''
			返回内部的Config对象
		'''
		return self.__config
	def Get_SQL(self):
		'''
			返回内部的XJ_SQLite对象
		'''
		return self.__sql
	def Get_QuestionsCount(self):
		'''
			获取题目数量
		'''
		return self.__sql.Get_RowsData('list',onlyCount=True)
	def Set_Callback(self,updateCall=None,successCall=None,failCall=None):
		'''
			设置数据更新时调用的回调函数。
			updateCall(count)：在Update_QuestionList中会被调用；
			successCall()：在数据顺利更新时会被调用；
			failCall()：在数据更新失败时会被调用；
		'''
		if(updateCall):
			self.__updateCall=updateCall
		if(successCall):
			self.__successCall=successCall
		if(failCall):
			self.__failCall=failCall
	def Update_QuestionsList(self,reload:bool=True,_async:bool=True):
		'''
			加载题目列表，如果reload为真则从头开始读取，为假时读取剩余部分。
			默认异步执行，如果当前的异步仍未执行完毕则该函数调用失败。
		'''
		if(_async):
			if(self.__th):
				return False
			self.__th=Thread(target=self.__Th_UpdateList,args=(reload,False))
		else:
			table='list'
			self.__sql.Opt_CreateTable(table,self.__config.tables[table],reload)
			self.__sql.Opt_Commit()
			start=0 if reload else self.Get_QuestionsCount()
			count=100
			success=True
			while(True):
				lst=self.__GetQuestionList(start,count)
				if(lst==None):
					success=False
					break
				for row in lst:
					self.__sql.Opt_AppendRow(table,row)
				self.__sql.Opt_Commit()
				start+=len(row)
				self.__updateCall(start)
				if(len(row)!=count):
					break
			self.__successCall() if success else self.__failCall()
		return True
	def Update_QuestionContent(self,questionSlug:str,reload:bool=False,_async:bool=True):
		'''
			请求题目内容(字符串)，如果reload为真则直接重新请求一遍数据。
			题目中出现的图片数据将保存到指定的本地路径中。
			默认异步执行，如果当前的异步仍未执行完毕则该函数调用失败。
		'''
		if(_async):
			if(self.__th):
				return False
			self.__th=Thread(target=self.__Th_UpdateContent,args=(questionSlug,reload,False))
		else:
			table='question'
			success=True
			lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
			if(not lst):
				self.__sql.Opt_AppendRow(table,[questionSlug,None,None])
				self.__sql.Opt_Commit()
				reload=True
			if(reload):
				rst=self.__GetQuestionContent(questionSlug)
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
		return True
	def Update_QuestionCode(self,questionSlug:str,reload:bool=False,_async:bool=True):
		'''
			请求题目的代码片段codeSnippets，如果reload为真则直接重新请求一遍数据。
			默认异步执行，如果当前的异步仍未执行完毕则该函数调用失败。
		'''
		if(_async):
			if(self.__th):
				return False
			self.__th=Thread(target=self.__Th_UpdateCode,args=(questionSlug,reload,False))
			return True
		else:
			table='question'
			success=True
			lst=self.__sql.Get_RowsData(table,f'questionSlug=="{questionSlug}"')
			if(not lst):
				self.__sql.Opt_AppendRow(table,[questionSlug,None,None])
				self.__sql.Opt_Commit()
				reload=True
			if(reload):
				codeNape=self.__GetQuestionCode(questionSlug)
				if(codeNape):
					self.__sql.Set_RowsData(table,f'questionSlug=="{questionSlug}"',code=json.dumps(codeNape))
					self.__sql.Opt_Commit()
				else:
					success=False
			self.__successCall() if success else self.__failCall()

	def __GetQuestionList(self,start:int,count:int):
		'''
			请求题目列表数据，如果返回None则说明请求失败。
			返回的数据单元是元组，顺序与tables['list']关联
		'''
		payload=self.__config.payload['list']
		payload=payload.replace('[start]',start).replace('[count]',count)
		cont = self.__RequestUrl(self.url,False,self.header,json.dumps(payload))
		if(not cont):
			return None
		data=json.loads(cont.decode())
		data=data['data']['problemsetQuestionList']['questions']
		rst=[]
		if(data):
			for item in data:
				item['topicTags']=list(map(lambda item:item['nameTranslated'],item['topicTags']))
				item['difficulty']={'EASY':'简单','MEDIUM':'中等','HARD':'困难'}[item['difficulty'].upper()]
				row={name:item[key] for key,name in self.keysMap.items()}
				row=list(map(lambda key:row[key] if key=='invisible' else str(row[key]),self.tables['list']))
				rst.append(row)
			start+=len(data)
		return rst
	def __GetQuestionContent(self,questionSlug:str):
		'''
			请求题目内容，请求失败则返回None。
			会返回两部分数据，一个是题目内容cont<str>，一个是图片列表imgs[tag<str>,url<str>,img<bytes>])，后者用于将图片转为本地链接
		'''
		payload=self.__config.payload['content']
		payload=payload.replace('[questionSlug]',questionSlug)
		cont = self.__RequestUrl(self.__url,False,self.__header,json.dumps(payload))
		imgs=[]
		if(cont):
			data=json.loads(cont.decode())
			data=data['data']['question']['translatedContent']
			if(not data):
				data=''
			for match in re.finditer('<img .*? src="(.*?)"',data):#读取其中的图片数据，以便后期转为本地图片
				img=self.__RequestUrl(match.group(1))
				imgs.append((match.group(0),match.group(1),img))
			return cont,imgs
		return None
	def __GetQuestionCode(self,questionSlug:str):
		'''
			获取题目的代码片段codeSnippets，请求失败则返回None。
			返回的是{lang<str>:code<str>}。
		'''
		payload=self.__config.payload['code']
		payload=payload.replace('[questionSlug]',questionSlug)
		cont = self.__RequestUrl(self.url,False,self.header,json.dumps(payload))
		if(cont):
			temp=json.loads(cont.decode())
			temp=temp['data']['question']['codeSnippets']
			data={}
			for item in temp:
				data[item['lang']]=item['code']
			return data
		return None
	@staticmethod
	def __RequestUrl(url,GET=True,headers=None,payload=None):
		func = getattr(requests,'get' if GET else 'post')
		rst=None
		try:
			res=func(url,data=payload,headers=headers)
			rst=res.content
		except:
			pass
		return rst

