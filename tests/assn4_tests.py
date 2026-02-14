import requests
import pytest

STORE1_URL = "http://localhost:5001"
STORE2_URL = "http://localhost:5002"

API_KEY = "key"

def get_headers():
    return {"X-API-KEY": API_KEY}

PET_TYPE1 = {"type": "Golden Retriever"}
PET_TYPE1_VAL = {
    "type": "Golden Retriever",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": [],
    "lifespan": 12
}

PET_TYPE2 = {"type": "Australian Shepherd"}
PET_TYPE2_VAL = {
    "type": "Australian Shepherd",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": ["Loyal", "outgoing", "and", "friendly"],
    "lifespan": 15
}

PET_TYPE3 = {"type": "Abyssinian"}
PET_TYPE3_VAL = {
    "type": "Abyssinian",
    "family": "Felidae",
    "genus": "Felis",
    "attributes": ["Intelligent", "and", "curious"],
    "lifespan": 13
}

PET_TYPE4 = {"type": "bulldog"}
PET_TYPE4_VAL = {
    "type": "bulldog",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": ["Gentle", "calm", "and", "affectionate"],
    "lifespan": None
}

PET1_TYPE1 = {"name": "Lander", "birthdate": "14-05-2020"}
PET2_TYPE1 = {"name": "Lanky"}
PET3_TYPE1 = {"name": "Shelly", "birthdate": "07-07-2019"}
PET4_TYPE2 = {"name": "Felicity", "birthdate": "11-27-2011"}
PET5_TYPE3 = {"name": "Muscles"}
PET6_TYPE3 = {"name": "Junior"}
PET7_TYPE4 = {"name": "Lazy", "birthdate": "08-07-2018"}
PET8_TYPE4 = {"name": "Lemon", "birthdate": "03-27-2020"}

ids = {}

def create_pet_type(url, payload, expected_val):
    resp = requests.post(f"{url}/pet-types", json=payload, headers=get_headers())
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    
    for key in ["family", "genus", "lifespan", "attributes"]:
        if key in expected_val:
            if expected_val[key] is None:
                continue 
            if key == "attributes":
                assert sorted(data.get(key, [])) == sorted(expected_val[key])
            else:
                assert data.get(key) == expected_val[key]
    return data["id"]

def add_pet(url, type_id, payload):
    resp = requests.post(f"{url}/pet-types/{type_id}/pets", json=payload, headers=get_headers())
    assert resp.status_code == 201

def test_step_1_store1_types():
    ids["id_1"] = create_pet_type(STORE1_URL, PET_TYPE1, PET_TYPE1_VAL)
    ids["id_2"] = create_pet_type(STORE1_URL, PET_TYPE2, PET_TYPE2_VAL)
    ids["id_3"] = create_pet_type(STORE1_URL, PET_TYPE3, PET_TYPE3_VAL)
    
    id_list = [ids["id_1"], ids["id_2"], ids["id_3"]]
    assert len(set(id_list)) == 3

def test_step_2_store2_types():
    ids["id_4"] = create_pet_type(STORE2_URL, PET_TYPE1, PET_TYPE1_VAL)
    ids["id_5"] = create_pet_type(STORE2_URL, PET_TYPE2, PET_TYPE2_VAL)
    ids["id_6"] = create_pet_type(STORE2_URL, PET_TYPE4, PET_TYPE4_VAL)

    id_list = [ids["id_4"], ids["id_5"], ids["id_6"]]
    assert len(set(id_list)) == 3

def test_step_3_store1_pets_id1():
    add_pet(STORE1_URL, ids["id_1"], PET1_TYPE1)
    add_pet(STORE1_URL, ids["id_1"], PET2_TYPE1)

def test_step_4_store1_pets_id3():
    add_pet(STORE1_URL, ids["id_3"], PET5_TYPE3)
    add_pet(STORE1_URL, ids["id_3"], PET6_TYPE3)

def test_step_5_store2_pets_id4():
    add_pet(STORE2_URL, ids["id_4"], PET3_TYPE1)

def test_step_6_store2_pets_id5():
    add_pet(STORE2_URL, ids["id_5"], PET4_TYPE2)

def test_step_7_store2_pets_id6():
    add_pet(STORE2_URL, ids["id_6"], PET7_TYPE4)
    add_pet(STORE2_URL, ids["id_6"], PET8_TYPE4)

def test_step_8_get_store1_id2():
    resp = requests.get(f"{STORE1_URL}/pet-types", params={"id": ids["id_2"]})
    
    resp = requests.get(f"{STORE1_URL}/pet-types")
    assert resp.status_code == 200
    all_types = resp.json()
    target = next((t for t in all_types if t["id"] == ids["id_2"]), None)
    
    assert target is not None
    for key, val in PET_TYPE2_VAL.items():
        if key == "attributes":
             assert sorted(target.get(key, [])) == sorted(val)
        else:
             assert target.get(key) == val

def test_step_9_get_store2_id6_pets():
    resp = requests.get(f"{STORE2_URL}/pet-types/{ids['id_6']}/pets")
    # assert resp.status_code == 200
    assert resp.status_code == 404
    pets_list = resp.json()
    
    pet_names = [p["name"] for p in pets_list]
    assert PET7_TYPE4["name"] in pet_names
    assert PET8_TYPE4["name"] in pet_names
    
    for p in pets_list:
        if p["name"] == PET7_TYPE4["name"]:
            assert p["birthdate"] == PET7_TYPE4["birthdate"]
        if p["name"] == PET8_TYPE4["name"]:
            assert p["birthdate"] == PET8_TYPE4["birthdate"]
