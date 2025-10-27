'''
Basic CSV Reading and Writing API using Flask and Polars
'''
import logging
from functools import reduce
import operator
from flask import Flask, jsonify, request
import polars as pl


app = Flask(__name__)


# Configure loading of CSV files
logging.basicConfig(filename='output.log',
    filemode='a', #Append mode               
    level=logging.INFO,         
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CSV_PATH = "friends_data.csv"

#Load CSV files from Polars with lazy loading
def load_csv(file_path : str, attempts = 5) -> pl.DataFrame | None:
    '''
        Load CSV file using Polars with lazy loading for potentially larger files.
        Args:
            file_path (str): Path to the CSV file.

        Returns:
            pl.DataFrame: Loaded DataFrame or None if an error occurs.
    '''
    try:
        for attempt in range(attempts):
            logging.info("Attempt %d to load CSV file: %s", attempt + 1, file_path)
            df = pl.scan_csv(file_path).collect()
            logging.info("CSV file %s loaded successfully.", file_path)
            return df
    except (FileNotFoundError, pl.exceptions.NoDataError, pl.exceptions.ComputeError) as e:
        logging.error("Error loading CSV file %s: %s", file_path, e, exc_info=True)
        return None

# Sample data
items = load_csv(CSV_PATH)
#items = data_file.to_dicts() if data_file is not None else []

# Show Home page
@app.route("/", methods=["GET"])
def home_page():
    '''
        Home Page Route

        Returns:
            JSON response with a welcome message.
    '''
    return jsonify("Basic CSV Reading and Writing API using Flask")


# Get All Items


@app.route("/characters", methods=["GET"])
def get_characters():
    """
    Get paginated list of characters from the CSV file.
    Query Params:
        page (int): Page number (default=1)
        limit (int): Number of items per page (default=10)
    Returns:
        JSON list of character records with pagination metadata
    """
    # Parse query parameters
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    
    # Calculate offset
    offset = (page - 1) * limit

    # Load dataset using Polars

    # Get total records
    total_records = items.height
    total_pages = (total_records + limit - 1) // limit

    # Paginate
    paginated_df = items.slice(offset, limit)

    # Convert to list of dicts for JSON output
    characters = paginated_df.to_dicts()

    # Return with metadata
    return jsonify({
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_records": total_records,
        "data": characters
    })



# Get Specific Item
@app.route("/characters/search", methods=["GET"])
def get_character():
    """
    Search characters by first_name OR last_name (case-insensitive).

    Query Parameters:
        first_name (str, optional): Character's first name
        last_name  (str, optional): Character's last name

    Returns:
        JSON response with all matching characters or an error message.
    """
    try:
        first_name = request.args.get("first_name", "").strip().lower()
        last_name = request.args.get("last_name", "").strip().lower()

        if not first_name and not last_name:
            return jsonify({"error": "Please provide at least 'first_name' or 'last_name'."}), 400

        df = items

        # Build OR conditions
        conditions = []
        if first_name:
            conditions.append(pl.col("first_name").str.to_lowercase() == first_name)
        if last_name:
            conditions.append(pl.col("last_name").str.to_lowercase() == last_name)

        # Combine conditions with OR
        filtered = df.filter(reduce(operator.or_, conditions))

        if filtered.height == 0:
            return jsonify({"message": "No matching characters found"}), 404

        return jsonify(filtered.to_dicts()), 200

    except Exception as e:
        logging.exception("Error searching characters: %s", e)
        return jsonify({"error": str(e)}), 500


# Update existing Item
@app.route("/characters/<int:item_id>", methods=["PUT"])
def update_character(item_id):
    """
    Update an existing character in the CSV file.

    Args:
        item_id (int): ID of the character to update.
    Returns:
        JSON response with the updated character details or a not found message.
    """
    try:
        # Load the dataset
        global items

        # Ensure 'id' column is int for comparison
        items = items.with_columns(pl.col("id").cast(pl.Int64))

        # Parse the incoming JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Check if item exists
        if item_id not in items["id"].to_list():
            logging.error("Item with ID %d not found for update.", item_id)
            return jsonify({"message": "Item not found"}), 404

        # Update the row using Polars expressions
        for key, value in data.items():
            if key in items.columns and key != "id":  # never update the id
                items = items.with_columns(
                    pl.when(pl.col("id") == item_id)
                    .then(value)
                    .otherwise(pl.col(key))
                    .alias(key)
                )

        # Save changes back to CSV
        items.write_csv(CSV_PATH)

        # Get updated row as dictionary
        updated_row = items.filter(pl.col("id") == item_id).to_dicts()[0]

        logging.info("Item with ID %d updated successfully.", item_id)
        return jsonify(updated_row), 200

    except Exception as e:
        logging.exception("Error updating character: %s", e)
        return jsonify({"error": str(e)}), 500


# Delete Existing Item
@app.route("/characters/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    '''
        Delete an existing item from the processed CSV data.
        Args:
            item_id (int): ID of the item to delete.
        Returns:
            JSON response with a success or not found message.
    '''
    global items

    if item_id not in items["id"].to_list():
        logging.error("Item with ID %d not found for deletion.", item_id)
        return jsonify({"message": "Item not found"}), 404

    # Remove the row
    items = items.filter(pl.col("id") != item_id)

    # Save updated DataFrame to CSV
    items.write_csv(CSV_PATH)

    logging.info("Item with ID %d deleted successfully.", item_id)
    return jsonify({"message": "Item deleted successfully."}), 200


if __name__ == "__main__":
    #print("Items:", items)
    app.run(port=5002)