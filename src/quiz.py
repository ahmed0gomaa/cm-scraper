import json
import os.path
import re

import requests

from utils import get_soup


class Quiz:

    def __init__(self, soup, path):
        self.quiz = None
        try:
            url = Quiz.get_quiz_url(soup)
            quiz_id = Quiz.get_quiz_id(url)
            self.path = path
            if not os.path.exists(self.path):
                self.quiz = Quiz.get_quiz_list(quiz_id)
            else:
                print('Quiz FOUND')
                self.quiz = json.load(open(self.path))

        except:
            pass

    def save(self):
        if self.quiz:
            json.dump(self.quiz, open(self.path, 'w'))

    @staticmethod
    def get_quiz_url(soup):
        try:
            take_quiz = soup.find_all(class_='take-quiz')[0]
            return take_quiz.get('href')
        except:
            return None

    @staticmethod
    def get_quiz_id(url):
        try:
            soup = get_soup(url)

            posta = None
            for script in soup.body.find_all('script'):
                if script.text.strip().startswith('const solved_quiz_percent'):
                    posta = script
            # script = soup.body.find_all('script')[8]
            return int(re.find("quiz_id: '(.*)'", posta.text)[0])
        except:
            return None

    @staticmethod
    def get_quiz_list(quiz_number):
        params = {"quiz_id": quiz_number}

        quiz_list = []

        while True:
            r = requests.get("https://chessmood.com/quiz/unauthorized/puzzle/next", params=params)
            data = json.loads(r.content)
            if not data['puzzle']:
                break

            quiz_list.append(data)
            last_id = data['puzzle']['id']
            #             print(f'\t{last_id}')
            params['puzzle_id'] = last_id + 1

        return quiz_list


if __name__ == '__main__':
    import json
    data = Quiz.get_quiz_list(167)
    json.dump(data, open('167.json', 'w'))

