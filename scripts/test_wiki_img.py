import urllib.request
import json

headers = {'User-Agent': 'AutoSenseProject/1.0 (vaishampayan@example.com)'}
req = urllib.request.Request('https://en.wikipedia.org/api/rest_v1/page/summary/Mahindra_Thar', headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Title:", data.get('title'))
        print("Thumbnail:", data.get('thumbnail', {}).get('source'))
        print("Original:", data.get('originalimage', {}).get('source'))
except Exception as e:
    print("Error:", e)
