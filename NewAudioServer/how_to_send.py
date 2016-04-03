import requests
url = 'http://127.0.0.1:5000/upload'
files = {'file': open('uploads/uploaded2.wav', 'rb')}
r = requests.post(url, files=files)
r.text

