# 🧩 Basic CSV Reading and Writing API (Flask + Polars)

This project provides a simple REST API for reading, updating, and deleting entries in a CSV file using **Flask** and **Polars**.  
It is designed to serve and modify structured character data such as the *Friends* dataset.

---

## ⚙️ Setup

### 1. Install Dependencies

Make sure you have Python 3.10+ and install the required packages:

```bash
uv sync
```

By default, the server runs at:
```bash
http://127.0.0.1:5002
```
🔹 Step 1: Open Thunder Client

Install Thunder Client from the VS Code Extensions Marketplace.

Open the Thunder Client tab in the sidebar.

Create a new collection called Friends API.

🔹 Step 2: Home Page Test

Request:

Method: GET
```bash
URL: http://127.0.0.1:5002/
```
Expected Response:
```bash
"Basic CSV Reading and Writing API using Flask"
```
🔹 Step 3: Retrieve All Characters

Request:

Method: GET
```bash
URL: http://127.0.0.1:5002/characters
```
Expected Response:
```bash
[
  {
    "id": 1,
    "first_name": "Rachel",
    "last_name": "Green",
    ...
  },
  ...
]
```

If you see "No data available", make sure your CSV file exists and matches the schema above.

🔹 Step 4: Retrieve a Character by ID

Request:

Method: GET
```bash
URL: http://127.0.0.1:5002/characters/3
```

Expected Response:
```bash
{
  "id": 3,
  "first_name": "Chandler",
  "last_name": "Bing",
  "city": "New York",
  ...
}
```

If not found:
```bash
{"message": "Item not found"}
```
🔹 Step 5: Update a Character

Request:

Method: PUT
```bash
URL: http://127.0.0.1:5002/characters/3
```
Headers:
Content-Type: application/json

Body (JSON):
```bash
{
  "city": "New York",
  "catchphrase": "Could I *be* wearing any more clothes?",
  "screen_time_minutes": 655
}
```

Expected Response:
```bash
{
  "id": 3,
  "first_name": "Chandler",
  "last_name": "Bing",
  "city": "New York",
  "catchphrase": "Could I *be* wearing any more clothes?",
  "screen_time_minutes": 655,
  ...
}
```

The corresponding CSV line should update automatically.

🔹 Step 6: Delete a Character

Request:

Method: DELETE
```bash
URL: http://127.0.0.1:5002/characters/3
```
Expected Response:
```bash
{"message": "Item deleted successfully."}
```

If the record doesn’t exist:
```bash
{"message": "Item not found"}
```