


import XJ_LeetCode


if True:
	sqlPath:str='./data'
	imgPath:str='./data/img'
	nape=XJ_LeetCode.FilterNape.List(['字母','最'],['数组'])
	# nape=XJ_LeetCode.FilterNape.List(['字母'],['贪心'])
	crawler=XJ_LeetCode.Crawler(sqlPath,imgPath)
	manager=XJ_LeetCode.Manager(crawler)
	rst=manager.Get_QuestionList(nape)[:10]
	for i in rst:
		# print(i[3])
		print(i)

