import json
import time

import requests
from tqdm import tqdm

data = json.load(open("./final_data.json", "r"))

get_url = lambda x: f"https://public.chainalysis.com/api/v1/address/{x}"

payload = {}
headers = {
    "X-API-Key": "e9f5d36d2f01642e4407fdbc56074d031d31f49fe9c06eec9a24943b1e928b76"
}

users = list(data.keys())
responses = {}
i = 0
t0 = time.time()
for user in tqdm(users):
    i += 1
    response = requests.request("GET", get_url(user), headers=headers, data=payload)
    assert response.status_code == 200
    responses[user] = response.json()
    if i % 100 == 0:
        json.dump(responses, open("./sanctions.json", "w"))
    if i % 5000 == 0:
        missing_time = time.time() - t0
        if missing_time < 300:
            print("sleeping", 300 - missing_time)
            time.sleep(300 - missing_time)
json.dump(responses, open("./sanctions.json", "w"))
