from pymongo import MongoClient

# ---------------- MONGODB CONNECTION ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["crop_project"]
users_collection = db["users"]


# ---------------- CREATE USER (REGISTER) ----------------
def register_user(username, password):

    existing_user = users_collection.find_one({"username": username})

    if existing_user:
        return False

    users_collection.insert_one({
        "username": username,
        "password": password
    })

    return True


# ---------------- LOGIN USER ----------------
def login_user(username, password):

    user = users_collection.find_one({
        "username": username,
        "password": password
    })

    return user