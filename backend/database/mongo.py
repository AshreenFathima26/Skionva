from pymongo import MongoClient

# Local MongoDB connection
client = MongoClient("mongodb://localhost:27017/")

# Database
db = client["skinova_db"]

# Collection for progress tracking
progress_collection = db["progress"]
