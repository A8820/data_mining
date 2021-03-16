import datetime
import json
from typing import Optional

import scrapy

from instasub_item import InstaSubFollowItem
from instasub_loaders import InstaSubUserLoader


class InstaSubSpider(scrapy.Spider):
    name = 'instasub'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    users = ['rickness1686', 'sunrisehotelsprotaras']
    query_hashes = {
        'followers': 'c76146de99bb02f6415203be841dd25a',
        'following': 'd04b0a864b4b54837c0d870b0e77e076',
    }

    def __init__(self, *args, login: str, enc_password: str, users: Optional[list] = None, **kwargs):
        self.login = login
        self.enc_password = enc_password

        if users:
            self.users = users

        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        """
        Login to Instagram and go to user pages from the self.users list.
        """
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
                for user in self.users:
                    yield response.follow(
                        f'https://www.instagram.com/{user}/',
                        callback=self.user_parse
                    )

    @staticmethod
    def extract_js_dict(response):
        """
        Extract window._sharedData dictionary from the response.
        """
        js_string = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(js_string.replace('window._sharedData = ', '')[:-1])

    def user_parse(self, response, **kwargs):
        """
        Parse a user and get followers and following data for them.
        """
        user_data = self.extract_js_dict(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        yield from self.get_user_item(response, user_data)

        # Get user's followers and following data
        variables = {
            'id': user_data['id'],
            'first': 50,
        }
        yield from self.get_from_api(response, variables, user_data, hash_name='followers')
        yield from self.get_from_api(response, variables, user_data, hash_name='following')

    def follow_parse(self, response, variables, follow_type, user_data, **kwargs):
        """
        Parse the follows data - followers or following.
        """
        instructions = {
            'followers': 'edge_followed_by',
            'following': 'edge_follow',
        }

        data = response.json()['data']['user'][instructions[follow_type]]
        if data['page_info']['has_next_page']:
            variables['after'] = data['page_info']['end_cursor']
            yield from self.get_from_api(
                response,
                variables,
                user_data,
                hash_name=follow_type,
            )

        yield from self.get_items(response, user_data, data, follow_type)

    def get_from_api(self, response, request_variables, user_data, *, hash_name):
        """
        Get data for follows from Instagram API.
        """
        yield response.follow(
            f'{self.start_urls[0]}graphql/query/'
            f'?query_hash={self.query_hashes[hash_name]}'
            f'&variables={json.dumps(request_variables)}',
            callback=self.follow_parse,
            cb_kwargs={
                'variables': request_variables,
                'follow_type': hash_name,
                'user_data': user_data,
            },
        )

    def get_items(self, response, user_data: dict, follow_data: dict, follow_type: str):
        """
        Form and yield Instagram user and follower Items.
        """
        for follow in follow_data['edges']:
            # User Item
            yield from self.get_user_item(response, follow['node'])

            # Follow Item
            if follow_type == 'followers':
                yield InstaSubFollowItem(
                    date_parse=datetime.datetime.now(),
                    user_id=int(follow['node']['id']),
                    user_name=follow['node']['username'],
                    follows_id=int(user_data['id']),
                    follows_name=user_data['username'],
                )
            elif follow_type == 'following':
                yield InstaSubFollowItem(
                    date_parse=datetime.datetime.now(),
                    user_id=int(user_data['id']),
                    user_name=user_data['username'],
                    follows_id=int(follow['node']['id']),
                    follows_name=follow['node']['username'],
                )
            else:
                raise ValueError("Invalid 'follow_type' value.")

    @staticmethod
    def get_user_item(response, user_data):
        """
        Form and yield an InstagramUserItem.
        """
        loader = InstaSubUserLoader(response=response)
        loader.add_value('date_parse', datetime.datetime.now())
        loader.add_value('data', user_data)
        yield loader.load_item()
