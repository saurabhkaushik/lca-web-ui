import requests
import json

'''
def main():
    response = requests.get(
        'https://api.case.law/v1/cases/435800/?full_case=true',
        headers={'Authorization': 'Token 2724f0b89084b69f3f29f875333e7e31bede7d30'}
    )
    print(response.json())
'''

def main_webread():
    response = requests.post(
        # 'https://api.indiankanoon.org/search/?formInput=case&pagenum=1',
        'https://api.indiankanoon.org/doc/198550325/',
        headers={'Authorization': 'Token 111ee136421361730f216d1fcebd9e05acd53a93',
        'Content-Type': 'application/json'}
    )
    jsonresp = str(response.json())
    jsonresp = eval(jsonresp)

    case_dict = json.dumps(jsonresp)

    with open('store/case.json', 'w') as f:
        f.write(case_dict)

def read_file_json(): 
    f = open('store/case.json', 'r')
    strjoson = f.read()
    jsonobj = json.loads(strjoson)
    print(jsonobj['citeList'])

if __name__ == "__main__":
    read_file_json()
    #main_webread()