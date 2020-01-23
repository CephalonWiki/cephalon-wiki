import requests
import json
from lxml import html

import RedditBotCephalonWiki
import articles_list

test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "test-cephalon-wiki", subreddit = "cephalonwiki")

def search(title):
    suggestions_json = requests.get("http://warframe.wikia.com/api/v1/SearchSuggestions/List?query=" + title.replace(" ", "_"))
    suggestions_dict = [d["title"] for d in json.loads(suggestions_json.content.decode('utf-8'))["items"]]
    return suggestions_dict

def article(title):
    article_main = requests.get("https://warframe.fandom.com/wiki/" + title.replace(' ','_').replace("&", "%26").replace(" and ", " %26 "))
    article_tree = html.fromstring(article_main.content)
    return article_tree

def generate_article_list():
    articles_list.generate()