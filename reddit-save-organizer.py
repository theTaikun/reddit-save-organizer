"""
TODO:
1. Allow providing JSON instead of pulling from server ever time
2. Format CSV into readable md/pdf/html

"""
import secrets # file with user credentials
import json
import requests
import requests.auth
import csv
from time import sleep

user=secrets.user
passwd=secrets.passwd
client=secrets.client
secret=secrets.secret # lol

download=True
json_pages=6

final_useragent=secrets.useragent+" by /u/theTaikun"
token =''

def get_data_from_type(row):
   if row['kind']=="t1" or row['kind']=="t3":
       data=row['data']
       if row['kind']=="t1":
          return [get_type_from_fullname(row['kind']),data['subreddit_name_prefixed'],data['link_title'],data['author'],data['body'],data['link_permalink'],data['link_permalink']]
       elif row['kind']=="t3":
          return [get_type_from_fullname(row['kind']),data['subreddit_name_prefixed'],data['title'],data['author'],data['selftext'],"https://www.reddit.com{0}".format(data['permalink']),data['url']]

def get_type_from_fullname(fullname):
    prefix=fullname[:2]
    if prefix == "t1":
        return "Comment"
    elif prefix == "t2":
        return "Account"
    elif prefix == "t3":
        return "Link"
    elif prefix == "t4":
        return "Message"
    elif prefix == "t5":
        return "Subreddit"
    elif prefix == "t6":
        return "Award"
    else:
        return "ERROR"

def download_json():
    client_auth = requests.auth.HTTPBasicAuth(client, secret)
    post_data = {"grant_type": "password", "username": user, "password": passwd}
    headers = {"User-Agent":  final_useragent}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    auth_details=response.json()
    token=auth_details['access_token']
    headers = {"Authorization": "bearer "+token, "User-Agent":  final_useragent}
    
    pages=0
    after=""
    
    while (after is not None):
        if pages==0:
            query ="https://oauth.reddit.com/user/"+user+"/saved?limit=100"
        else:
            query ="https://oauth.reddit.com/user/"+user+"/saved?limit=100&after="+after
        response = requests.get(query, headers=headers)
        print("=================NEW PAGE================",pages)
        with open('raw_page-{0}.json'.format(pages), 'w') as outfile:  
            json.dump(response.json(), outfile)
        after=response.json()["data"]["after"]
        pages+=1
        
        sleep(1.001) # Reddit API requirement (60requests/min max)
    json_pages=pages

def combine_json():
    collection={}
    collection['data']=[]
    for i in range(json_pages):
        with open('raw_page-{0}.json'.format(i)) as json_file:  
            print("Combining page {0}".format(i))
            data = json.load(json_file)
            entrynum=0
            for entry in data['data']['children']:
                collection['data'].append(entry)
                entrynum+=1
    with open('combined.json', 'a') as outfile:  
        json.dump(collection, outfile)

def write_csv():
    with open("output.csv", 'w', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["post_type","subreddit", "title", "author", "body", "permalink","url"])

        with open('combined.json') as json_file:  
                data = json.load(json_file)
                entrynum=0
                for entry in data['data']:
                    spamwriter.writerow(get_data_from_type(entry))
                    #print("{0} items processed".format(saved))
def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {unicode(key, 'utf-8'):unicode(value, 'utf-8') for key, value in row.iteritems()}

def create_markdown():
    mdfile = open("output.md","w",encoding="utf-8")
    with open('output.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        linenum=0
        for row in reader:
            if linenum>1:
                url=row[6]
                mdfile.write(
"""
# {0}
## {1}
{6} by _{2}_ ([Source]({3}))

{4}
[![{5}]({5}) ]({5})

----
""".format(row[2],row[1],row[3],row[5],row[4],url,row[0] if row[0] is "Comment" else "Post")
                    )
            linenum+=1

download_json()
combine_json()
write_csv()

create_markdown()

x=0