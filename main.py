'''
Basic CSV Reading and Writing API using Flask and Polars
'''
import logging
from flask import Flask, jsonify, request
import polars as pl


app = Flask(__name__)


# Configure loading of CSV files
logging.basicConfig(level=logging.INFO)

#Load CSV files from Polars with lazy loading
def load_csv(file_path : str) -> pl.DataFrame | None:
    '''
        Load CSV file using Polars with lazy loading for potentially larger files.
        Args:
            file_path (str): Path to the CSV file.

        Returns:
            pl.DataFrame: Loaded DataFrame or None if an error occurs.
    '''
    try:
        df = pl.scan_csv(file_path).collect()
        logging.info("CSV file %s loaded successfully.", file_path)
        return df
    except (FileNotFoundError, pl.exceptions.NoDataError, pl.exceptions.ComputeError) as e:
        logging.error("Error loading CSV file %s: %s", file_path, e, exc_info=True)
        return None

# Sample data
items = load_csv("friends_data.csv")
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


@app.route("/items", methods=["GET"])
def get_items():
    '''
        Retrieve all items from the processed CSV data.

        Returns:
            JSON response with a list of all items.
    '''
    return jsonify(items)


# Get Specific Item
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    '''
        Retrieve a specific item by ID from the processed CSV data.

        Args:
            item_id (int): ID of the item to retrieve.
        Returns:
            JSON response with the item details or a not found message.
    '''
    # Using Python Generator and Iterator (next)
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"message": "Item not found"}), 404


# Create a new Item
@app.route("/items", methods=["POST"])
def create_item():
    '''
        Create a new item and add it to the processed CSV data.
        
        Returns:
            JSON response with the created item details.
    '''
    data = request.get_json()
    new_item = {"id": len(items) + 1, "name": data["name"]}
    items.append(new_item)
    return jsonify(new_item), 201


# Update existing Item
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    '''
        Update an existing item in the processed CSV data.
        Args:
            item_id (int): ID of the item to update.
        Returns:
            JSON response with the updated item details or a not found message.
    '''
    data = request.get_json()
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        item["name"] = data["name"]
        return jsonify(item)
    return jsonify({"message": "Item not found"}), 404


# Delete Existing Item
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    '''
        Delete an existing item from the processed CSV data.
        Args:
            item_id (int): ID of the item to delete.
        Returns:
            JSON response with a success or not found message.
    '''
    global items
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        items = [i for i in items if i["id"] != item_id]
        return jsonify({"message": "Item deleted"})
    return jsonify({"message": "Item not found"}), 404


if __name__ == "__main__":
    #print("Items:", items)
    app.run(port=5002)