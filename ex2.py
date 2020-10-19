from selenium import webdriver
import re
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd
# from google.colab import files
# takes url from user
url = input("Enter the website url: ")

# creates a double ended queue iterable object
new_urls = deque([url])
# len(new_urls) == 1

# # created an immutable set for the processed_urls emails
emails = []

processed_urls = set()
local_urls = set()
foreign_urls = set()
broken_urls = set()

# while the length of the set new_urls
while len(new_urls):
    url = new_urls.popleft()

    processed_urls.add(url)
    print("Processing %s" % url)

    try:
        response = requests.get(url)
    except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError,
            requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
        broken_urls.add(url)
        continue

    new_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+[\.com|.co.uk]", response.text, re.I)
    emails.append(new_emails)

    parts = urlsplit(url)

    base = "{0.netloc}".format(parts)
    strip_base = base.replace("www.", "")
    base_url = "{0.scheme}://{0.netloc}".format(parts)

    path = url[:url.rfind('/')+1] if '/' in parts.path else url

    soup = BeautifulSoup(response.text, 'lxml')

    for link in soup.find_all('a'):
        anchor = link.attrs["href"] if "href" in link.attrs else ''
        if anchor.startswith('/'):
            local_link = base_url + anchor
            local_urls.add(local_link)
        elif strip_base in anchor:
            local_urls.add(anchor)
        elif not anchor.startswith('http'):
            local_link = path + anchor
            local_urls.add(local_link)
        else:
            foreign_urls.add(anchor)

    for i in local_urls:
        if not i in new_urls and not i in processed_urls:
            new_urls.append(i)
            
print("Email: ", emails)
