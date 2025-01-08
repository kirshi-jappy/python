from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Load the Excel file
data_file = "customer.xlsx"
excel_data = pd.read_excel(data_file)

data = pd.read_excel(data_file)

# Convert read_date_time to datetime format
data['read_date_time'] = pd.to_datetime(data['read_date_time'])

# Define a function to calculate quarterly usage for a single customer
def calculate_quarterly_usage(customer_name):
    # Filter data for the given customer
    customer_data = data[data['cons_name'] == customer_name]

    if customer_data.empty:
        return None

    # Add a column for the quarter (convert Period to string with space between year and quarter)
    customer_data['quarter'] = customer_data['read_date_time'].dt.to_period('Q').astype(str).replace(r'(\d{4})Q(\d)', r'\1 Q\2', regex=True)

    # Group by quarter and calculate total usage
    quarterly_usage = customer_data.groupby('quarter')['Reading'].sum().to_dict()

    # Calculate total usage
    total_usage = customer_data['Reading'].sum()

    return {
        "total_usage": total_usage,
        "quarterly_usage": quarterly_usage
    }

# Define a function to calculate quarterly usage for all customers
def calculate_all_quarterly_usage():
    # Add a column for the quarter (convert Period to string with space between year and quarter)
    excel_data['quarter'] = excel_data['read_date_time'].dt.to_period('Q').astype(str).replace(r'(\d{4})Q(\d)', r'\1 Q\2', regex=True)

    # Group by customer name and quarter, then calculate total usage
    grouped_data = excel_data.groupby(['cons_name', 'quarter'])['Reading'].sum().reset_index()

    # Convert to a structured JSON-like format
    result = {}
    for _, row in grouped_data.iterrows():
        customer_name = row['cons_name']
        quarter = row['quarter']  # Already formatted with space
        reading = row['Reading']

        if customer_name not in result:
            result[customer_name] = {}
        result[customer_name][quarter] = reading

    return result

@app.route('/get-usage', methods=['GET'])
def get_usage():
    customer_name = request.args.get('customer_name')
    if not customer_name:
        return jsonify({"error": "Please provide a customer_name parameter."}), 400

    # Filter customer names that start with the given prefix
    matching_customers = excel_data[data['cons_name'].str.startswith(customer_name, na=False)]

    if matching_customers.empty:
        return jsonify({"error": f"No customers found starting with '{customer_name}'"}), 404

    # Process each matching customer and return results
    result = {}
    for customer in matching_customers['cons_name'].unique():
        result[customer] = calculate_quarterly_usage(customer)

    return jsonify(result)
@app.route('/get-yearly-and-quarterly-usage', methods=['GET'])
def get_yearly_and_quarterly_usage():
    # Ensure 'excel_data' is a DataFrame and not overwritten
    if isinstance(excel_data, pd.DataFrame):  # Check if 'excel_data' is indeed a DataFrame
        # Initialize the dictionary to store yearly and quarterly usage totals
        yearly_and_quarterly_usage = {}

        # Iterate through all data and aggregate the usage by year and quarter
        for _, row in excel_data.iterrows():
            year = row['read_date_time'].year
            quarter = row['read_date_time'].quarter  # Extract the quarter (1-4)

            # Create a dictionary for the year if not already present
            if year not in yearly_and_quarterly_usage:
                yearly_and_quarterly_usage[year] = {
                    "Q1": 0,
                    "Q2": 0,
                    "Q3": 0,
                    "Q4": 0
                }

            # Add the reading to the correct quarter
            quarter_label = f"Q{quarter}"
            yearly_and_quarterly_usage[year][quarter_label] += row['Reading']

        # Return the yearly and quarterly usage totals
        return jsonify(yearly_and_quarterly_usage)
    else:
        return jsonify({"error": "Excel data is not properly loaded."}), 500

@app.route('/get-all-usage', methods=['GET'])
def get_all_usage():
    result = calculate_all_quarterly_usage()
    return jsonify(result)
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
file_path = "book3.xlsx"
data = pd.read_excel(file_path)

# Process the data
data['read_date_time'] = pd.to_datetime(data['read_date_time'])
data['year-month'] = data['read_date_time'].dt.to_period('M').astype(str)



