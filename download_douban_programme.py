#coding=utf8


""" Just for fun :-)
Download songs from Douban Programme.
http://music.douban.com/programmes/
"""


import argparse
import HTMLParser
import json
import os
import re
import random
import socket
import sys
import time
import urllib2


class DoubanProgramme(object):

    def __init__(self, programme_id, output_path):
        self.programme_id = programme_id
        self.output_path = output_path

    def _get_song_url(self, songid, ssid):
        url = ('http://music.douban.com/j/songlist/get_song_url?'
               'sid={0}&ssid={1}'.format(songid, ssid)
              )
        r = urllib2.urlopen(url)
        data = json.loads(r.read())
        return data.get('r', '')

    def _download_song(self, song_url, output_file, retry=5):
        # need several retrys due to the terrible network
        for i in xrange(retry):
            try:
                content = urllib2.urlopen(song_url).read()
                break
            except Exception as e:
                content = None

        if not content:
            return False
        with open(output_file, 'wb') as f:
            f.write(content)
        return True

    def _get_meta_infos(self):
        """ Extract programme-title, song-list."""

        purl = 'http://music.douban.com/programme/{0}'.format(self.programme_id)
        r = urllib2.urlopen(purl)
        text = r.read()

        # extract programme_title
        ptitle_re = re.compile(r'id="songlist-title">(?P<ptitle>.+?)</', re.S)
        ptitle = ptitle_re.search(text)
        if ptitle:
            ptitle = ptitle.group('ptitle')
        else:
            ptitle = str(self.programme_id)

        self.output_path = os.path.join(self.output_path, ptitle)
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        meta_re = re.compile(r'<div\s+class="song-item"\s.*?data-title="(?P<title>.+?)"'
                             r'\s.*?data-songid="(?P<songid>\d+?)"'
                             r'\s.*?data-ssid="(?P<ssid>.+?)".*?>', re.S
                            )
        matches = meta_re.findall(text)
        html_parser = HTMLParser.HTMLParser()
        meta_list = [(html_parser.unescape(title), songid, ssid) for
                     title, songid, ssid in matches]
        return meta_list

    def _get_valid_filename(self, title, songid, suffix):
        # unsafe chracters for some operating systems. Maybe:)
        invalid = r'[\\/\'",?&#<>|`!@$%^*:]+'
        name = re.sub(invalid, '', title)[:50]
        fname = '{0}_{1}{2}'.format(name, songid, suffix)
        return os.path.join(self.output_path, fname)

    def start(self):
        meta_list = self._get_meta_infos()
        for title, songid, ssid in meta_list:
            song_url = self._get_song_url(songid, ssid)
            suffix = os.path.splitext(song_url)[1]
            output_file = self._get_valid_filename(title, songid, suffix)
            print 'Downloading... {0}'.format(title)
            self._download_song(song_url, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('programme_id', type=int)
    parser.add_argument('output_path', type=str,
                        help='Path to contain the downloaded songs')
    args = parser.parse_args()

    doupro = DoubanProgramme(args.programme_id, args.output_path)
    doupro.start()


if __name__ == '__main__':
    main()
