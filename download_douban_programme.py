#coding=utf8


""" Just for fun :-)
Download songs from Douban Programme.
http://music.douban.com/programmes/
"""


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
        self.output_path = unicode(output_path)

    def get_song_url(self, song_id, ssid):
        req_url = 'http://music.douban.com/j/songlist/get_song_url?sid=%s&ssid=%s' % (song_id, ssid)
        r = urllib2.urlopen(req_url)
        data = json.loads(r.read())
        return data.get('r', '')

    def download_song(self, song_url, output_file, retry=5):
        # need several retrys due to the terrible network
        for i in xrange(retry):
            try:
                content = urllib2.urlopen(song_url).read()
                break
            except Exception as e:
                content = None

        if content:
            with open(output_file, 'wb') as f:
                f.write(content)
            return True

        return False

    def get_meta_infos(self):
        """ Extract programme-title, song-list from the programme page.
        """

        p_url = 'http://music.douban.com/programme/%s' % self.programme_id
        r = urllib2.urlopen(p_url)
        text = r.read()

        self.pattern_item = re.compile(r'<div\s+class="song-item"(.+?)>', re.S)
        self.pattern_meta = re.compile(r'data-title="(.+?)".*?data-songid="(\d+?)".*?data-ssid="(.+?)"', re.S)

        # extract programme_title
        pattern_title = re.compile(r'<p\s+id="songlist-title">(.+?)</p>', re.S)
        p_title = pattern_title.search(text)
        if p_title:
            _title = p_title.group(1).decode('utf8', 'ignore')
            self.output_path = os.path.join(self.output_path, _title + unicode(self.programme_id))
        else:
            self.output_path = os.path.join(self.output_path, unicode(self.programme_id))

        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        meta_list = []
        html_parser = HTMLParser.HTMLParser()
        song_items = self.pattern_item.findall(text)
        for _item in song_items:
            _meta = self.pattern_meta.search(_item)
            if _meta:
                song_title = html_parser.unescape(_meta.group(1).decode('utf8', 'ignore'))
                song_id = _meta.group(2)
                ssid = _meta.group(3)
                meta_list.append((song_title, song_id, ssid))

        return meta_list

    def get_valid_filename(self, song_title, suffix):
        # unsafe chracters for some operating systems, maybe
        invalid = r'[\\/\'",?&#<>|`!@$%^*:]+'
        name = re.sub(invalid, ' ', song_title)

        while len(name) < 200:
            output_file = os.path.join(self.output_path, name) + suffix
            if not os.path.exists(output_file):
                return output_file
            name = name + '_'

        return os.path.join(self.output_path, str(random.randint(1, 10000000))) + suffix

    def start(self):
        meta_list = self.get_meta_infos()
        for song_title, song_id, ssid in meta_list:
            song_url = self.get_song_url(song_id, ssid)
            suffix = os.path.splitext(song_url)[1]
            output_file = self.get_valid_filename(song_title, suffix)
            self.download_song(song_url, output_file)

            print 'Done:', output_file


def main():
    if len(sys.argv) < 3:
        print '[1]douban_programme_id [2]output_path'
        return

    programme_id = sys.argv[1]
    output_path = sys.argv[2]
    dp = DoubanProgramme(programme_id, output_path)
    dp.start()


if __name__ == '__main__':
    main()
