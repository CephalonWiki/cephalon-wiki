import requests
import json
import csv


def generate(output="../../data/articles.csv"):
    articles_json = requests.get("https://warframe.fandom.com/api/v1/Articles/List?limit=100000")
    articles_list = json.loads(articles_json.content.decode('utf-8'))['items']

    with open(output, 'w', newline='', encoding='utf-8') as articles:
        writer = csv.DictWriter(articles, fieldnames=articles_list[0].keys())
        writer.writeheader()
        writer.writerows(articles_list)


def load(input_dir="../../data/articles.csv"):
    with open(input_dir, 'r', newline='') as articles:
        reader = csv.DictReader(articles)
        articles_dict = {row['title'].lower(): row for row in reader}
        return articles_dict
