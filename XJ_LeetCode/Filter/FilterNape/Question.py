from .Base import Base

__all__=['Question']
class Question(Base):
	def Opt_AppendQuestion(self,
				   hasContent:bool=None,
				   hasCode:bool=None):
		'''
			添加筛选项——题目缓存：
				hasContent:是否有content数据;
				hasCode:是否有code数据;
		'''
		super().__init__()
		table='question'
		conditions=[]
		if(hasContent):
			conditions.append(f'{table}.content IS NOT NULL')
		if(hasCode):
			conditions.append(f'{table}.code IS NOT NULL')
		self.table=table
		self.conditions=conditions
		self.cols=[f"{table}.questionSlug"]

