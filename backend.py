import json
import time

import requests
import vk
from random import randint

class vk_audio:
    app_id = 6146827
    api = 0
    now_play_audio_id = {'id': 0, 'aid': 0}
    access_token = ''

    def __init__(self, login = '', passwd = '', acc = ''):
        self.now_play_audio_id = {'id': 0, 'aid': 0}
        try:
            if (login != '' and passwd != ''):
                session = vk.AuthSession(app_id=str(self.app_id),
                                         user_login=login, user_password=passwd,
                                         scope='audio, offline')
            elif acc != '':
                session = vk.Session(access_token=acc)
            else:
                raise vk.exceptions.VkAuthError
        except vk.exceptions.VkAuthError as VkAuthError:
            raise VkAuthError
        self.access_token = session.access_token
        self.api = vk.API(session)

    def get_audio(self):
        user_id = randint(1, 5000000)
        do = False
        while not do:
            try:
                audio_user = self.api.audio.get(user_id=user_id, v="5.22")
            except vk.exceptions.VkAPIError as err:
                user_id = randint(1, 5000000)
                time.sleep(1)
            else:
                if len(audio_user['items']) > 0:
                    do = True
                else:
                    user_id = randint(1, 5000000)
        lastfm = last()
        audio_num = randint(0, len(audio_user['items']) - 1)
        self.now_play_audio_id['id'] = user_id
        self.now_play_audio_id['aid'] = audio_user['items'][audio_num]['id']
        artist = audio_user['items'][audio_num]['artist']
        title = audio_user['items'][audio_num]['title']
        image = lastfm.get_image(artist, title)
        if image == lastfm.Not_Found:
            audio = {'url': audio_user['items'][audio_num]['url'],
                     'artist': artist,
                     'title': title,
                     'id': user_id,
                     'aid': audio_user['items'][audio_num]['id'],
                     'duration': audio_user['items'][audio_num]['duration']}
            return audio
        audio = {'url': audio_user['items'][audio_num]['url'],
                 'artist': artist,
                 'title': title,
                 'duration': audio_user['items'][audio_num]['duration'],
                 'id': user_id,
                 'aid': audio_user['items'][audio_num]['id'],
                 'image': image}
        return audio

    def add(self, id, aid):
        self.api.audio.add(owner_id=id, audio_id=aid)

    def get_access_token(self):
        return self.access_token


class last:
    api_key = 'ebbf28d2f2b3f66122332e8ad63a321b'
    Not_Found = 'Not found'
    def __init__(self):
        pass
    def get_image(self, artist, title):
        # pylast.Track
        url = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=' \
              + 'ebbf28d2f2b3f66122332e8ad63a321b' + '&artist=' + artist +'&track=' + title + '&format=json'
        anw = json.loads(requests.get(url).text)
        if ('error' in anw) or ('album' not in anw['track']):
            return self.Not_Found
        image = anw['track']['album']['image']
        image = image[len(image) - 1]['#text']
        return image
