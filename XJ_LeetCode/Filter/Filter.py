
from . import FilterNape
from XJ.Structs.XJ_SQLite import XJ_SQLite

__all__=['Filter']
#TODO：mole，又不是不能用————sql支持多条join子句，因此不需要连续两张临时表先后存储临时数据，可以优化
class Filter:
	'''
		建造者模式，将多表的条件查询分成多次进行，并最终处理为单张临时表，该表仅记录questionSlug信息
	'''
	def __init__(self,sql:XJ_SQLite,tempTableName:str='tempFilter_{n}'):
		'''
			简单搜索，会占用两个临时表
		'''
		self.__sql=sql
		self.__tempTable=tempTableName
		self.__lst=[]
	def Opt_Append(self,filterNape:FilterNape.Base):
		'''
			添加筛选项。
		'''
		self.__lst.append(filterNape)
	def Opt_Start(self):
		'''
			开始生成匹配结果。
		'''
		compTable=None
		saveTable=''
		for i in range(len(self.__lst)):
			nape=self.__lst[i]
			saveTable=self.__tempTable.format(n=str(i%2))
			self.__sql.Opt_DeleteTable(saveTable)
			self.__sql.Get_RowsData(
				nape.table,
				*nape.conditions,
				cols=nape.cols,
				conditionsLink="AND",
				distinct=True,
				joinTableName=compTable,
				innerJoinCondition=f"{nape.table}.questionSlug=={str(compTable)}.questionSlug",
				saveToNewTable=saveTable)
			compTable=saveTable
	def Opt_Clear(self):
		'''
			清空Opt_Append的操作
		'''
		self.__lst.clear()
	def Get_ReslutTableName(self):
		'''
			获取生成的表，以便后续进行表格的连接操作
		'''
		if(len(self.__lst)):
			saveTable=self.__tempTable.format(n=str(len(self.__lst)-1%2))
			return saveTable
		return None