@app.route('/usage', methods=['GET'])
def usage():
    # Debugging: Print the first few rows of the data
    print("First few rows of data:")
    print(data.head())  # Inspect the first few rows to see the data structure

    # Optional filters
    year_month = request.args.get('year-month')
    m_status = request.args.get('m_status')

    # Start with the full data
    filtered_data = data

    # Step 1: Exclude October 2023 data
    print("Unique year-month values:", filtered_data['year-month'].unique())  # Check unique values of 'year-month'
    filtered_data = filtered_data[filtered_data['year-month'] != '2023-10']

    # Debugging: Print the data after excluding October to see if any data remains
    print("Data after excluding October 2023:")
    print(filtered_data.head())  # Show first few rows after filtering

    # Step 2: Apply year-month filter if provided
    if year_month:
        print(f"Applying filter for year-month: {year_month}")
        filtered_data = filtered_data[filtered_data['year-month'] == year_month]
        print("Filtered data for year-month {year_month}:")
        print(filtered_data.head())

    # Step 3: Apply m_status filter if provided
    if m_status:
        print(f"Applying filter for m_status: {m_status}")
        filtered_data = filtered_data[filtered_data['m_status'] == m_status]
        print("Filtered data for m_status {m_status}:")
        print(filtered_data.head())

    # Grouping and aggregating data
    grouped_data = (
        filtered_data.groupby(['year-month', 'm_status'])['Reading']
        .sum()
        .reset_index()
        .rename(columns={'Reading': 'total_usage'})
    )

    # Return the response
    return jsonify(grouped_data.to_dict(orient='records'))

@app.route('/consumption_chart')
def consumption_chart():
    return jsonify(consumption_chart_data)
@app.route('/total_usage')
def total_usage():
    return jsonify(total_usage_chart_data)
@app.route('/zone_usage', methods=['GET'])
def zone_usage():
    zone = request.args.get('zone')
    if zone:
        filtered_data = [entry for entry in zone_usage_chart_data if entry['zone'] == zone]
    else:
        filtered_data = zone_usage_chart_data
    return jsonify(filtered_data)
# New endpoint to get list of available zones
@app.route('/zones', methods=['GET'])
def get_zones():
    # Extract all unique zones from the data
    zones = set(entry['zone'] for entry in zone_usage_chart_data)
    return jsonify(list(zones))

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

 data_file = 'zon.xlsx'
 data = pd.read_excel(data_file)

# Renaming columns early in the code
data = data.rename(columns={
    'read_date_time': 'date',
    'Reading': 'usage',
    'Prop_zone': 'zone',  # Check if 'Prop_zone' exists in the data, adjust accordingly
    'cutomer': 'customer'  # Ensure the correct name for 'customer' column
})

# Ensure date column is in datetime format
data['date'] = pd.to_datetime(data['date'])

# Add additional date-based columns
data['year'] = data['date'].dt.year
data['month'] = data['date'].dt.month
data['quarter'] = data['date'].dt.quarter
data['quarterly'] = data['quarter'].apply(lambda x: f'q{x}')
data['day'] = data['date'].dt.day

# Verify column names for debugging (optional)
print(data.columns)
@app.route('/api/monthly', methods=['GET'])
def get_monthly_data():
    """API to get data filtered by month, year, zone, customer, and daily usage."""
    # Get query parameters from the request
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    zone = request.args.get('zone', type=str)
    day = request.args.get('day', type=int)
    customer = request.args.get('customer', type=str)

    # Start with the entire dataset
    filtered_data = data

    # Apply filters one by one
    if year:
        filtered_data = filtered_data[filtered_data['year'] == year]
    if month:
        filtered_data = filtered_data[filtered_data['month'] == month]
    if zone:
        filtered_data = filtered_data[filtered_data['zone'] == zone]
    if day:
        filtered_data = filtered_data[filtered_data['day'] == day]
    if customer:
        filtered_data = filtered_data[filtered_data['customer'] == customer]

    # Debugging: Check filtered_data before accessing specific columns
    print(f"Filtered data shape: {filtered_data.shape}")
    print(filtered_data.head())

    if filtered_data.empty:
        return jsonify({"error": "No data found for the given filters"}), 404

    # Check if the required columns exist in the filtered DataFrame
    required_columns = ['date', 'usage', 'zone', 'customer', 'quarterly']
    missing_columns = [col for col in required_columns if col not in filtered_data.columns]
    if missing_columns:
        return jsonify({"error": f"Missing columns: {missing_columns}"}), 400

    # Convert the filtered data to a list of dictionaries
    result = filtered_data[required_columns].to_dict(orient='records')

    # Return the filtered data as a JSON response
    return jsonify(result)


@app.route('/api/quarterly', methods=['GET'])
def get_quarterly_data():
    """API to get data filtered by quarter, zone, customer, and optionally daily usage."""
    year = request.args.get('year', type=int)
    quarter = request.args.get('quarter', type=int)
    zone = request.args.get('zone', type=str)
    day = request.args.get('day', type=int)
    min_usage = request.args.get('min_usage', type=float)
    max_usage = request.args.get('max_usage', type=float)
    customer = request.args.get('customer', type=str)

    # Filter data
    filtered_data = data
    if year:
        filtered_data = filtered_data[filtered_data['year'] == year]
    if quarter:
        filtered_data = filtered_data[filtered_data['quarter'] == quarter]
    if zone:
        filtered_data = filtered_data[filtered_data['zone'] == zone]
    if day:
        filtered_data = filtered_data[filtered_data['day'] == day]
    if min_usage is not None:
        filtered_data = filtered_data[filtered_data['usage'] >= min_usage]
    if max_usage is not None:
        filtered_data = filtered_data[filtered_data['usage'] <= max_usage]
    if customer:
        filtered_data = filtered_data[filtered_data['customer'] == customer]

    result = filtered_data[['date', 'usage', 'zone', 'customer', 'quarterly']].to_dict(orient='records')
    return jsonify(result)

