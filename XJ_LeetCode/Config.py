
import os
import re
import json
import requests

__all__=['Config']

class Config:
	'''
		XJ_LeetCode的配置类。
		部分数据与其他类(例如XJ_LeetCode)出现了部分不可避免的耦合，例如表格列名。

		除了url、header和keysMap内的键名以外，其他都是只能看不能动(即tables内的数据不能改，改了就暴毙)
	'''
	url="https://leetcode.cn/graphql/"
	header={
		"content-type": "application/json",
	}
	keysMap={#键名与请求传回的题目列表信息关联
		'frontendQuestionId':'id',
		'titleCn':'title',
		'topicTags':'tags',
		'difficulty':'difficulty',
		'titleSlug':'questionSlug',
		'paidOnly':'invisible',
	}
	tables={#每张表的主键均以questionSlug为准。
		'''
			其中出现的布尔量使用字符串记录，即'False'和'True'，
			因为直接存布尔量的话结果就是变成了0和1，会对后续的判断造成干扰，不如统一处理为字符串
		'''
		'list':[
			'questionSlug',
			'id',
			'title',
			'tags',
			'difficulty',
			'invisible',
		],
		'question':[
			'questionSlug',
			'content',
			'code',
		],
		'record':[
			'questionSlug',
			'finish',#是否标记完成
			'favorite',#收藏
			'codePath',#导出的文件路径(相对路径)(是个字典数据，{编程语言:代码路径})
		],
		'time':[
			'questionSlug',
			'start',
			'stop',
		],
	}

	@classmethod
	def Get_QuestionList(self,start:int,count:int):
		'''
			请求题目列表数据，如果返回None则说明请求失败。
			返回的数据单元是元组，顺序与tables['list']关联
		'''
		payload = {
			"query": "\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    hasMore\n    total\n    questions {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId\n      isFavor\n      paidOnly\n      solutionNum\n      status\n      title\n      titleCn\n      titleSlug\n      topicTags {\n        name\n        nameTranslated\n        id\n        slug\n      }\n      extra {\n        hasVideoSolution\n        topCompanyTags {\n          imgUrl\n          slug\n          numSubscribed\n        }\n      }\n    }\n  }\n}\n    ",
			"variables": {
				"categorySlug": "algorithms",
				"skip": start,
				"limit": count,
				"filters": {}
			},
			"operationName": "problemsetQuestionList"
		}
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
				row=list(map(lambda key:str(row[key]),self.tables['list']))
				# row=list(map(lambda key:row[key] if key=='invisible' else str(row[key]),self.tables['list']))
				rst.append(row)
			start+=len(data)
		return rst
	@classmethod
	def Get_QuestionContent(self,questionSlug:str):
		'''
			请求题目内容，请求失败则返回None。
			会返回两部分数据，一个是题目内容cont<str>，一个是图片列表imgs[tag<str>,url<str>,img<bytes>])，后者用于将图片转为本地链接
		'''
		payload = {
			"query": "\n    query questionTranslations($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    translatedTitle\n    translatedContent\n  }\n}\n    ",
			"variables": {
				"titleSlug": questionSlug
			},
			"operationName": "questionTranslations"
		}	
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
	@classmethod
	def Get_QuestionCode(self,questionSlug:str):
		'''
			获取题目的代码片段codeSnippets，请求失败则返回None。
			返回的是{lang<str>:code<str>}。
		'''
		payload={
			"query": "\n    query questionEditorData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    codeSnippets {\n      lang\n      langSlug\n      code\n    }\n    envInfo\n    enableRunCode\n    hasFrontendPreview\n    frontendPreviews\n  }\n}\n    ",
			"variables": {
				"titleSlug": questionSlug
			},
			"operationName": "questionEditorData"
		}
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


