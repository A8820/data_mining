import datetime
import bs4
import requests
from urllib.parse import urljoin
from task_lesson3_db import DataBase


class GbBlogParse_:

    def __init__(self, start_url: str, db_obj: DataBase):
        self.start_url = start_url
        self.page_done = set()
        self.db = db_obj

    def __get(self, url) -> bs4.BeautifulSoup:
        response = requests.get(url)
        self.page_done.add(url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        return soup

    def run(self, url=None):
        if not url:
            url = self.start_url

        if url not in self.page_done:
            soup = self.__get(url)
            posts, pagination = self.parse(soup)

            for post_url in posts:
                page_data = self.page_parse(self.__get(post_url), post_url)
                self.save(page_data)
            for p_url in pagination:
                self.run(p_url)

    def parse(self, soup):
        ul_pag = soup.find('ul', attrs={'class': 'gb__pagination'})
        paginations = set(
            urljoin(self.start_url, url.get('href')) for url in ul_pag.find_all('a') if url.attrs.get('href'))
        posts = set(
            urljoin(self.start_url, url.get('href')) for url in soup.find_all('a', attrs={'class': 'post-item__title'}))
        return posts, paginations

    def page_parse(self, soup, url) -> dict:
        # контент есть тут
        # tmp = soup.find('script', attrs={'type': 'application/ld+json'}).string

        date_time_str = soup.find('div', attrs={'class': 'blogpost-date-views'}).find('time').get('datetime')
        date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S%z")
        data = {
            'post_data': {
                'url': url,
                'title': soup.find('h1').text,
                'image': soup.find('div', attrs={'class': 'blogpost-content'}).find('img').get('src') if soup.find(
                    'div', attrs={'class': 'blogpost-content'}).find('img') else None,
                'date': date_time_obj,
            },
            'writer': {'name': soup.find('div', attrs={'itemprop': 'author'}).text,
                       'url': urljoin(self.start_url,
                                      soup.find('div', attrs={'itemprop': 'author'}).parent.get('href'))},

            'tags': [],
            'comments': []
        }

        for tag in soup.find_all('a', attrs={'class': "small"}):
            tag_data = {
                'url': urljoin(self.start_url, tag.get('href')),
                'name': tag.text
            }
            data['tags'].append(tag_data)

        comments_soup = soup.find('div', attrs={'class': 'm-t-xl'}).find('comments')
        for comment in self.get_comments(comments_soup):
            comment_data = {
                'id': comment.get('comment').get('id'),
                'author': comment.get('comment').get('user').get('full_name'),
                'comment': comment.get('comment').get('body')
            }
            data['comments'].append(comment_data)

        return data

    def get_comments(self, comments_soup):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        }

        if comments_soup:
            params = {
                'commentable_type': comments_soup.get('commentable-type'),
                'commentable_id': comments_soup.get('commentable-id'),
                'order': comments_soup.get('order')
            }
            com_url = 'https://geekbrains.ru/api/v2/comments'
            response: requests.Response = requests.get(com_url, params=params, headers=headers)
            if response.status_code != 200:
                return []

            comm_data = response.json()
            return comm_data

    def save(self, page_data: dict):
        # print(page_data)
        self.db.create_post(page_data)


if __name__ == '__main__':
    db = DataBase('sqlite:///task_lesson3_db.db')
    parser = GbBlogParse_('https://geekbrains.ru/posts', db)

    parser.run()
