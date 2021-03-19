import datetime
import json
from collections import deque
from typing import Optional

import scrapy

from insta_handshake_item import InstaSHFollowItem


class InstaHandshakeSpider(scrapy.Spider):
    name = 'insta_handshake'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    users_to_parse = deque()
    user_followings = set()
    user_followers = set()
    # start_users = ['alex.sokolov505', 'bessarabskiy']
    query_hashes = {
        'followers': 'c76146de99bb02f6415203be841dd25a',
        'following': 'd04b0a864b4b54837c0d870b0e77e076',
    }

    def __init__(self, *args, users: list, login: str, enc_password: str, **kwargs):
        self.login = login
        self.enc_password = enc_password

        self.start_user, self.target_user = users
        self.users_to_parse.append(self.start_user)

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
                yield from self.usernames_parse(response)
                # for user in self.users:
                #     yield response.follow(
                #         f'https://www.instagram.com/{user}/',
                #         callback=self.user_parse
                #     )

    def usernames_parse(self, response):
        """
        Parse all users in the self.users_to_parse.
        """
        while self.users_to_parse:
            user = self.users_to_parse.pop()
            self.user_followings.clear()
            self.user_followers.clear()
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

        # Get user's followers and following data
        variables = {
            'id': user_data['id'],
            'first': 50,
        }
        yield from self.get_from_api(response, variables, user_data, hash_name='following')
        yield from self.get_from_api(response, variables, user_data, hash_name='followers')

    def follow_parse(self, response, variables, follow_type, user_data, **kwargs):
        """
        Parse the follows data - followers or following.
        """
        edge = {
            'following': 'edge_follow',
            'followers': 'edge_followed_by',
        }

        data = response.json()['data']['user'][edge[follow_type]]
        yield from self.get_items(response, user_data, data, follow_type)
        if data['page_info']['has_next_page']:
            variables['after'] = data['page_info']['end_cursor']
            yield from self.get_from_api(
                response,
                variables,
                user_data,
                hash_name=follow_type,
            )
        else:
            # Run this only once, because twice is a waste.
            if follow_type == 'followers':
                # Implement.
                yield from self.get_mutual_follows(response, user_data['username'])

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
            # Follow Item
            if follow_type == 'following':
                self.user_followings.add(user_data['username'])
                yield InstaSHFollowItem(
                    date_parse=datetime.datetime.now(),
                    user_id=user_data['id'],
                    user_name=user_data['username'],
                    follows_id=follow['node']['id'],
                    follows_name=follow['node']['username'],
                )
            elif follow_type == 'followers':
                self.user_followers.add(user_data['username'])
                yield InstaSHFollowItem(
                    date_parse=datetime.datetime.now(),
                    user_id=follow['node']['id'],
                    user_name=follow['node']['username'],
                    follows_id=user_data['id'],
                    follows_name=user_data['username'],
                )
            else:
                raise ValueError("Invalid 'follow_type' value.")

    def get_mutual_follows(self, response, username):
        """
        Find only mutual follows.
        If target_user is not found, parse mutual follows.
        """
        mutual_follows = self.user_followings.intersection(self.user_followers)
        if self.target_user in mutual_follows:
            # Handle somehow building a path from start to target user.
            pass
        else:
            self.users_to_parse.extendleft(list(mutual_follows))
            yield from self.usernames_parse(response)
