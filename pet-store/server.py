import os
from flask import Flask, request, jsonify
from db import pettypes, pets, STORE_ID
from bson.objectid import ObjectId

app = Flask(__name__)

NINJA_API_KEY = os.environ.get("NINJA_API_KEY", "no-key-set")

def check_api_key():
    key = request.headers.get("X-API-KEY")
    return key == NINJA_API_KEY

ENRICHMENT_DATA = {
    "Golden Retriever": {
        "family": "Canidae",
        "genus": "Canis",
        "attributes": [],
        "lifespan": 12
    },
    "Australian Shepherd": {
        "family": "Canidae",
        "genus": "Canis",
        "attributes": ["Loyal", "outgoing", "and", "friendly"],
        "lifespan": 15
    },
    "Abyssinian": {
        "family": "Felidae",
        "genus": "Felis",
        "attributes": ["Intelligent", "and", "curious"],
        "lifespan": 13
    },
    "bulldog": {
        "family": "Canidae",
        "genus": "Canis",
        "attributes": ["Gentle", "calm", "and", "affectionate"],
        "lifespan": None
    }
}

@app.route('/pet-types', methods=['POST'])
def create_pet_type():
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if not data or 'type' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    type_name = data['type']
    
    if pettypes.find_one({"type": type_name}):
        return jsonify({"error": "Type already exists"}), 400

    if type_name in ENRICHMENT_DATA:
        defaults = ENRICHMENT_DATA[type_name]
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
    else:
        if "family" not in data: data["family"] = "Unknown"
        if "genus" not in data: data["genus"] = "Unknown"
        if "attributes" not in data: data["attributes"] = []
        if "lifespan" not in data: data["lifespan"] = None

    new_id = str(pettypes.insert_one(data).inserted_id)
    data['id'] = new_id
    data.pop('_id', None)
    
    return jsonify(data), 201

@app.route('/pet-types', methods=['GET'])
def get_pet_types():
    query_filter = {}
    for key, value in request.args.items():
        if key == 'id':
            try:
                query_filter['_id'] = ObjectId(value)
            except:
                return jsonify([]), 200
        else:
            query_filter[key] = value

    results = []
    for doc in pettypes.find(query_filter):
        doc['id'] = str(doc['_id'])
        del doc['_id']
        results.append(doc)
    return jsonify(results), 200

@app.route('/pet-types/<type_id>', methods=['DELETE'])
def delete_pet_type(type_id):
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        res = pettypes.delete_one({"_id": ObjectId(type_id)})
        if res.deleted_count == 0:
            return jsonify({"error": "Not found"}), 404
        pets.delete_many({"type_id": type_id})
        return jsonify({"message": "Deleted"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400

@app.route('/pet-types/<type_id>/pets', methods=['POST'])
def add_pet(type_id):
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        if not pettypes.find_one({"_id": ObjectId(type_id)}):
            return jsonify({"error": "Pet type not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 404

    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    data['type_id'] = type_id
    new_id = str(pets.insert_one(data).inserted_id)
    return jsonify({"id": new_id, "message": "Pet added"}), 201

@app.route('/pet-types/<type_id>/pets', methods=['GET'])
def get_pets(type_id):
    results = []
    for doc in pets.find({"type_id": type_id}):
        doc['id'] = str(doc['_id'])
        del doc['_id']
        results.append(doc)
    return jsonify(results), 200

@app.route('/pet-types/<type_id>/pets/<pet_name>', methods=['GET'])
def get_pet_by_name(type_id, pet_name):
    doc = pets.find_one({"type_id": type_id, "name": pet_name})
    if not doc:
        return jsonify({"error": "Pet not found"}), 404
    doc['id'] = str(doc['_id'])
    del doc['_id']
    return jsonify(doc), 200

@app.route('/pet-types/<type_id>/pets/<pet_name>', methods=['DELETE'])
def delete_pet_by_name(type_id, pet_name):
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    res = pets.delete_one({"type_id": type_id, "name": pet_name})
    if res.deleted_count == 0:
        return jsonify({"error": "Pet not found"}), 404
    return jsonify({"message": "Deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)