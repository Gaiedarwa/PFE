from pymongo import MongoClient

# Function to connect to MongoDB
def connect_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["drax"]  # Database name
    return db

# Connect to MongoDB and get the collection
db = connect_mongo()  # Connect to MongoDB
cv_collection = db["similarities"]  # Define the collection for storing CV similarities
offers_collection = db["job_offers"]

# Suppression de l'index unique
try:
    offers_collection.drop_index("unique_offer")
    print("Index unique_offer supprimé avec succès.")
except Exception as e:
    print(f"Erreur lors de la suppression de l'index unique_offer : {e}")

# Check the connection to MongoDB
try:
    connect_mongo().client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Connection error: {e}")
