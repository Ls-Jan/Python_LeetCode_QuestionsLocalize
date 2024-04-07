
from XJ.Structs.XJ_SQLite import XJ_SQLite

__all__=['Jointer']
class Jointer:
	'''
		处理多表的连接结果
	'''
	def __init__(self,sql:XJ_SQLite):
		self.__sql=sql
		self.__lst=[]
	def Opt_Append(self,table:str,joinCondition:str,cols:list=None,joinType='INNER'):
		'''
			添加表格，cols为从该表中选中的列(如果传入None则该列全选)。
			首张表的joinCondition不会生效，直接传入None即可。
		'''
		self.__lst.append([table,cols,joinCondition,joinType])
	def Opt_Start(self):
		'''
			开始内连接，并返回内连接结果
		'''
		selectedCols=[]
		joinConditions=[]
		for table,cols,condition,joinType in self.__lst:
			if(not cols):
				cols=self.__sql.Get_ColsName(table)
			for col in cols:
				selectedCols.append(f'{table}.{col}')
			joinConditions.append(f'{joinType} JOIN {table} ON {condition}')
		
		' '.join(joinConditions[1:])
		cmd='SELECT {cols} FROM {table} {joinConditinos}'
		cmd=cmd.format(cols=','.join(selectedCols), table=self.__lst[0][0],joinConditions=joinConditions)
		curr=self.__sql.Get_SQL().execute(cmd)
		return curr.fetchall()
	def Opt_Clear(self):
		'''
			清除Opt_Append记录
		'''
		self.__lst.clear()
