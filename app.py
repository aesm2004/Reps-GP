from flask import Flask, jsonify, request, render_template
import pyodbc, os
from werkzeug.middleware.dispatcher import DispatcherMiddleware

DEBUG_MODE = False
# --- DEBUG_MODE = False  # Set to False for production

# --- Database connection ---
DB_SERVER = os.environ.get('DB_SERVER', 'BC-SQL\\SAGE200')
DB_NAME = os.environ.get('DB_NAME', 'CRMCompanyList')
DB_USER = os.environ.get('DB_USER', 'sa')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'SD8gW0JfqV')

connection_string = (
    f'DRIVER={{SQL Server}};'
    f'SERVER={DB_SERVER};'
    f'DATABASE={DB_NAME};'
    f'UID={DB_USER};'
    f'PWD={DB_PASSWORD};'
)

# --- Flask app ---
app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/RepsGP/static'
)
app.config['APPLICATION_ROOT'] = '/RepsGP'

# --- CORS headers ---
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/salesdata')
def get_sales_data():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    rep_status = request.args.get('rep')
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("EXEC FinanceModule_RepGPReport_Date_Range ?, ?, ?", rep_status, start_date, end_date)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics')
@app.route('/analytics.html')
def analytics():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    rep_status = request.args.get('rep')
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("EXEC FinanceModule_RepGPReport_Date_Range ?, ?, ?", rep_status, start_date, end_date)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return render_template('analytics.html', data=results, columns=columns)
    except Exception as e:
        return render_template('analytics.html', data=[], columns=[], error=str(e))

# --- WSGI callable for IIS ---
if not DEBUG_MODE:
    application = DispatcherMiddleware(None, {'/RepsGP': app})


# --- Local development ---
if __name__ == '__main__' or DEBUG_MODE:
    print("Running Flask in local debug mode on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

    # Access via http://localhost:5000/RepsGP/