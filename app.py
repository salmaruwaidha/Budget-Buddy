from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'srf*123'
app.config['MYSQL_DB'] = 'budgetbuddy'

mysql = MySQL(app)

def calculate_net_balance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT SUM(amount) FROM income")
    total_income = cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cur.fetchone()[0] or 0
    net_balance = total_income - total_expenses
    cur.close()
    return net_balance

@app.route('/')
def index():
    net_balance = calculate_net_balance()
    return render_template('index.html', net_balance=net_balance)

# Add Income Route
@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        date = request.form['date']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO income (description, amount, date) VALUES (%s, %s, %s)",
                    (description, amount, date))
        mysql.connection.commit()
        cur.close()
        return redirect('/')
    return render_template('add_income.html')

# Add Expense Route
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expenses (description, amount, category, date) VALUES (%s, %s, %s, %s)",
                    (description, amount, category, date))
        mysql.connection.commit()
        cur.close()
        return redirect('/view_expenses')
    return render_template('add_expense.html')

# View and Delete Expenses Route
@app.route('/view_expenses', methods=['GET', 'POST'])
def view_expenses():
    if request.method == 'POST':
        expense_id = request.form.get('expense_id')
        if expense_id:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM expenses WHERE id = %s", [expense_id])
            mysql.connection.commit()
            cur.close()
            return redirect('/view_expenses')

        income_id = request.form.get('income_id')
        if income_id:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM income WHERE id = %s", [income_id])
            mysql.connection.commit()
            cur.close()
            return redirect('/view_expenses')

    cur = mysql.connection.cursor()

    # Fetch all incomes
    cur.execute("SELECT * FROM income")
    incomes = cur.fetchall()

    # Fetch all expenses
    cur.execute("SELECT * FROM expenses")
    expenses = cur.fetchall()

    cur.close()
    
    net_balance = calculate_net_balance()
    return render_template('view_expenses.html', incomes=incomes, expenses=expenses, net_balance=net_balance)
if __name__ == '__main__':
    app.run(debug=True)
