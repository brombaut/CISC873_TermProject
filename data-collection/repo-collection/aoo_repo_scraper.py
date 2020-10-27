import requests
import re
import json
import pathlib
from bs4 import BeautifulSoup

AOO_CATEGORIES = [
    'self-driving-car',
    'autonomous-driving',
    'autonomous-vehicles',
    'object-detection',
    'object-detection?projectPage=2',
    'object-detection?projectPage=3',
    'object-detection?projectPage=4',
    'artificial-intelligence',
    'artificial-intelligence?projectPage=2',
    'artificial-intelligence?projectPage=3',
    'artificial-intelligence?projectPage=4',
    'artificial-intelligence?projectPage=5'
]
OUTPUT_FILE = "{}/aoo_repos.json".format(pathlib.Path(__file__).parent.absolute())


def run():
    all_category_repo_urls = list()
    for category in AOO_CATEGORIES:
        aoo_repo_details_urls = scrape_repo_details_urls(category)
        git_repo_urls = scrape_git_urls_from_details(aoo_repo_details_urls)
        all_category_repo_urls.extend(git_repo_urls)
    all_category_repo_urls = remove_duplicates(all_category_repo_urls)
    write_to_csv(all_category_repo_urls)


def scrape_repo_details_urls(category):
    aoo_tree = build_aoo_tree('https://awesomeopensource.com/projects/{}'.format(category))
    list_elems = aoo_tree.find_all('div', class_='aos_project_container')
    urls = list()
    for el in list_elems:
        urls.append(el.find('a')['href'])
    return urls


def scrape_git_urls_from_details(urls):
    git_repo_urls = list()
    for url in urls:
        print("Scraping {}".format(url))
        aoo_tree = build_aoo_tree(url)
        a_tags = aoo_tree.select('span.aos_project_metadata_content > a')
        # a_tags = aoo_tree.find_all('a')
        for a_tag in a_tags:
            if check_if_href_is_correct(a_tag):
                git_repo_urls.append("{}.git".format(a_tag['href']))
        break
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


def write_to_csv(urls):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(urls, f)


if __name__ == "__main__":
    run()
