from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os


# Initialize the Flask app
app = Flask(__name__)
CORS(app)
# Load data from JSON file
data_file = "data.json"
def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

chart_data = load_data()

# Static data for consumption chart
consumption_chart_data = [
    {"year": 2024, "month": 1, "consumption": 121.235},
    {"year": 2024, "month": 2, "consumption": 109.762},
    {"year": 2024, "month": 3, "consumption": 150.24},
    {"year": 2024, "month": 4, "consumption": 144.208},
    {"year": 2024, "month": 5, "consumption": 158.066},
    {"year": 2024, "month": 6, "consumption": 177.928},
    {"year": 2024, "month": 7, "consumption": 200.989},
    {"year": 2024, "month": 8, "consumption": 198.18},
    {"year": 2024, "month": 9, "consumption": 144.125},
    {"year": 2024, "month": 10, "consumption": 146.889},
    {"year": 2024, "month": 11, "consumption": 144.461},
    {"year": 2024, "month": 12, "consumption": 113.606},
    {"year": 2023, "month": 10, "consumption": 145.707},
    {"year": 2023, "month": 11, "consumption": 144.461},
    {"year": 2023, "month": 12, "consumption": 113.606}
]

# Static data for total usuage

total_usage_chart_data=[
    {"type": "commercial", "percentage": 43},
    {"type": "domestic", "percentage": 57}

]

zone_usage_chart_data = [
    {"year": 2023, "month": 10, "usage": 66944.51748, "zone": "Khumbharwadi"},
    {"year": 2023, "month": 11, "usage": 45891.24478, "zone": "Khumbharwadi"},
    {"year": 2023, "month": 12, "usage": 54497.85709, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 1, "usage": 441779.7084, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 2, "usage": 432123.704, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 3, "usage": 43122.704, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 4, "usage": 43341.704, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 5, "usage": 42340.704, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 6, "usage": 53212.704, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 7, "usage": 54121.114, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 8, "usage": 46112.304, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 9, "usage": 34567.744, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 10, "usage": 62720.702, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 11, "usage": 473120.608, "zone": "Khumbharwadi"},
    {"year": 2024, "month": 12, "usage": 35120.704, "zone": "Khumbharwadi"}
]
flow_chart_data = [
    {"year": 2024, "month": 1, "usage": 121.235},
    {"year": 2024, "month": 2, "usage": 109.762},
    {"year": 2024, "month": 3, "usage": 150.24},
    {"year": 2024, "month": 4, "usage": 144.208},
    {"year": 2024, "month": 5, "usage": 158.066},
    {"year": 2024, "month": 6, "usage": 177.928},
    {"year": 2024, "month": 7, "usage": 200.989},
    {"year": 2024, "month": 8, "usage": 198.18},
    {"year": 2024, "month": 9, "usage": 144.125},
    {"year": 2024, "month": 10, "usage": 148.071},
    {"year": 2023, "month": 10, "usage": 145.707},
    {"year": 2023, "month": 11, "usage": 144.461},
    {"year": 2023, "month": 12, "usage": 113.606}
]




peek_time_chart_data = [
    {"year": 2024, "month": 1, "usage": 121.235},
    {"year": 2024, "month": 2, "usage": 109.762},
    {"year": 2024, "month": 3, "usage": 150.24},
    {"year": 2024, "month": 4, "usage": 144.208},
    {"year": 2024, "month": 5, "usage": 158.066},
    {"year": 2024, "month": 6, "usage": 177.928},
    {"year": 2024, "month": 7, "usage": 200.989},
    {"year": 2024, "month": 8, "usage": 198.18},
    {"year": 2024, "month": 9, "usage": 144.125},
    {"year": 2024, "month": 10, "usage": 148.071}
]  


Quartely_usage_chart_data = [
    {"year": 2024, "month": "Q1", "average": 141014.112},
    {"year": 2024, "month": "Q2", "average": 147745.563},
    {"year": 2024, "month": "Q3", "average": 159022.204},
    {"year": 2024, "month": "Q4", "average": 29386.847},
    {"year": 2023, "month": "Q4", "average": 179061.1945}

]
monthly_usage_chart_data = [
    {"year": 2023, "month": 10, "usage": 66944.51748},
    {"year": 2023, "month": 11, "usage": 45891.24478},
    {"year": 2023, "month": 12, "usage": 54497.85709},
    {"year": 2024, "month": 1, "usage": 441779.7084},
    {"year": 2024, "month": 2, "usage": 432123.704},
    {"year": 2024, "month": 3, "usage": 43122.704},
    {"year": 2024, "month": 4, "usage": 43341.704},
    {"year": 2024, "month": 5, "usage": 42340.704},
    {"year": 2024, "month": 6, "usage": 53212.704},
    {"year": 2024, "month": 7, "usage": 54121.114},
    {"year": 2024, "month": 8, "usage": 46112.304},
    {"year": 2024, "month": 9, "usage": 34567.744},
    {"year": 2024, "month": 10, "usage": 62720.702},
    {"year": 2024, "month": 11, "usage": 473120.608},
    {"year": 2024, "month": 12, "usage": 35120.704}
]

@app.route('/')
def index():
    return render_template('chart.html')

@app.route('/data')
def data():
    return jsonify(chart_data)

@app.route('/m_status', methods=['GET', 'POST'])
def m_status():
    if request.method == 'GET':
        return jsonify(chart_data)
    elif request.method == 'POST':
        new_entry = request.get_json()
        if "users" not in chart_data:
            chart_data["users"] = []
        chart_data["users"].append(new_entry)
        save_data(chart_data)
        return jsonify(new_entry), 201

@app.route('/consumption_chart')
def consumption_chart():
    return jsonify(consumption_chart_data)
@app.route('/total_usage')
def total_usage():
    return jsonify(total_usage_chart_data)
@app.route('/zone_usage')
def zone_usage():
    return jsonify(zone_usage_chart_data)
@app.route('/flow_chart')
def flow_chart():
    return jsonify(flow_chart_data)
@app.route('/peek_time')
def peek_time():
    return jsonify(peek_time_chart_data)
@app.route('/quartely_usage')
def quartely_usage():
    return jsonify(Quartely_usage_chart_data)
@app.route('/monthly_usage')
def monthly_usage():
    return jsonify(monthly_usage_chart_data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
