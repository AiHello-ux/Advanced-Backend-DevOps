import requests

URL = "http://127.0.0.1:8001"

user_credentials={
  "username": "Kanav",
  "password": "naman20070",
  "role": "admin"
}

response = requests.post(url=URL + "/register",json=user_credentials)
print(response)