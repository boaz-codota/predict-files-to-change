import requests
import json
from requests_oauthlib import OAuth1
import sys
import pathlib

# Usage example: python3 kaki.py my_out_dir https://api.github.com/repos/y2kappa/timed

if (len(sys.argv) != 3):
    print('Usage: python3 kaki.py <output_dir> <repo> (https://api.github.com/repos/<user>/repo)')

path = str(sys.argv[1])
repo = str(sys.argv[2])

pathlib.Path(path).mkdir(parents=True, exist_ok=True)
output_file = path + '/' + repo.replace('/', '_') + '.txt'

print('Scanning ' + repo + ' -> ' + output_file + '\n=============')
def request_to_github(url):
    result = requests.get(url, 
    headers={"Accept": "application/vnd.github.v3+"}, 
    auth=OAuth1("8477dcc5255b6d701da96123d516bf14ca59664a")).json()
    # print(str(result))
    return result

data = []
i = 1
cur_page = request_to_github(repo + '/pulls?state=closed&per_page=100&page=' + str(i))

while len(cur_page) > 0:
    for entry in cur_page:
        pull = {}
        pull['title'] = entry['title']
        pull['body'] = entry['body']
        pull['files'] = list(map(lambda x: x['filename'], request_to_github(str(entry['_links']['self']['href']) + '/files')))
        print('Pull: ' + pull['title'] + '\n')
        data.append(pull)
    i += 1
    cur_page = request_to_github(repo + '/pulls?state=closed&per_page=100&page=' + str(i))


with open (output_file, 'w') as f:
    f.write(json.dumps(data))
