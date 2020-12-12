import requests
import re
import json
import os
from bs4 import BeautifulSoup

AOO_CATEGORIES = [
    'self-driving-car',
    # 'autonomous-driving',
    # 'autonomous-vehicles',
    # 'object-detection',
    # 'object-detection?projectPage=2',
    # 'object-detection?projectPage=3',
    # 'object-detection?projectPage=4',
    # 'artificial-intelligence',
    # 'artificial-intelligence?projectPage=2',
    # 'artificial-intelligence?projectPage=3',
    # 'artificial-intelligence?projectPage=4',
    # 'artificial-intelligence?projectPage=5'
]
OUTPUT_FILE = "./repo-collection/aoo_repos.json"


def run():
    all_category_repo_urls = read_json_file(OUTPUT_FILE)
    for category in AOO_CATEGORIES:
        aoo_repo_details_urls = scrape_repo_details_urls(category)
        git_repo_urls = scrape_git_urls_from_details(aoo_repo_details_urls)
        all_category_repo_urls.extend(git_repo_urls)
        break
    all_category_repo_urls = remove_duplicates(all_category_repo_urls)
    write_to_json(all_category_repo_urls)


def scrape_repo_details_urls(category):
    aoo_tree = build_aoo_tree('https://awesomeopensource.com/projects/{}'.format(category))
    list_elems = aoo_tree.find_all('div', class_='aos_project_container')
    urls = list()
    for el in list_elems:
        urls.append(el.find('a')['href'])
    return urls


def scrape_git_urls_from_details(urls):
    git_repo_urls = list()
    count = 1
    total = len(urls)
    for url in urls:
        try:
            print("{}/{} Scraping {}".format(count, total, url))
            count += 1
            aoo_tree = build_aoo_tree(url)
            a_tags = aoo_tree.select('span.aos_project_metadata_content > a')
            # a_tags = aoo_tree.find_all('a')
            for a_tag in a_tags:
                if check_if_href_is_correct(a_tag):
                    git_repo_urls.append(a_tag['href'].split('https://github.com/')[1])
        except Exception as e:
            print('FAILED {}'.format(url))
    return git_repo_urls


def check_if_href_is_correct(a_tag):
    githubg_url_regex = 'https://github\.com/([\w\d\.\-]+)/([\w\d\.\-]+)$'
    return a_tag.has_attr('href') and \
        re.search(githubg_url_regex, a_tag['href'])


def build_aoo_tree(url):
    return BeautifulSoup(get_aoo_html(url), 'html.parser')


def get_aoo_html(url):
    page = requests.get(url)
    return page.content


def remove_duplicates(l):
    return list(dict.fromkeys(l))


def write_to_json(urls):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(urls, f)


def read_json_file(file):
    result = list()
    if not os.path.exists(file):
        return result
    with open(file) as f:
        result = json.load(f)
    return result


if __name__ == "__main__":
    run()
