
from __future__ import print_function
import requests
import cv2

addr = 'http://127.0.0.1:5000'
test_url = addr + '/api/info'

# sudo kill -9 `sudo lsof -t -i:9001`

input_path = "https://d1plicc6iqzi9y.cloudfront.net/sites/default/files/image/201806/25/trinh-thi-oanh_img_0_0.JPEG"
response = requests.post(test_url, json={"data": "data/old_card/51.jpg","choice": 1},headers = {'Content-Type': 'application/json'})
# decode response
if response.status_code == 200:
    print(response.json())
else:
    print(response.status_code)
    print('Cannot get the response from server')
