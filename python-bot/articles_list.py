import requests
import json

articles_json = requests.get("https://warframe.fandom.com/api/v1/Articles/List?limit=100000")
articles_list = json.loads(articles_json.content.decode('utf-8'))['items']
articles_dict = {a['title'].lower():a for a in articles_list}