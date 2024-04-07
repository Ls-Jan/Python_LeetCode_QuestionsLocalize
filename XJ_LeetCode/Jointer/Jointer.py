
from XJ.Structs.XJ_SQLite import XJ_SQLite

__all__=['Jointer']
class Jointer:
	'''
		建造者模式，将多表的连接查询分成多次进行
	'''
	def __init__(self,sql:XJ_SQLite):
		self.__sql=sql
		self.__lst=[]
	def Opt_Append(self,table:str,joinCondition:str,cols:list=None,joinType='INNER'):
		'''
			添加表格，cols为从该表中选中的列(如果传入None则该列全选)。
			joinType是该表被上一个表以哪种方式进行连接，默认内连接。
			首次调用该函数时joinCondition和joinType不会生效，joinCondition直接传入None即可。
		'''
		self.__lst.append([table,cols,joinCondition,joinType])
	def Opt_Start(self,saveToNewTable:str=None):
		'''
			开始内连接，并返回内连接结果。
			如果saveToNewTable为真那么将另存到一张新的临时表中，并且返回结果为None。
		'''
		selectedCols=[]
		joinConditions=[]
		for table,cols,condition,joinType in self.__lst:
			if(cols==None):
				cols=map(lambda col:f'{table}.{col}',self.__sql.Get_ColsName(table))
			selectedCols.extend(cols)
			joinConditions.append(f'{joinType} JOIN {table} ON {condition}')
		createNewTableAs=''
		if(saveToNewTable):
			self.__sql.Opt_DeleteTable(saveToNewTable)
			createNewTableAs=f'CREATE TEMPORARY TABLE {saveToNewTable} AS'
		cmd='{createNewTableAs} SELECT {cols} FROM {table} {joinConditions}'
		cmd=cmd.format(createNewTableAs=createNewTableAs,cols=','.join(selectedCols),table=self.__lst[0][0],joinConditions=' '.join(joinConditions[1:]))
		curr=self.__sql.Get_SQL().execute(cmd)
		return None if saveToNewTable else curr.fetchall()
	def Opt_Clear(self):
		'''
			清除Opt_Append记录
		'''
		self.__lst.clear()
