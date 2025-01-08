from flask import Flask, request, jsonify
import pandas as pd
from datetime import timedelta
from flask_cors import CORS


app = Flask(__name__)
CORS(app) 
# Load the dataset
file_path = 'zon.xlsx'

# Read the Excel file
try:
    data = pd.read_excel(file_path, sheet_name='Sheet1')
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    exit(1)

# Strip any leading/trailing whitespaces in the column names
data.columns = data.columns.str.strip()

# Rename the 'time' column to 'date' and 'customers' to 'customer'
data = data.rename(columns={
    'time': 'date',
    'customers': 'customer',
    'm_status': 'status'
})

# Handle missing or invalid date values
data['date'] = pd.to_datetime(data['date'], errors='coerce')  # Convert invalid dates to NaT
data = data.dropna(subset=['date'])  # Drop rows where 'date' is NaT

# Standardize and preprocess the data
data['year'] = data['date'].dt.year
data['month'] = data['date'].dt.month
data['quarter'] = data['date'].dt.quarter
data['quarterly'] = data['quarter'].apply(lambda x: f'q{x}')
data['day'] = data['date'].dt.day

# Zone Usage Endpoint
@app.route('/zone_usage', methods=['GET'])
def get_zone_usage():
    """API to get total usage grouped by zone and month."""
    zone_filter = request.args.get('zone', type=str)  # Get the zone filter from the request, optional
    filtered_data = data.copy()  # Create a copy to avoid modifying global data

    # Apply filter if zone is provided
    if zone_filter:
        filtered_data = filtered_data[filtered_data['zone'] == zone_filter]

    # Group by zone and month, then calculate total usage
    result = (
        filtered_data.groupby(['zone', 'year', 'month'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    # Convert the result to the required output format (list of dictionaries)
    result_list = result.to_dict(orient='records')

    return jsonify(result_list)

# Monthly Usage Endpoint
@app.route('/monthly_usage', methods=['GET'])
def get_monthly_data():
    """API to get data filtered by month, year, zone, customer, and daily usage."""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    zone = request.args.get('zone', type=str)  # Zone filter
    day = request.args.get('day', type=int)
    customer = request.args.get('customer', type=str)

    filtered_data = data.copy()  # Create a copy to avoid modifying global data

    # Apply filters
    if zone:
        filtered_data = filtered_data[filtered_data['zone'] == zone]
    if year:
        filtered_data = filtered_data[filtered_data['year'] == year]
    if month:
        filtered_data = filtered_data[filtered_data['month'] == month]
    if day:
        filtered_data = filtered_data[filtered_data['day'] == day]
    if customer:
        filtered_data = filtered_data[filtered_data['customer'] == customer]

    if filtered_data.empty:
        return jsonify([]), 200  # Return empty list instead of error

    required_columns = ['date', 'usage', 'zone', 'quarterly']
    missing_columns = [col for col in required_columns if col not in filtered_data.columns]
    if missing_columns:
        return jsonify({"error": f"Missing columns: {missing_columns}"}), 400

    # Format the 'date' column to 'Month, Year' (e.g., 'Apr, 2024')
    filtered_data['formatted_date'] = filtered_data['date'].dt.strftime('%b, %Y')

    # Group by the formatted date, zone, and quarterly, and sum the usage for each group
    result = (
        filtered_data.groupby(['formatted_date', 'zone', 'quarterly'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    # Convert the result to a list of dictionaries for JSON serialization
    result_list = result.to_dict(orient='records')

    return jsonify(result_list)  # Use result_list instead of the raw DataFrame
@app.route('/quarterly_usage', methods=['GET'])
def get_quarterly_usage_summary():
    """API to get total usage grouped by zone and quarterly usage summary."""
    zone_filter = request.args.get('zone', type=str)  # Get the zone filter from the request, optional

    filtered_data = data.copy()  # Create a copy to avoid modifying global data

    # Apply filter if zone is provided
    if zone_filter:
        filtered_data = filtered_data[filtered_data['zone'] == zone_filter]

    # Group by quarter and zone, then calculate total usage
    result = (
        filtered_data.groupby(['quarterly', 'zone'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    # Capitalize the 'quarterly' values to 'Q1', 'Q2', etc.
    result['quarterly'] = result['quarterly'].apply(lambda x: f"Q{x[1]}")

    # Convert the result to the required output format (list of dictionaries)
    result_list = result.to_dict(orient='records')

    return jsonify(result_list)


# Quarterly Usage Summary Endpoint (Modified to include zone filter)

#@app.route('/quarterl_usage', methods=['GET'])
#def get_quarterly_usage_summary():
 #   """API to get total usage grouped by zone and quarterly usage summary."""
  #  zone_filter = request.args.get('zone', type=str)  # Get the zone filter from the request, optional

   # filtered_data = data.copy()  # Create a copy to avoid modifying global data

    # Apply filter if zone is provided
    #if zone_filter:
     #   filtered_data = filtered_data[filtered_data['zone'] == zone_filter]

    # Group by quarter and zone, then calculate total usage
    #result = (
     #   filtered_data.groupby(['quarterly', 'zone'])['usage']
      #  .sum()
       # .reset_index()
        #.rename(columns={'usage': 'Total usage'})
    #)

    # Convert the result to the required output format (list of dictionaries)
    #result_list = result.to_dict(orient='records')

    #return jsonify(result_list)

# MStatus Endpoint (Modified for handling recent months filter)


# MStatus Endpoint (Modified for handling recent months filter)
@app.route('/api/mstatus', methods=['GET'])
def get_mstatus():
    """API to filter data by recent months and group by status and month-year."""
    months_param = request.args.get('months', '').strip()
    latest_date = data['date'].max()

    # Define the set of possible statuses
    possible_statuses = ["Normal", "Suspicious", "Faulty_HiFlow", "Faulty_Rev"]

    # Filter data based on the 'months' parameter
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
        filtered_data = data.copy()
    else:
        return jsonify({"error": "Invalid or missing 'months' parameter"}), 400

    if months_param:
        filtered_data = data[data['date'] >= start_date]

    # Drop rows with missing status
    filtered_data = filtered_data.dropna(subset=['status'])

    # Add a 'month_year' column for grouping by month and year
    filtered_data['month_year'] = filtered_data['date'].dt.to_period('M').astype(str)

    # Group data by status and month-year
    result = (
        filtered_data.groupby(['status', 'month_year'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'month_year': 'time'})
    )

    # Create a full result that includes all possible statuses for each month
    all_results = []
    for time in filtered_data['month_year'].unique():
        for status in possible_statuses:
            status_data = result[(result['time'] == time) & (result['status'] == status)]
            if status_data.empty:
                all_results.append({
                    "status": status,
                    "time": time,
                    "usage": 0
                })
            else:
                all_results.append(status_data.iloc[0].to_dict())

    return jsonify(all_results)
# First 6 Months Total Usage Endpoint
@app.route('/api/first_6_months_usage', methods=['GET'])
def get_first_6_months_usage():
    """API to get total usage for the first 6 months."""
    earliest_date = data['date'].min()  # Get the earliest date from the dataset

    # Filter for the first 6 months
    first_6_months_data = data[data['date'] < earliest_date + pd.DateOffset(months=6)]

    # Group by month and year, and calculate the total usage for the first 6 months
    result = (
        first_6_months_data.groupby(['year', 'month'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    result_list = result.to_dict(orient='records')

    return jsonify(result_list)

# Last 6 Months Total Usage Endpoint
@app.route('/api/last_6_months_usage', methods=['GET'])
def get_last_6_months_usage():
    """API to get total usage for the last 6 months."""
    latest_date = data['date'].max()  # Get the latest date from the dataset

    # Filter for the last 6 months
    last_6_months_data = data[data['date'] >= latest_date - pd.DateOffset(months=6)]

    # Group by month and year, and calculate the total usage for the last 6 months
    result = (
        last_6_months_data.groupby(['year', 'month'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    result_list = result.to_dict(orient='records')

    return jsonify(result_list)


@app.route('/flowchart', methods=['GET'])
def flowchart():
    """API to get total usage for the first and last 6 months combined."""

    # Get the earliest and latest dates from the dataset
    earliest_date = data['date'].min()
    latest_date = data['date'].max()

    # Filter for the first 6 months
    first_6_months_data = data[data['date'] < earliest_date + pd.DateOffset(months=6)]

    # Filter for the last 6 months
    last_6_months_data = data[data['date'] >= latest_date - pd.DateOffset(months=6)]

    # Group by month and year, and calculate the total usage for the first 6 months
    first_6_months_result = (
        first_6_months_data.groupby(['year', 'month'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    # Group by month and year, and calculate the total usage for the last 6 months
    last_6_months_result = (
        last_6_months_data.groupby(['year', 'month'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    # Function to safely format year and month into 'Month, Year'
    def safe_format_date(row):
        try:
            year = int(row['year'])
            month = int(row['month'])
            # Check if year and month are valid
            if 1 <= month <= 12:
                return pd.to_datetime(f'{year}-{month}-01').strftime('%b, %Y')
        except (ValueError, TypeError):
            return None  # Return None if invalid data
        return None

    # Apply the function to format the 'Date' column
    first_6_months_result['Date'] = first_6_months_result.apply(safe_format_date, axis=1)
    last_6_months_result['Date'] = last_6_months_result.apply(safe_format_date, axis=1)

    # Drop rows where 'Date' could not be parsed
    first_6_months_result = first_6_months_result.dropna(subset=['Date'])
    last_6_months_result = last_6_months_result.dropna(subset=['Date'])

    # Drop the 'year' and 'month' columns as they are no longer needed
    first_6_months_result = first_6_months_result.drop(columns=['year', 'month'])
    last_6_months_result = last_6_months_result.drop(columns=['year', 'month'])

    # Combine both results using pd.concat
    combined_result = {
        "first_6_months": first_6_months_result.to_dict(orient='records'),
        "last_6_months": last_6_months_result.to_dict(orient='records')
    }

    return jsonify(combined_result)

@app.route('/total_usages', methods=['GET'])
def get_total_usage():
    """
    API to get total usage summary grouped by zone, quarterly, and formatted_date.
    """
    # Get the filter parameters
    customer_filter = request.args.get('customer', type=str)
    zone_filter = request.args.get('zone', type=str)
    quarterly_filter = request.args.get('quarterly', type=str)

    filtered_data = data.copy()  # Create a copy to avoid modifying global data

    # Debug: Log the incoming customer filter
    print("Customer Filter Value:", customer_filter)

    # Apply filters if provided
    if customer_filter:
        filtered_data = filtered_data[
            filtered_data['customer'].str.lower() == customer_filter.lower()
        ]
    if zone_filter:
        filtered_data = filtered_data[filtered_data['zone'] == zone_filter]
    if quarterly_filter:
        filtered_data = filtered_data[filtered_data['quarterly'] == quarterly_filter]

    # Debug: Log the shape of the filtered data
    print("Filtered Data Shape:", filtered_data.shape)

    if filtered_data.empty:
        return jsonify([])  # Return empty list if no data matches the filters

    # Add 'formatted_date' column for grouping
    filtered_data['formatted_date'] = filtered_data['date'].dt.strftime('%b, %Y')

    # Group by zone, quarterly, and formatted_date, then sum the total usage
    grouped_data = (
        filtered_data.groupby(['zone', 'quarterly', 'formatted_date'])['usage']
        .sum()
        .reset_index()
        .rename(columns={'usage': 'Total usage'})
    )

    # Add a helper column to sort by the original datetime
    grouped_data['sort_date'] = pd.to_datetime(
        grouped_data['formatted_date'], format='%b, %Y'
    )

    # Sort by the helper datetime column
    sorted_data = grouped_data.sort_values(by='sort_date').drop(columns=['sort_date'])

    # Convert the result to a dictionary for API response
    result_list = sorted_data.to_dict(orient='records')

    return jsonify(result_list)


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
@app.route('/consumption_chart')
def consumption_chart():
    return jsonify(consumption_chart_data)

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
total_usage_chart_data=[
    {"type": "commercial", "percentage": 43},
    {"type": "domestic", "percentage": 57}

]
@app.route('/peek_time')
def peek_time():
    return jsonify(peek_time_chart_data)
@app.route('/total_usage')
def quartely_usage():
    return jsonify(total_usage_chart_data)

@app.route('/zones', methods=['GET'])
def get_zone_list():
    """API to get the list of unique zones."""
    zone_list = data['zone'].unique().tolist()
    return jsonify(zone_list)
@app.route('/customers', methods=['GET'])
def get_customer_list():
    """API to get the list of unique customers."""
    customer_list = data['customer'].unique().tolist()
    return jsonify(customer_list)


# Run the app
if __name__ == '__main__':
   app.run(debug=True,  host='0.0.0.0')
