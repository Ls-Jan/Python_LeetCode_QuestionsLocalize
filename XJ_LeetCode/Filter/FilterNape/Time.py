from .Base import Base

__all__=['Time']
class Time(Base):
	def Opt_AppendTime(self,
				startGreaterThan:int=None,
				startLessThan:int=None,
				stopGreaterThan:int=None,
				stopLessThan:int=None):
		'''
			添加筛选项——时间：
				startGreaterThan:start值大于某值；
				startLessThan:start值小于某值；
				stopGreaterThan:stop值大于某值；
				stopLessThan:stop值小于某值；
		'''
		super().__init__()
		table='time'
		conditions=[]
		if(startGreaterThan):
			conditions.append(f'{table}.start > {startGreaterThan}')
		if(startLessThan):
			conditions.append(f'{table}.start < {startLessThan}')
		if(stopGreaterThan):
			conditions.append(f'{table}.stop > {stopGreaterThan}')
		if(stopLessThan):
			conditions.append(f'{table}.stop < {stopLessThan}')
		self.table=table
		self.conditions=conditions
		self.cols=[f"{table}.questionSlug"]

