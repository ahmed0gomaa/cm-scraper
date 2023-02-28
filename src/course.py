import json
import re

from lessons import Lessons
from utils import get_soup, monospace
from pathlib import Path


def get_quiz_url(soup):
    try:
        take_quiz = soup.find_all(class_='take-quiz')[0]
        return take_quiz.get('href')
    except:
        return None


def get_quiz_id(url):
    try:
        soup = get_soup(url)

        posta = None
        for script in soup.body.find_all('script'):
            lines = script.text.split('\n')
            if len(lines) >= 2:
                first_line = lines[1].strip()
                if first_line.startswith('const solved_quiz_percent'):
                    posta = script
        # script = soup.body.find_all('script')[8]
        return int(re.findall("quiz_id: '(.*)'", posta.text)[0])
    except:
        return None


class Course:

    def __init__(self, course_url):
        # URL
        self.course_url = course_url

        # Soup
        self.soup = get_soup(course_url)

        # Name
        self.name = Course.get_name(self.soup)

        self.short_name = self.course_url.split('/')[-1]

        # Lessons
        self.lessons = None

        # Quiz
        self.quiz = None


    @staticmethod
    def get_name(soup):
        return monospace(soup.find('h1').contents[0])

    def get_lessons(self):
        if not self.lessons:
            self.lessons = Lessons(self.soup, self.name)
        return self.lessons

    def save(self):
        dest = Path(f'../data/{self.short_name}.json')

        print(self.name, '...')
        if dest.exists():
            print('Data already found')
        else:
            print('Getting lessons metadata...')
            dest.parent.mkdir(parents=True, exist_ok=True)

            quiz_url = get_quiz_url(self.soup)
            quiz_id = get_quiz_id(quiz_url)
            lessons = self.get_lessons().lessons
            # lessons = None
            data = {
                'Name': self.name,
                'Lessons': lessons,
                'Quiz': quiz_id,
            }
            print(json.dumps(data, indent=4), file=open(dest, 'w'))
            return data
