

__all__=['Config']

class Config:
	'''
		XJ_LeetCode的配置类，配置不需要进行调整，除非无法顺利获取数据。
		keysMap的值以及以及tables内的数据是只能看不能动的，除此之外的其他内容可以根据实际情况进行适当改动。

		payload的值，里头的关键词"[start]"、"[count]"、"[questionSlug]"不能改动，因为要在别的地方进行字符串替换
	'''
	url="https://leetcode.cn/graphql/"
	header={
		"content-type": "application/json",
	}
	payload={
		'list':'''
				{
					"query": "\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    hasMore\n    total\n    questions {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId\n      isFavor\n      paidOnly\n      solutionNum\n      status\n      title\n      titleCn\n      titleSlug\n      topicTags {\n        name\n        nameTranslated\n        id\n        slug\n      }\n      extra {\n        hasVideoSolution\n        topCompanyTags {\n          imgUrl\n          slug\n          numSubscribed\n        }\n      }\n    }\n  }\n}\n    ",
					"variables": {
						"categorySlug": "algorithms",
						"skip": [start],
						"limit": [count],
						"filters": {}
					},
					"operationName": "problemsetQuestionList"
				}
			''',
		'content':'''
				{
					"query": "\n    query questionTranslations($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    translatedTitle\n    translatedContent\n  }\n}\n    ",
					"variables": {
						"titleSlug": [questionSlug]
					},
					"operationName": "questionTranslations"
				}
			''',
		'code':'''
				{
					"query": "\n    query questionEditorData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    codeSnippets {\n      lang\n      langSlug\n      code\n    }\n    envInfo\n    enableRunCode\n    hasFrontendPreview\n    frontendPreviews\n  }\n}\n    ",
					"variables": {
						"titleSlug": [questionSlug]
					},
					"operationName": "questionEditorData"
				}
			''',
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