@app.route('/api/total-usage', methods=['GET'])
def get_total_usage():
    """API to get total usage filtered by multiple quarters, zone, and customer."""
    year = request.args.get('year', type=int)
    quarters = request.args.getlist('quarter', type=int)
    zone = request.args.get('zone', type=str)
    customer = request.args.get('customer', type=str)

    # Filter data
    filtered_data = data
    if year:
        filtered_data = filtered_data[filtered_data['year'] == year]
    if quarters:
        filtered_data = filtered_data[filtered_data['quarter'].isin(quarters)]
    if zone:
        filtered_data = filtered_data[filtered_data['zone'] == zone]
    if customer:
        filtered_data = filtered_data[filtered_data['customer'] == customer]

    total_usage = filtered_data['usage'].sum()
    return jsonify({"total_usage": total_usage})

@app.route('/api/quarterly-total', methods=['GET'])
def get_quarterly_total():
    """API to get total usage for a specific quarter, month, year, and customer."""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    quarter = request.args.get('quarter', type=str)  # e.g., 'q1', 'q2'
    customer = request.args.get('customer', type=str)

    # Filter data
    filtered_data = data
    if year:
        filtered_data = filtered_data[filtered_data['year'] == year]
    if month:
        filtered_data = filtered_data[filtered_data['month'] == month]
    if quarter:
        filtered_data = filtered_data[filtered_data['quarterly'] == quarter]
    if customer:
        filtered_data = filtered_data[filtered_data['customer'] == customer]

    total_usage = filtered_data['usage'].sum()
    return jsonify({"quarterly": quarter, "total_usage": total_usage, "year": year, "month": month})

@app.route('/api/total-by-quarter', methods=['GET'])
def get_total_by_quarter():
    """API to get total usage for all quarters (Q1, Q2, Q3, Q4) grouped by year."""

    # Group data by year and quarter
    grouped_data = data.groupby(['year', 'quarter'])['usage'].sum().reset_index()

    # Prepare the result
    result = {}
    for year in grouped_data['year'].unique():
        year_data = grouped_data[grouped_data['year'] == year]
        result[int(year)] = {  # Convert year to int if it's a numpy int64
            f"total_q{int(row['quarter'])}": row['usage'] for _, row in year_data.iterrows()
        }

        return jsonify({"totals": result})
file_path = 'book3.xlsx'
data = pd.read_excel(file_path, sheet_name='Sheet1')
data['read_date_time'] = pd.to_datetime(data['read_date_time'])  # Ensure the date column is in datetime format

@app.route('/api/mstatus', methods=['GET'])
def get_mstatus():
    # Get the filter parameter
    months_param = request.args.get('months', '').strip()
    logging.debug(f"Received months parameter: {months_param}")

    # Get the latest available date from the data
    latest_date = data['read_date_time'].max()

    # Calculate date range based on the parameter
    if months_param == 'last3months':
        start_date = latest_date - timedelta(days=90)
    elif months_param == 'lastmonth':
        start_date = latest_date - timedelta(days=30)
    elif months_param == 'last10days':
        start_date = latest_date - timedelta(days=10)
    elif months_param == 'last10months':
        start_date = latest_date - timedelta(days=300)
    elif months_param == 'last6months':
        start_date = latest_date - timedelta(days=180)
    elif months_param == '':
        # No parameter provided; use all data
        filtered_data = data
        logging.debug("No filter applied; returning all data.")
    else:
        logging.error("Invalid or missing 'months' parameter")
        return jsonify({"error": "Invalid or missing 'months' parameter"}), 400

    # If a filter exists, apply it
    if months_param:
        filtered_data = data[data['read_date_time'] >= start_date]

    # Group by 'm_status' and month, calculate total usage
    filtered_data['month_year'] = filtered_data['read_date_time'].dt.to_period('M').astype(str)
    result = (
        filtered_data
        .groupby(['m_status', 'month_year'])['Reading']
        .sum()
        .reset_index()
        .rename(columns={'month_year': 'time'})
    )

    # Convert the result to JSON format
    result_json = result.to_dict(orient='records')
    return jsonify(result_json)
if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0')

