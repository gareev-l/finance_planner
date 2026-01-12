from datetime import datetime, timedelta
import asyncio

def get_month_range():
    """диапазон текущего месяца"""
    now = datetime.now()
    start = now.replace(day=1).strftime('%Y-%m-%d')
    next_m = now.replace(day=28) + timedelta(days=4)
    end = (next_m.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
    return start, end

def fmt_amt(amt):
    """форматирование суммы"""
    return f"{amt:,.2f}".replace(',', ' ')

async def async_validate_date(dt_str):
    """асинхронная валидация даты"""
    await asyncio.sleep(0.001)
    try:
        datetime.strptime(dt_str, '%Y-%m-%d')
        return True
    except:
        return False

def get_today():
    """текущая дата"""
    return datetime.now().strftime('%Y-%m-%d')