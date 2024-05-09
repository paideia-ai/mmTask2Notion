import requests
import os

app_secret = os.environ['MM_CMD_TOKEN']

# The URL to the endpoint, replace `localhost` and `8000`
# if your app is hosted elsewhere or on a different port
base_url = "https://87370c55-a249-4d58-a24f-7e4bbae43ffa-00-13jqmwm0yzxfg.spock.replit.dev"
endpoint = "/items/1?q=some_query"
url = f"{base_url}{endpoint}"

# Your token goes here. For demonstration, "fixed_token" is used
token = app_secret

# Headers for the request
headers = {"Authorization": f"Token {token}"}

# Making the GET request
response = requests.post(url, headers=headers)

# Printing the response
print("Status Code:", response.status_code)
print("Response Body:", response.json())
