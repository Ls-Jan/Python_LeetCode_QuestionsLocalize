from .Base import Base

__all__=['List']
class List(Base):
	def __init__(self,
				keywords:list=[],
				tags:list=[],
				difficulty:str=None,
				accessible:bool=None):
		'''
			添加筛选项——列表：
				keywords:题目搜索，支持模糊搜索；
				tags:题目标签，支持多标签；
				difficulty:题目难易度(可选值为“简单”、“中等”、“困难”)；
				accessable:显示可用/不可用的题目；
		'''
		super().__init__()
		table='list'
		conditions=[]
		if(keywords):
			conditions.append(' OR '.join([f'INSTR({table}.title,{key})' for key in keywords]))
		if(tags):
			conditions.append(' OR '.join([f'INSTR({table}.tags,{tag})' for tag in tags]))
		if(difficulty!=None):
			conditions.append(f'INSTR({table}.difficulty,{difficulty})')
		if(accessible!=None):
			conditions.append(f'{table}.invisible=={str(not accessible)}')
		self.table=table
		self.conditions=conditions
		self.cols=[f"{table}.questionSlug"]


