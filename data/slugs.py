import json
import os
import time

with open('authors.json', encoding='utf-8') as file:
    authors = json.load(file)
    for i, author in enumerate(authors):
        if i > 100 and author["id"] - authors[i - 1]["id"] > 1:
            print(author["id"])
