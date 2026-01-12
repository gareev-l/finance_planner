import asyncio
import pandas as pd
from datetime import datetime

class AsyncTasks:
    """асинхронные задачи"""
    
    @staticmethod
    async def calc_stats(df):
        """асинхронный расчет статистики"""
        await asyncio.sleep(0.01)  # симуляция долгой операции
        if df.empty:
            return {'total_inc': 0, 'total_exp': 0, 'count': 0}
        
        stats = {
            'total_inc': df[df['tp']=='inc']['amt'].sum(),
            'total_exp': df[df['tp']=='exp']['amt'].sum(),
            'count': len(df)
        }
        return stats
    
    @staticmethod
    async def process_batch(ops):
        """асинхронная обработка пакета операций"""
        tasks = []
        for op in ops:
            task = asyncio.create_task(AsyncTasks._process_op(op))
            tasks.append(task)
        return await asyncio.gather(*tasks)
    
    @staticmethod
    async def _process_op(op):
        """обработка одной операции"""
        await asyncio.sleep(0.001)
        return op.to_dict()
    
    @staticmethod
    async def analyze_trends(df):
        """асинхронный анализ трендов"""
        await asyncio.sleep(0.01)
        if df.empty:
            return {}
        
        df['dt'] = pd.to_datetime(df['dt'])
        monthly = df.groupby(df['dt'].dt.to_period('M')).agg({
            'amt': 'sum',
            'tp': 'count'
        })
        return monthly.to_dict()