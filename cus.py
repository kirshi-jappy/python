from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the Excel file
data_file = "customer.xlsx"
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
    data['quarter'] = data['read_date_time'].dt.to_period('Q').astype(str).replace(r'(\d{4})Q(\d)', r'\1 Q\2', regex=True)

    # Group by customer name and quarter, then calculate total usage
    grouped_data = data.groupby(['cons_name', 'quarter'])['Reading'].sum().reset_index()

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
    matching_customers = data[data['cons_name'].str.startswith(customer_name, na=False)]

    if matching_customers.empty:
        return jsonify({"error": f"No customers found starting with '{customer_name}'"}), 404

    # Process each matching customer and return results
    result = {}
    for customer in matching_customers['cons_name'].unique():
        result[customer] = calculate_quarterly_usage(customer)

    return jsonify(result)

@app.route('/get-all-usage', methods=['GET'])
def get_all_usage():
    result = calculate_all_quarterly_usage()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

