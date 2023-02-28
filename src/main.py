from course import Course
import utils
from utils import get_courses


def main():
    utils.authenticate()

    courses = get_courses()
    print('\n'.join(courses), file=open('../courses-full.txt', 'w'))

    with open('../courses.txt') as f:
        for line in f:
            Course(line.strip()).save()


if __name__ == '__main__':
    main()