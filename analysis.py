import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import asyncio
from async_tasks import AsyncTasks

class Anl:
    def __init__(self, stor):
        self.stor = stor
        self.async_tasks = AsyncTasks()
        
    def bal(self):
        """текущий баланс"""
        try:
            df = self.stor.get_all()
            if df.empty:
                return 0
            inc = df[df['tp']=='inc']['amt'].sum()
            exp = df[df['tp']=='exp']['amt'].sum()
            return inc - exp
        except:
            return 0
    
    async def bal_async(self):
        """асинхронный расчет баланса"""
        df = self.stor.get_all()
        stats = await self.async_tasks.calc_stats(df)
        return stats['total_inc'] - stats['total_exp']
            
    def by_cat(self):
        """расходы по категориям"""
        try:
            df = self.stor.get_all()
            if df.empty:
                return {}
            exp_df = df[df['tp']=='exp']
            return exp_df.groupby('cat')['amt'].sum().to_dict()
        except:
            return {}
            
    def by_period(self, dt_from, dt_to):
        """статистика за период"""
        try:
            df = self.stor.filter(dt_from=dt_from, dt_to=dt_to)
            if df.empty:
                return {'inc':0, 'exp':0, 'bal':0}
            inc = df[df['tp']=='inc']['amt'].sum()
            exp = df[df['tp']=='exp']['amt'].sum()
            return {'inc':inc, 'exp':exp, 'bal':inc-exp}
        except:
            return {'inc':0, 'exp':0, 'bal':0}
    
    def top_cat(self, n=5):
        """топ категорий расходов"""
        cat_data = self.by_cat()
        sorted_cats = sorted(cat_data.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_cats[:n])
            
    def plot_cat(self):
        """график по категориям"""
        try:
            data = self.by_cat()
            if not data:
                return None
            
            plt.figure(figsize=(10,8))
            colors = ['#1a1a1a', '#4a4a4a', '#7a7a7a', '#aaaaaa', '#dadada']
            plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%',
                   colors=colors, textprops={'fontsize': 11})
            plt.title('Расходы по категориям', fontsize=14, pad=20)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            img = base64.b64encode(buf.getvalue()).decode()
            plt.close()
            return img
        except:
            return None
            
    def plot_time(self):
        """график расходов по времени"""
        try:
            df = self.stor.get_all()
            if df.empty:
                return None
            df['dt'] = pd.to_datetime(df['dt'])
            grp = df.groupby(['dt','tp'])['amt'].sum().unstack(fill_value=0)
            
            plt.figure(figsize=(12,6))
            plt.style.use('default')
            
            if 'inc' in grp.columns:
                plt.plot(grp.index, grp['inc'], label='Доходы', 
                        marker='o', color='#16a34a', linewidth=2)
            if 'exp' in grp.columns:
                plt.plot(grp.index, grp['exp'], label='Расходы', 
                        marker='o', color='#dc2626', linewidth=2)
            
            plt.xlabel('Дата', fontsize=11)
            plt.ylabel('Сумма, ₽', fontsize=11)
            plt.title('Динамика доходов и расходов', fontsize=14, pad=20)
            plt.legend(fontsize=11)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            img = base64.b64encode(buf.getvalue()).decode()
            plt.close()
            return img
        except:
            return None
    
    def plot_top_cat(self):
        """график топ категорий"""
        try:
            data = self.top_cat(10)
            if not data:
                return None
            
            plt.figure(figsize=(10,6))
            cats = list(data.keys())
            vals = list(data.values())
            
            plt.barh(cats, vals, color='#1a1a1a')
            plt.xlabel('Сумма, ₽', fontsize=11)
            plt.title('Топ категорий расходов', fontsize=14, pad=20)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            img = base64.b64encode(buf.getvalue()).decode()
            plt.close()
            return img
        except:
            return None