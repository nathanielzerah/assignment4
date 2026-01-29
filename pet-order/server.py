import os
import uuid
import random
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo-order:27017")
client = MongoClient(MONGO_URI)
db = client.get_database("petorder_db")
transactions_col = db["transactions"]

PETSTORE1_URL = os.getenv("PETSTORE1_URL", "http://pet-store1:8000")
PETSTORE2_URL = os.getenv("PETSTORE2_URL", "http://pet-store2:8000")

OWNER_HEADER_VALUE = "LovesPetsL2M3n4"
NINJA_API_KEY = os.environ.get("NINJA_API_KEY", "no-key-set")

def get_headers():
    return {"X-API-KEY": NINJA_API_KEY}

def find_pet_type_id(base_url, pet_type):
    try:
        resp = requests.get(f"{base_url}/pet-types", params={"type": pet_type}, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                return data[0]['id']
    except:
        pass
    return None

def list_pets(base_url, type_id):
    try:
        resp = requests.get(f"{base_url}/pet-types/{type_id}/pets", timeout=2)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def delete_pet(base_url, type_id, name):
    try:
        requests.delete(f"{base_url}/pet-types/{type_id}/pets/{name}", headers=get_headers(), timeout=2)
    except:
        pass

@app.route('/purchases', methods=['POST'])
def purchase():
    data = request.get_json()
    if not data: 
        return jsonify({"error": "No data"}), 400
    
    purchaser = data.get("purchaser")
    pet_type = data.get("pet-type")
    store_req = data.get("store")
    pet_name_req = data.get("pet-name")

    if not purchaser or not pet_type:
        return jsonify({"error": "Missing fields"}), 400

    candidates = []

    if store_req is None or store_req == 1:
        tid = find_pet_type_id(PETSTORE1_URL, pet_type)
        if tid:
            pets = list_pets(PETSTORE1_URL, tid)
            for p in pets:
                if pet_name_req and p['name'] != pet_name_req: continue
                candidates.append((PETSTORE1_URL, 1, tid, p['name']))

    if store_req is None or store_req == 2:
        tid = find_pet_type_id(PETSTORE2_URL, pet_type)
        if tid:
            pets = list_pets(PETSTORE2_URL, tid)
            for p in pets:
                if pet_name_req and p['name'] != pet_name_req: continue
                candidates.append((PETSTORE2_URL, 2, tid, p['name']))

    if not candidates:
        return jsonify({"error": "Pet not found"}), 400

    chosen = random.choice(candidates)
    url, store_num, tid, pname = chosen

    delete_pet(url, tid, pname)
    
    purchase_id = str(uuid.uuid4())
    record = {
        "id": purchase_id,
        "purchase-id": purchase_id,
        "purchaser": purchaser,
        "pet-type": pet_type,
        "store": store_num,
        "pet-name": pname
    }
    transactions_col.insert_one(record)
    
    record.pop('_id', None)
    record.pop('id', None)
    return jsonify(record), 201

@app.route('/transactions', methods=['GET'])
def get_transactions():
    if request.headers.get("OwnerPC") != OWNER_HEADER_VALUE:
        return jsonify({"error": "Unauthorized"}), 401
    
    query = {}
    if request.args.get("store"): query["store"] = int(request.args.get("store"))
    if request.args.get("pet-type"): query["pet-type"] = request.args.get("pet-type")
    if request.args.get("purchaser"): query["purchaser"] = request.args.get("purchaser")

    results = []
    for doc in transactions_col.find(query):
        doc.pop('_id', None)
        if 'purchase-id' not in doc and 'id' in doc:
            doc['purchase-id'] = doc['id']
            doc.pop('id', None)
        results.append(doc)
    return jsonify(results), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)