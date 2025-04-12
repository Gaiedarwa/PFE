from pymongo import MongoClient

# Function to connect to MongoDB
def connect_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["drax"]  # Database name
    return db

# Connect to MongoDB and get the collection
db = connect_mongo()  # Connect to MongoDB
cv_collection = db["similarities"]  # Define the collection for storing CV similarities

# Check the connection to MongoDB
try:
    connect_mongo().client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Connection error: {e}")
