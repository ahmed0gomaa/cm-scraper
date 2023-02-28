import os
import re

from utils import monospace, get_soup


def get_vimeo_url(url):
    soup = get_soup(url)
    m = re.search(b'<iframe class="iframe video_iframe vimeo_iframe " src="" ata-src="([^\s]*)"', soup.encode())
    return m.group(1).decode('utf-8')


def is_pgn(url):
    return url.startswith('https://chessmood.com/download-from-s3')


def is_quiz(url):
    pos = url.find('episode') + len('episode')
    suffix = url[pos:]
    return suffix.count('/') > 1


class Lessons:

    def __init__(self, soup, dir):
        self.lessons = Lessons.get_lessons_metadata(soup, dir=dir)

    @staticmethod
    def get_anchor_text(anchor):
        # print('anchor', anchor)
        for div in anchor.select('div'):
            div.clear()
        return monospace(anchor.text.strip())

    @staticmethod
    def get_href(anchor):
        return anchor.get('href').strip()




    @staticmethod
    def get_lessons_metadata(soup, dir='prueba'):
        cards_selector = '#accordionExample > div[class*=card]'

        sections = []
        for idx, part in enumerate(soup.select(cards_selector)):
            title = part.select('div[class*=card-header] > button > span')[0]
            links = part.select('div[class*=target] > div > div > a')

            section = {'Name': monospace(title.text.strip())}
            print(section['Name'])

            parts = []
            for link in links:
                try:
                    url = Lessons.get_href(link)

                    part_name = Lessons.get_anchor_text(link)
                    part = {
                        'Name': part_name,
                        'url': url,
                    }

                    if is_pgn(url):
                        part['type'] = 'pgn'
                    elif is_quiz(url):
                        part['type'] = 'quiz'
                    else:
                        part['type'] = 'video'

                    if part['type'] == 'video':
                        part['vimeo_url'] = get_vimeo_url(part['url'])
                    parts.append(part)
                    print('\t', part['Name'])


                except:
                    pass

            section['Parts'] = parts
            sections.append(section)

        return sections

    def save(self, path):
        root = path
        if not os.path.exists(path):
            os.mkdir(path)

        for section in self.lessons:
            for part in section['Parts']:
                path = section['Name']
                path += '/' + part['Name'] + '.mp4'
                print(root + '/' + path)
