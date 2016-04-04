import requests
url = 'http://audio.norijacoby.com/analyze'
files = {'file': open('uploads/uploaded2.wav', 'rb')}
r = requests.post(url, files=files)
print r.text

