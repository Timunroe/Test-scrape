import requests
from bs4 import BeautifulSoup
import pprint
import pyperclip
import time
import json
import bleach
import re
import sys

config = {
    "star": {
        "targets": [
            ('author', 'span', 'article__author-name'),
            ('credit', 'span', 'article__author-credit'),
            ('headline', 'h1', 'article__headline'),
        ]
    },
    "dnn": {},
    "e2e": {},
    "3down": {},
    "hamontpolice": {}
}


def get_html(s_url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}
    r = requests.get(s_url, headers=headers)
    return r.text


def url_check(s_url):
    if 'star.com' in s_url:
        return "star"
    if ('thespec.com' in s_url) or ('therecord.com' in s_url) or ('guelphmercury.com' in s_url):
        return "dnn"
    if 'e2e' in s_url:
        return "e2e"
    if 'marauders.ca' in s_url:
        return "mac"
    if 'hamontpolice' in s_surl:
        return 'hamontpolice'


def process(s_site, s_url):
    if s_site == 'star':
        return star_process(s_url)
    if s_site == 'dnn':
        return dnn_process(s_url)
    if s_site == 'e2e':
        return e2e_process(s_url)
    if s_site == 'mac':
        return mac_process(s_url)
    if s_site == 'hamontpolice':
        return hamontpolice_process(s_url)


def star_process(s_url):
    source = get_html(s_url)
    soup = BeautifulSoup(source, "html.parser")

    d_temp_data = {}

    if soup.find("span", class_="article__author-name"):
        d_temp_data["author"] = soup.find("span", class_="article__author-name").text
    else:
        d_temp_data["author"] = ""
    if soup.find("span", class_="article__author-credit"):
        d_temp_data["credit"] = soup.find("span", class_="article__author-credit").text
    else:
        d_temp_data["credit"] = ""
    d_temp_data["headline"] = soup.find("h1", class_="article__headline").text
    if soup.find("span", class_=".article__subheadline"):
        d_temp_data['deck'] = soup.select_one(".article__subheadline").p.text
    else:
        d_temp_data['deck'] = ""

    s_paras = ""
    for para in soup.find_all('p'):
        # paragraphs with any class aren't part of actual article body.
        if para.get('class') is None:
            # Need to filter out all graphs which have an attribute of {'data-reactid'}
            if para.get('data-reactid') is None:
                # Filter out the Read More paragraph and related links in body
                # where the linked text are the entire paragraph
                if para.text.strip() != "Read more:":
                    # Read more links are sentences with all text linked
                    # So, if para.text = para.a.string ?!?
                    # then filter out
                    if para.a:
                        # print("Length of para.text:")
                        # print(len(para.text))
                        # print("Length of para.a.string:")
                        # print(len(para.a.string))
                        print("Para.a.string:")
                        print(para.a.string)
                        print("Para.text: ")
                        print(para.text)
                        # because mistakes! Empty links get sent up
                        if para.a.string is not None:
                            if len(para.a.string) == len(para.text):
                                para.a.string = ''

                    if para.text != '':
                        # print(para.contents)
                        # para.contents is a list of 'children' tags in current tag
                        # normally there is only 1 item in list, but tags
                        # such as <b> <i> etc become their own items in the list
                        # so we have loop through the list, as we don't know how many items
                        new_string = ""
                        for item in para.contents:
                            new_string += str(item)
                        s_paras += "<p>" + new_string + "</p>"
    # Remove all a (link) tags, keeping the text that was linked, obviously
    d_temp_data['body'] = bleach.clean(s_paras, tags=['p', 'b', 'em', 'strong'], strip=True)
    return d_temp_data


def mac_process(s_url):
    source = get_html(s_url)
    soup = BeautifulSoup(source, "html.parser")
    d_temp_data = {}

    d_temp_data['headline'] = soup.find('header', class_='story-header').hgroup.h1.text
    d_temp_data['deck'] = soup.select_one('h2').text
    # need to split into lines based on \n, removing \r
    d_temp_data['body'] = soup.find('div', class_='story-text').text
    d_temp_data['body'] = [item for item in d_temp_data['body'].splitlines()]

    # need to pull out the substrin from last '|' to end of string
    d_temp_data['author'] = soup.find('header', class_='story-header').p.text

    return d_temp_data


def dnn_process(s_url):
    source = get_html(s_url)
    soup = BeautifulSoup(source, "html.parser")

    d_temp_data = {}

    # d_temp_data['author'] = soup.find('meta', name="author").get('content')
    # d_temp_data['author'] = author["content"]
    d_temp_data['headline'] = soup.find('h1', class_="ar-title").text
    # if soup.find('h2', class_="ar-sub-title"):
    # d_temp_data['deck'] = soup.find('h2', class_="ar-sub-titlear-title").text
    temp_site = soup.find("link", rel="canonical").get('href')
    d_temp_data['site'] = re.sub(r'https:\/\/www\.(.*)\.c(a|om)\/.*$', "\\1", temp_site)
    # d_temp_data['section'] = soup.find("meta", property="article:section").get('content')
    if soup.find("script", type="application/ld+json"):
        data_json = json.loads(soup.find("script", type="application/ld+json").text, strict=False)
        d_temp_data['section'] = data_json['articleSection']
        d_temp_data['body'] = data_json['articleBody'].replace('\r\n', '')
        d_temp_data['deck'] = data_json['alternativeHeadline']
        d_temp_data['author'] = data_json['author']['name']
    else:
        d_temp_data['section'] = "NA"
        d_temp_data['body'] = "NA"
        d_temp_data['deck'] = "NA"
        d_temp_data['author'] = "CP Feed"
    return d_temp_data


def e2e_process(s_url):
    source = get_html(config['url'])
    soup = BeautifulSoup(source, "html.parser")
    d_temp_data = {}
    return d_temp_data


def main(url):
    pp = pprint.PrettyPrinter(indent=2)

    site = url_check(url)
    # print(site)
    data = process(site, url)
    # print data to screen
    pp.pprint(data)
    # print data to clipboard
    pyperclip.copy(data['body'])
    time.sleep(1)
    pyperclip.copy(data['deck'])
    time.sleep(1)
    pyperclip.copy(data['headline'])
    time.sleep(1)
    pyperclip.copy(data['author'])
    return


# -- MAIN ---------

# check if url given via applescript
if len(sys.argv) == 2:
    url = sys.argv[1]
    main(url)
elif len(sys.argv) == 1:
    url = input("URL to retrieve? ")
    main(url)
else:
    print("Too many arguments")
