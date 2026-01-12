import unittest
import asyncio
from models import Op, Cat
from storage import Stor
from async_tasks import AsyncTasks
import os
import pandas as pd

class TestOp(unittest.TestCase):
    def test_valid(self):
        """тест валидации"""
        op = Op(100, 'еда', '2024-01-01', 'обед', 'exp')
        self.assertTrue(op.validate())
        
    def test_invalid_amt(self):
        """тест негативной суммы"""
        op = Op(-100, 'еда', '2024-01-01', 'обед', 'exp')
        with self.assertRaises(ValueError):
            op.validate()
    
    def test_to_dict(self):
        """тест конвертации в словарь"""
        op = Op(100, 'еда', '2024-01-01', 'обед', 'exp')
        d = op.to_dict()
        self.assertEqual(d['amt'], 100)
        self.assertEqual(d['cat'], 'еда')

class TestStor(unittest.TestCase):
    def setUp(self):
        self.stor = Stor('data/test.db')
        
    def test_add(self):
        """тест добавления"""
        op = Op(100, 'тест', '2024-01-01', 'тест', 'exp')
        self.assertTrue(self.stor.add(op))
    
    def test_get_all(self):
        """тест получения всех операций"""
        df = self.stor.get_all()
        self.assertIsInstance(df, pd.DataFrame)
        
    def tearDown(self):
        if os.path.exists('data/test.db'):
            os.remove('data/test.db')

class TestAsyncTasks(unittest.TestCase):
    def test_calc_stats(self):
        """тест асинхронной статистики"""
        df = pd.DataFrame({
            'amt': [100, 200, 150],
            'tp': ['inc', 'exp', 'exp']
        })
        result = asyncio.run(AsyncTasks.calc_stats(df))
        self.assertEqual(result['total_inc'], 100)
        self.assertEqual(result['total_exp'], 350)
        self.assertEqual(result['count'], 3)

class TestCat(unittest.TestCase):
    def test_cat_creation(self):
        """тест создания категории"""
        cat = Cat('Продукты', 'exp')
        self.assertEqual(cat.name, 'Продукты')
        self.assertEqual(cat.tp, 'exp')

if __name__ == '__main__':
    unittest.main()