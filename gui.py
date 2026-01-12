from flask import Flask, render_template_string, request, redirect, send_file
from models import Op
from storage import Stor
from analysis import Anl
import os

app = Flask(__name__)
stor = Stor()
anl = Anl(stor)

INDEX = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Финансовый планер</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: #ffffff;
    color: #1a1a1a;
    line-height: 1.6;
    padding: 20px;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
}
h1 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #1a1a1a;
}
.balance {
    font-size: 42px;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 40px;
}
.balance small {
    font-size: 16px;
    color: #666;
    font-weight: 400;
}
.card {
    background: #fff;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
}
h2 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #1a1a1a;
}
form {
    display: grid;
    gap: 16px;
}
.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 6px;
    color: #1a1a1a;
}
input, select {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #d1d1d1;
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
    background: #fff;
    transition: border 0.2s;
}
input:focus, select:focus {
    outline: none;
    border-color: #1a1a1a;
}
button {
    background: #1a1a1a;
    color: #fff;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
}
button:hover {
    background: #000;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}
thead {
    border-bottom: 1px solid #e5e5e5;
}
th {
    text-align: left;
    font-weight: 600;
    padding: 12px 8px;
    color: #666;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
td {
    padding: 16px 8px;
    border-bottom: 1px solid #f5f5f5;
}
tr:last-child td {
    border-bottom: none;
}
.type-inc {
    color: #16a34a;
    font-weight: 600;
}
.type-exp {
    color: #dc2626;
    font-weight: 600;
}
.links {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}
.link {
    color: #1a1a1a;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    transition: all 0.2s;
}
.link:hover {
    border-color: #1a1a1a;
    background: #f5f5f5;
}
.del-link {
    color: #dc2626;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
}
.del-link:hover {
    text-decoration: underline;
}
.empty {
    text-align: center;
    color: #999;
    padding: 40px;
    font-size: 14px;
}
@media (max-width: 768px) {
    .form-row {
        grid-template-columns: 1fr;
    }
    table {
        font-size: 12px;
    }
    th, td {
        padding: 8px 4px;
    }
}
</style>
</head>
<body>
<div class="container">
<h1>Финансовый планер</h1>
<div class="balance">{{ "{:,.0f}".format(bal).replace(',', ' ') }} ₽ <small>баланс</small></div>

<div class="card">
<h2>Новая операция</h2>
<form method="post" action="/add">
<div class="form-row">
<div>
<label>Тип</label>
<select name="tp">
<option value="inc">Доход</option>
<option value="exp">Расход</option>
</select>
</div>
<div>
<label>Сумма</label>
<input name="amt" type="number" step="0.01" required placeholder="0.00">
</div>
</div>
<div class="form-row">
<div>
<label>Категория</label>
<input name="cat" required placeholder="Продукты, транспорт...">
</div>
<div>
<label>Дата</label>
<input name="dt" type="date" required value="{{ today }}">
</div>
</div>
<div>
<label>Комментарий</label>
<input name="cmt" placeholder="Необязательно">
</div>
<button>Добавить операцию</button>
</form>
</div>

<div class="card">
<h2>История операций</h2>
{% if ops.empty %}
<div class="empty">Операции отсутствуют</div>
{% else %}
<table>
<thead>
<tr>
<th>Дата</th>
<th>Категория</th>
<th>Комментарий</th>
<th style="text-align:right">Сумма</th>
<th></th>
</tr>
</thead>
<tbody>
{% for _, row in ops.iterrows() %}
<tr>
<td>{{ row.dt }}</td>
<td>{{ row.cat }}</td>
<td style="color:#999">{{ row.cmt or '—' }}</td>
<td style="text-align:right" class="{{ 'type-inc' if row.tp=='inc' else 'type-exp' }}">
{{ '+' if row.tp=='inc' else '−' }}{{ "{:,.0f}".format(row.amt).replace(',', ' ') }} ₽
</td>
<td style="text-align:right">
<a href="/del/{{ row.id }}" class="del-link">Удалить</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>
{% endif %}
</div>

<div class="links">
<a href="/stats" class="link">Статистика</a>
<a href="/export/csv" class="link">Экспорт CSV</a>
<a href="/export/json" class="link">Экспорт JSON</a>
</div>
</div>
</body>
</html>
'''

STATS = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Статистика</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: #ffffff;
    color: #1a1a1a;
    line-height: 1.6;
    padding: 20px;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
}
h1 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 30px;
    color: #1a1a1a;
}
.back {
    display: inline-block;
    color: #1a1a1a;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    margin-bottom: 30px;
    transition: all 0.2s;
}
.back:hover {
    border-color: #1a1a1a;
    background: #f5f5f5;
}
.card {
    background: #fff;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
}
h2 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #1a1a1a;
}
.cat-list {
    list-style: none;
    display: grid;
    gap: 12px;
}
.cat-item {
    display: flex;
    justify-content: space-between;
    padding: 12px;
    background: #fafafa;
    border-radius: 6px;
    font-size: 14px;
}
.cat-name {
    font-weight: 500;
}
.cat-amt {
    color: #666;
}
.chart {
    text-align: center;
    padding: 20px 0;
}
.chart img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}
.empty {
    text-align: center;
    color: #999;
    padding: 40px;
    font-size: 14px;
}
</style>
</head>
<body>
<div class="container">
<a href="/" class="back">← Назад</a>
<h1>Статистика</h1>

<div class="card">
<h2>Расходы по категориям</h2>
{% if by_cat %}
<ul class="cat-list">
{% for cat, amt in by_cat.items() %}
<li class="cat-item">
<span class="cat-name">{{ cat }}</span>
<span class="cat-amt">{{ "{:,.0f}".format(amt).replace(',', ' ') }} ₽</span>
</li>
{% endfor %}
</ul>
{% else %}
<div class="empty">Данные отсутствуют</div>
{% endif %}
</div>

{% if plot_cat %}
<div class="card">
<h2>Распределение расходов</h2>
<div class="chart">
<img src="data:image/png;base64,{{ plot_cat }}">
</div>
</div>
{% endif %}

{% if plot_time %}
<div class="card">
<h2>Динамика доходов и расходов</h2>
<div class="chart">
<img src="data:image/png;base64,{{ plot_time }}">
</div>
</div>
{% endif %}

{% if plot_top %}
<div class="card">
<h2>Топ категорий</h2>
<div class="chart">
<img src="data:image/png;base64,{{ plot_top }}">
</div>
</div>
{% endif %}
</div>
</body>
</html>
'''

@app.route('/')
def index():
    try:
        from utils import get_today
        ops = stor.get_all()
        bal = anl.bal()
        today = get_today()
        return render_template_string(INDEX, ops=ops, bal=bal, today=today)
    except Exception as e:
        return f"Ошибка: {e}"

@app.route('/add', methods=['POST'])
def add():
    try:
        op = Op(
            amt=request.form['amt'],
            cat=request.form['cat'],
            dt=request.form['dt'],
            cmt=request.form.get('cmt',''),
            tp=request.form['tp']
        )
        stor.add(op)
        return redirect('/')
    except Exception as e:
        return f"Ошибка: {e}"

@app.route('/del/<int:id>')
def delete(id):
    try:
        stor.del_op(id)
        return redirect('/')
    except Exception as e:
        return f"Ошибка: {e}"

@app.route('/stats')
def stats():
    try:
        by_cat = anl.by_cat()
        plot_cat = anl.plot_cat()
        plot_time = anl.plot_time()
        plot_top = anl.plot_top_cat()
        return render_template_string(STATS, by_cat=by_cat, plot_cat=plot_cat, 
                                     plot_time=plot_time, plot_top=plot_top)
    except Exception as e:
        return f"Ошибка: {e}"

@app.route('/export/<fmt>')
def export(fmt):
    try:
        if fmt == 'csv':
            stor.exp_csv()
            return send_file('data/export.csv', as_attachment=True)
        elif fmt == 'json':
            stor.exp_json()
            return send_file('data/export.json', as_attachment=True)
    except Exception as e:
        return f"Ошибка: {e}"

def run():
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)