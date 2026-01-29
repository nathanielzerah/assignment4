import requests
import json
import sys

STORE1_URL = "http://localhost:5001"
STORE2_URL = "http://localhost:5002"
ORDER_URL = "http://localhost:5003"

API_KEY = "key"
HEADERS = {"X-API-KEY": API_KEY}

SETUP_DATA = {
    "types_store1": [
        {"type": "Golden Retriever", "family": "Canidae", "genus": "Canis", "lifespan": 12},
        {"type": "Australian Shepherd", "family": "Canidae", "genus": "Canis", "lifespan": 15, "attributes": ["Loyal", "outgoing", "and", "friendly"]},
        {"type": "Abyssinian", "family": "Felidae", "genus": "Felis", "lifespan": 13, "attributes": ["Intelligent", "and", "curious"]}
    ],
    "types_store2": [
        {"type": "Golden Retriever"},
        {"type": "Australian Shepherd"},
        {"type": "bulldog", "family": "Canidae", "genus": "Canis", "lifespan": None, "attributes": ["Gentle", "calm", "and", "affectionate"]}
    ]
}

ids = {}

def run_setup():
    print("Running Setup...")
    ids["id_1"] = requests.post(f"{STORE1_URL}/pet-types", json=SETUP_DATA["types_store1"][0], headers=HEADERS).json()["id"]
    ids["id_2"] = requests.post(f"{STORE1_URL}/pet-types", json=SETUP_DATA["types_store1"][1], headers=HEADERS).json()["id"]
    ids["id_3"] = requests.post(f"{STORE1_URL}/pet-types", json=SETUP_DATA["types_store1"][2], headers=HEADERS).json()["id"]

    ids["id_4"] = requests.post(f"{STORE2_URL}/pet-types", json=SETUP_DATA["types_store2"][0], headers=HEADERS).json()["id"]
    ids["id_5"] = requests.post(f"{STORE2_URL}/pet-types", json=SETUP_DATA["types_store2"][1], headers=HEADERS).json()["id"]
    ids["id_6"] = requests.post(f"{STORE2_URL}/pet-types", json=SETUP_DATA["types_store2"][2], headers=HEADERS).json()["id"]

    requests.post(f"{STORE1_URL}/pet-types/{ids['id_1']}/pets", json={"name": "Lander", "birthdate": "14-05-2020"}, headers=HEADERS)
    requests.post(f"{STORE1_URL}/pet-types/{ids['id_1']}/pets", json={"name": "Lanky"}, headers=HEADERS)

    requests.post(f"{STORE1_URL}/pet-types/{ids['id_3']}/pets", json={"name": "Muscles"}, headers=HEADERS)
    requests.post(f"{STORE1_URL}/pet-types/{ids['id_3']}/pets", json={"name": "Junior"}, headers=HEADERS)

    requests.post(f"{STORE2_URL}/pet-types/{ids['id_4']}/pets", json={"name": "Shelly", "birthdate": "07-07-2019"}, headers=HEADERS)

    requests.post(f"{STORE2_URL}/pet-types/{ids['id_5']}/pets", json={"name": "Felicity", "birthdate": "11-27-2011"}, headers=HEADERS)

    requests.post(f"{STORE2_URL}/pet-types/{ids['id_6']}/pets", json={"name": "Lazy", "birthdate": "08-07-2018"}, headers=HEADERS)
    requests.post(f"{STORE2_URL}/pet-types/{ids['id_6']}/pets", json={"name": "Lemon", "birthdate": "03-27-2020"}, headers=HEADERS)
    print("Setup Complete.")

def process_query_file():
    output = []
    try:
        with open("query.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("query.txt not found")
        return

    for line in lines:
        line = line.strip()
        if not line: continue
        clean_line = line.rstrip(';')
        
        if clean_line.startswith("query:"):
            content = clean_line.split("query:")[1].strip()
            store_num, query_str = content.split(",", 1)
            url = STORE1_URL if store_num.strip() == "1" else STORE2_URL
            try:
                resp = requests.get(f"{url}/pet-types?{query_str.strip()}")
                status = resp.status_code
                payload = json.dumps(resp.json()) if status == 200 else "NONE"
            except Exception as e:
                status = 500
                payload = "NONE"
            output.append(f"{status}\n{payload}\n;")

        elif clean_line.startswith("purchase:"):
            content = clean_line.split("purchase:")[1].strip()
            try:
                data = json.loads(content)
                resp = requests.post(f"{ORDER_URL}/purchases", json=data)
                status = resp.status_code
                payload = json.dumps(resp.json()) if status == 201 else "NONE"
            except Exception as e:
                status = 500
                payload = "NONE"
            output.append(f"{status}\n{payload}\n;")

    with open("response.txt", "w") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    try:
        run_setup()
        process_query_file()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)