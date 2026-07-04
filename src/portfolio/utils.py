import requests
from django.utils import timezone
from allauth.socialaccount.models import (
    SocialToken,
    SocialApp,
    SocialAccount
)
from django.core.exceptions import ImproperlyConfigured


URL_MAPS = {
    "youtube": {
        "token": "https://oauth2.googleapis.com/token",
        "api": "https://www.googleapis.com/youtube/v3",
        "channel": "/channels",
        "video": "/videos",
    },
    "discord": {
        "token": "https://discord.com/api/oauth2/token",
        "api": "https://discord.com/api",
        "channel": "/users/@me/guilds"
    },
    "twitch": {
        "token": "https://id.twitch.tv/oauth2/token",
        "api": "https://api.twitch.tv/helix",
        "video": "/videos"
    },
    "meta": {
        "token": "",
        "api": ""
    },
}


class Authentication:

    def __init__(self, user, provider, purpose=None):
        self.token = None
        self.user = user
        self.provider = provider
        self.purpose = purpose

    def __get_url(self):
        return URL_MAPS.get(self.provider, {}).get("token")

    def __refresh_token(self, social_token):
        url = self.__get_url()

        if not url:
            raise ImproperlyConfigured("No url for the provider")

        app = SocialApp.objects.get(
            provider=self.provider if self.provider != 'youtube' else 'google')
        refresh_token = social_token.token_secret

        if not refresh_token:
            raise ImproperlyConfigured("No refresh token. Re-auth required.")

        data = {
            "client_id": app.client_id,
            "client_secret": app.secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"} if self.provider == 'discord' else None

        res = requests.post(url, data=data, headers=headers)
        token_data = res.json()

        if "access_token" not in token_data:
            raise ImproperlyConfigured(f"refresh failed: {token_data}")

        social_token.token = token_data["access_token"]

        # rotate refresh token
        if "refresh_token" in token_data:
            social_token.token_secret = token_data["refresh_token"]

        social_token.save()

        return social_token.token

    def get_token(self):
        if not self.user:
            raise ImproperlyConfigured("user is either empty or not provided")

        if not self.provider:
            raise ImproperlyConfigured(
                "provider is either empty or not provided")

        try:
            social_token = SocialToken.objects.get(
                account__user=self.user,
                account__provider=self.provider if self.provider != 'youtube' else 'google'
            )

        except SocialToken.DoesNotExist:
            if self.purpose == 'SVID':
                social_token = SocialToken.objects.filter(
                    account__provider=self.provider if self.provider != "youtube" else "google"
                ).first()
            else:
                raise ImproperlyConfigured("No social token found")

        # If token exists, try using it first
        access_token = social_token.token

        # OPTIONAL: you can skip this check and always refresh
        if social_token.expires_at and social_token.expires_at <= timezone.now():
            access_token = self.__refresh_token(social_token)

        self.token = access_token
        return access_token

    def has_connected_account(self):
        return SocialAccount.objects.filter(
            user=self.user,
            provider=self.provider if self.provider != 'youtube' else 'google'
        ).exists()


class Api(Authentication):

    def __init__(self, user, provider):
        super().__init__(user, provider)

    def __get_client(self):
        app = SocialApp.objects.get(provider=self.provider)
        self.client_id = app.client_id
        return self.client_id

    def __get_header(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        if self.provider == 'twitch':
            headers['Client-Id'] = self.__get_client()
        return headers

    def __get_url(self):
        return URL_MAPS.get(self.provider, {}).get("api")

    def __request(self, url, params):
        res = requests.get(url=url, headers=self.__get_header(), params=params)
        return res.json()

    def request_video_data(self, id):
        self.purpose = 'SVID'
        self.get_token()
        url = f"{self.__get_url()}{URL_MAPS.get(self.provider, {}).get("video")}"
        params = {"id": id}

        if self.provider == 'youtube':
            params["part"] = "snippet"

        api = self.__request(url=url, params=params)

        if self.provider == 'youtube':
            items = api.get("items", [])

            return items[0]["snippet"] if items else None

        elif self.provider == 'twitch':
            videos = api.get("data", [])

            return videos[0] if videos else None

    def request_channel_data(self):
        self.get_token()
        url = f"{self.__get_url()}{URL_MAPS.get(self.provider, {}).get("channel")}"
        params = {}

        if self.provider == 'youtube':
            params["part"] = "snippet,statistics"
            params["mine"] = "true"

        elif self.provider == 'discord':
            params['with_counts'] = "true"

        api = self.__request(url=url, params=params)

        if self.provider == 'youtube':
            items = api.get("items", [])
            return items

        elif self.provider == 'discord':
            return api

        elif self.provider == 'twitch':
            videos = api.get("data", [])

            return videos[0] if videos else None
        

    def get_twitch_followers(self):
        url = f"{self.__get_url()}/channels/followers"
        params = {
            "broadcaster_id": self.user.public_id,
            "first": 1
        }

        data = self.__request(url=url, params=params)
        return data
                

class Verification(Api):
    def __init__(self, user, provider, video):
        super().__init__(user, provider)
        self.video = video

    def __get_video_data(self):

        if not self.video.extra_data:
            data = self.request_video_data(self.video.get_video_id())
            self.video.extra_data = data
            self.video.save()
            return data

        return self.video.extra_data


    def get_channel_data(self):
        extra_data = self.user.extra_data or {}

        if self.provider not in extra_data:
            data = self.request_channel_data()
            extra_data[self.provider] = data
            self.user.extra_data = extra_data
            self.user.save()

        return extra_data[self.provider]
    

    def __get_user_twitch_data(self):
        account = SocialAccount.objects.get(
            user=self.user,
            provider=self.provider
        )
        uid = account.uid
        data = self.get_twitch_followers()

        context = {
            "uid": uid,
            "statistics": data.get("total", 0)
        }

        if not self.user.extra_data.get(self.provider):
            self.user.extra_data = self.user.extra_data or {}
            self.user.extra_data[self.provider] = context
            self.user.save()
        
        return self.user.extra_data.get(self.provider, {})
        

    def __youtube(self):
        video_data = self.__get_video_data()
        channel_data = self.get_channel_data()

        video_channel_id = video_data.get('channelId')
        channel_ids = [item['id']
                       for item in channel_data]

        return video_channel_id in channel_ids

    def __discord(self):
        guild_id = self.video.get_video_id().get('guild_id', None)
        guilds = self.get_channel_data()

        return any(
            str(g.get("id")) == str(guild_id) and g.get("owner") is True
            for g in guilds
        )

    def __twitch(self):
        video_data = self.__get_video_data()
        channel_data = self.__get_user_twitch_data()

        return video_data.get('user_id') == channel_data.get('uid')

    def __meta(self):
        pass

    def process(self):
        if not self.has_connected_account():
            raise SocialAccount.DoesNotExist

        platform = self.video.platform

        if platform == 'youtube':
            return self.__youtube()
        elif platform == 'twitch':
            return self.__twitch()
        elif platform == 'discord':
            return self.__discord()
        elif platform == 'meta':
            return self.__meta()
