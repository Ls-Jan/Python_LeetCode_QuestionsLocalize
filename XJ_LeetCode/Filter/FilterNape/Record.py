from .Base import Base

__all__=['Record']
class Record(Base):
	def Opt_AppendRecord(self,
				   finish:bool=None,
				   favorite:bool=None,
				   hasCode:bool=None):
		'''
			添加筛选项——记录：
				finish:完成;
				favorite:收藏;
				hasCode:有代码文件记录;
		'''
		super().__init__()
		table='record'
		conditions=[]
		if(finish):
			conditions.append(f'{table}.finish=={str(finish)}')
		if(favorite):
			conditions.append(f'{table}.favorite=={str(favorite)}')
		if(hasCode):
			conditions.append(f'{table}.codePath IS NOT NULL')
		self.table=table
		self.conditions=conditions
		self.cols=[f"{table}.questionSlug"]

