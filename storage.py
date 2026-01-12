import aiosqlite
import asyncio
import csv
import json
import pandas as pd
from threading import Lock

class Stor:
    def __init__(self, db='data/fin.db'):
        self.db = db
        self.lock = Lock()
        asyncio.run(self._init_db())
        
    async def _init_db(self):
        """создание таблицы"""
        try:
            async with aiosqlite.connect(self.db) as conn:
                await conn.execute('''CREATE TABLE IF NOT EXISTS ops (
                    id INTEGER PRIMARY KEY,
                    amt REAL,
                    cat TEXT,
                    dt TEXT,
                    cmt TEXT,
                    tp TEXT
                )''')
                await conn.commit()
        except Exception as e:
            raise e
            
    async def _add_async(self, op):
        """асинхронное добавление"""
        try:
            op.validate()
            async with aiosqlite.connect(self.db) as conn:
                await conn.execute(
                    'INSERT INTO ops (amt,cat,dt,cmt,tp) VALUES (?,?,?,?,?)',
                    (op.amt, op.cat, op.dt, op.cmt, op.tp)
                )
                await conn.commit()
            return True
        except Exception as e:
            raise e
    
    def add(self, op):
        """добавить операцию"""
        return asyncio.run(self._add_async(op))
        
    async def _get_all_async(self):
        """асинхронное получение всех операций"""
        try:
            async with aiosqlite.connect(self.db) as conn:
                async with conn.execute('SELECT * FROM ops ORDER BY dt DESC') as cursor:
                    rows = await cursor.fetchall()
                    cols = [desc[0] for desc in cursor.description]
                    return pd.DataFrame(rows, columns=cols)
        except Exception as e:
            return pd.DataFrame()
    
    def get_all(self):
        """все операции"""
        return asyncio.run(self._get_all_async())
        
    async def _del_async(self, id):
        """асинхронное удаление"""
        try:
            async with aiosqlite.connect(self.db) as conn:
                await conn.execute('DELETE FROM ops WHERE id=?', (id,))
                await conn.commit()
        except Exception as e:
            raise e
    
    def del_op(self, id):
        """удалить по id"""
        return asyncio.run(self._del_async(id))
        
    async def _filter_async(self, cat=None, dt_from=None, dt_to=None):
        """асинхронная фильтрация"""
        try:
            q = 'SELECT * FROM ops WHERE 1=1'
            params = []
            if cat:
                q += ' AND cat=?'
                params.append(cat)
            if dt_from:
                q += ' AND dt>=?'
                params.append(dt_from)
            if dt_to:
                q += ' AND dt<=?'
                params.append(dt_to)
            q += ' ORDER BY dt DESC'
            
            async with aiosqlite.connect(self.db) as conn:
                async with conn.execute(q, params) as cursor:
                    rows = await cursor.fetchall()
                    cols = [desc[0] for desc in cursor.description]
                    return pd.DataFrame(rows, columns=cols)
        except Exception as e:
            return pd.DataFrame()
    
    def filter(self, cat=None, dt_from=None, dt_to=None):
        """фильтр"""
        return asyncio.run(self._filter_async(cat, dt_from, dt_to))
        
    def exp_csv(self, path='data/export.csv'):
        """экспорт CSV"""
        try:
            df = self.get_all()
            df.to_csv(path, index=False, encoding='utf-8')
        except Exception as e:
            raise e
            
    def imp_csv(self, path):
        """импорт CSV"""
        try:
            df = pd.read_csv(path)
            asyncio.run(self._imp_csv_async(df))
        except Exception as e:
            raise e
    
    async def _imp_csv_async(self, df):
        """асинхронный импорт"""
        async with aiosqlite.connect(self.db) as conn:
            for _, row in df.iterrows():
                await conn.execute(
                    'INSERT INTO ops (amt,cat,dt,cmt,tp) VALUES (?,?,?,?,?)',
                    (row['amt'], row['cat'], row['dt'], row['cmt'], row['tp'])
                )
            await conn.commit()
            
    def exp_json(self, path='data/export.json'):
        """экспорт JSON"""
        try:
            df = self.get_all()
            df.to_json(path, orient='records', force_ascii=False)
        except Exception as e:
            raise e