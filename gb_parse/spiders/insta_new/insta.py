"""
.env file with login info must be in the root of Scrapy project directory.
"""
import datetime
import json
from typing import Optional

import scrapy

from insta_loaders import InstagramHashtagLoader, InstagramPostLoader


class InstagramSpider(scrapy.Spider):
    """
    Spider for Instagram post parsing by hashtags.
    Also downloads images of the posts.

    Possible improvement - try to hold 1 session for a long time, so there is no need to log in again every time.
    Maybe store cookies in a file, then pull them to access the existing session?
    """
    name = 'insta'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    hashtags = ['cskabasket']
    api_url = '/graphql/query/'
    posts_query_hash = '9b498c08113f1e09617a1703c22b2f32'

    #   Download tag's image.
    #   For every post in the tag:
    #       Download the image of the post, save to disk (need to write pipeline and settings with Pillow for that).

    def __init__(self, *args, login: str, enc_password: str, hashtags: Optional[list] = None, **kwargs):
        self.login = login
        self.enc_password = enc_password

        if hashtags:
            self.hashtags = hashtags

        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            # Extract login form CSRF token from response.
            js_dict = self.extract_js_dict(response)
            csrf_token = js_dict['config']['csrf_token']
            # Login.
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_password,
                },
                headers={
                    'X-CSRFToken': csrf_token,
                }
            )
        except AttributeError as e:
            # When already logged in.
            if response.json().get('authenticated'):
                for hashtag in self.hashtags:
                    yield response.follow(
                        f'https://www.instagram.com/explore/tags/{hashtag}/',
                        callback=self.tag_parse
                    )

    @staticmethod
    def extract_js_dict(response):
        """
        Extract window._sharedData dictionary from the response.
        """
        js_string = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(js_string.replace('window._sharedData = ', '')[:-1])

    def tag_parse(self, response, **kwargs):
        hashtag = self.extract_js_dict(response)['entry_data']['TagPage'][0]['graphql']['hashtag']

        # Parse tag info (without posts).
        hashtag_data = {key: value for key, value in hashtag.items() if 'edge' not in key}
        loader = InstagramHashtagLoader(response=response)
        loader.add_value('date_parse', datetime.datetime.now())
        loader.add_value('data', hashtag_data)
        loader.add_value('img', hashtag_data['profile_pic_url'])
        yield loader.load_item()

        for post in self.get_posts(response, hashtag):
            yield post

    def get_posts(self, response, hashtag):
        # Get more posts
        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': hashtag["name"],
                'first': 200,
                'after': hashtag['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            yield response.follow(
                f'{self.api_url}?query_hash={self.posts_query_hash}&variables={json.dumps(variables)}',
                callback=self.api_hashtag_parse
            )

        for post in self.posts_parse(response, hashtag):
            yield post

    def api_hashtag_parse(self, response):
        """
        Extract hashtag dict from API response for more posts.
        Response structure is different than the response for the initial hashtag posts request.
        """
        hashtag = response.json()['data']['hashtag']
        for post in self.get_posts(response, hashtag):
            yield post

    @staticmethod
    def posts_parse(response, hashtag):
        """
        Load all the posts' Items.
        """
        for post in hashtag['edge_hashtag_to_media']['edges']:
            loader = InstagramPostLoader(response=response)
            loader.add_value('date_parse', datetime.datetime.now())
            loader.add_value('data', post['node'])
            loader.add_value('img', post['node']['display_url'])
            yield loader.load_item()
