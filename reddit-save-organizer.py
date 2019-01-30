
import secrets
import json
import requests
import requests.auth
import csv
from time import sleep

user=secrets.user
passwd=secrets.passwd
client=secrets.client
secret=secrets.secret
useragent=secrets.useragent

final_useragent=useragent+" by /u/theTaikun"
token =''

def get_data_from_type(row):
    if row['kind']=="t1" or row['kind']=="t3":
        data=row['data']
        if row['kind']=="t1":
            return [data['subreddit'],data['link_title'],data['author'],data['body'],data['link_permalink']]
        elif row['kind']=="t3":
            return [data['subreddit'],data['title'],data['author'],data['selftext'],data['url']]

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


client_auth = requests.auth.HTTPBasicAuth(client, secret)
post_data = {"grant_type": "password", "username": user, "password": passwd}
headers = {"User-Agent":  final_useragent}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
auth_details=response.json()

token=auth_details['access_token']
headers = {"Authorization": "bearer "+token, "User-Agent":  final_useragent}

after=""
collection=[]
pages=0
saved=0
with open("output.csv", 'w', newline='', encoding='utf-8') as csvfile:
    spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["subreddit", "title", "author", "body", "url"])
    while (after is not None):
        if pages==0:
            query ="https://oauth.reddit.com/user/"+user+"/saved?limit=100"
        else:
            query ="https://oauth.reddit.com/user/"+user+"/saved?limit=100&after="+after
        response = requests.get(query, headers=headers)
        formatted_response=response.json()
        #saved=response.json()
        for entry in formatted_response["data"]["children"]:
            data=entry['data']
            collection.append(data)
            
            # May reseult in KeyError if field doesn't exist
            spamwriter.writerow(get_data_from_type(entry))
            print("{0} items processed".format(saved))
            saved+=1
        after=formatted_response["data"]["after"]
        pages+=1
        print("=================NEW PAGE================",pages)
        sleep(1.001)
print(collection)


x=0