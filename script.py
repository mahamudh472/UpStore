
import requests

def load_dummy_products():
    # Step 1: Get the data from Fakestoreapi
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    products = response.json()


    for item in products:
        data = {
            "name" : item.get('title'),
            "description" : item.get('description'),
            "price" : item.get('price')
        }
        
        api_url = "http://127.0.0.1:8000/store/product/"
        res = requests.post(api_url, data=data)
        if res.status_code == 201:
            print(f"Product '{data["name"]}' added successfully")
        else: print(res.status_code)
