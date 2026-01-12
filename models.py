from datetime import datetime
import re

class Op:
    def __init__(self, amt, cat, dt=None, cmt='', tp='exp'):
        """amt: сумма, cat: категория, dt: дата, cmt: комментарий, tp: тип"""
        self.amt = float(amt)
        self.cat = cat
        self.dt = dt or datetime.now().strftime('%Y-%m-%d')
        self.cmt = cmt
        self.tp = tp
        
    def validate(self):
        """проверка корректности"""
        try:
            if self.amt <= 0:
                raise ValueError("Сумма > 0")
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', self.dt):
                raise ValueError("Дата YYYY-MM-DD")
            if self.tp not in ['inc', 'exp']:
                raise ValueError("Тип: inc/exp")
            return True
        except Exception as e:
            raise e
            
    def to_dict(self):
        """в словарь"""
        return {
            'amt': self.amt,
            'cat': self.cat,
            'dt': self.dt,
            'cmt': self.cmt,
            'tp': self.tp
        }

class Cat:
    """категория расходов/доходов"""
    def __init__(self, name, tp='exp'):
        self.name = name
        self.tp = tp
        
    def __str__(self):
        return f"{self.name} ({self.tp})"