import json
import re
from glob import glob

import requests
from pathlib import Path
import subprocess
from multiprocessing import Pool, Process, Queue

REFERER = 'https://chessmood.com'
RESOLUTION = 540
NUM_WORKERS = 4
YT_PATH = '../bin/yt-dlp'
COURSES_PATH = f'../courses-{RESOLUTION}'


def suffix(path, ext):
    return Path(str(path) + ext)


def get_quiz_list(quiz_number):
    params = {"quiz_id": quiz_number}

    quiz_list = []

    while True:
        r = requests.get("https://chessmood.com/quiz/unauthorized/puzzle/next", params=params)
        data = json.loads(r.content)
        if ('puzzle' not in data) or (not data['puzzle']):
            break

        quiz_list.append(data)
        last_id = data['puzzle']['id']
        #             print(f'\t{last_id}')
        params['puzzle_id'] = last_id + 1

    return quiz_list


def convert_puzzle(puzzle, section):
    puzzle = puzzle['puzzle']
    fen = puzzle['fen']
    moves = puzzle['answer']
    author = puzzle['author']
    return f'''[Event "?"]
[Site "?"]
[Date "{section}"]
[Round "?"]
[White "{author}"]
[Black "?"]
[Result "*"]
[FEN "{fen}"]

{moves}
'''


def convert_to_pgn(path):
    pgn_path = path.with_suffix('.pgn')
    if not pgn_path.exists():
        print(f'Converting {path} to {pgn_path}')
        try:
            puzzles = json.load(open(path))
            section = path.parts[-2]
            with open(pgn_path, 'w') as f:
                for puzzle in puzzles:
                    print(convert_puzzle(puzzle, section), file=f)
        except:
            print('REMOVING', path)
            subprocess.run(['rm', path])


def get_extension(r):
    d = r.headers['Content-Disposition']
    fname = re.findall("filename=(.+)", d)[0]
    ext = fname.split('.')[-1]
    return '.' + re.sub(r'\W+', '', ext)


def download_amazon(part, path):
    r = requests.get(part['url'])
    ext = get_extension(r)

    with open(suffix(path, ext), 'wb') as f:
        f.write(r.content)


def download_quiz(part, path):
    quiz_id = part['url'].split('/')[-1]
    quiz = get_quiz_list(quiz_id)
    json.dump(quiz, open(path, 'w'))
    convert_to_pgn(path)


def download_video(part, path):
    cmd = [YT_PATH,
           # f'-f best[height={RESOLUTION}]',
           '--referer', REFERER, '-o', str(path), part['vimeo_url']]
    #subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(cmd)


def download_part(part, path):
    if part['type'] == 'pgn':
        pass
        # path = suffix(path, '.pgn')
    elif part['type'] == 'quiz':
        path = suffix(path, '.json')
        if path.exists():
            convert_to_pgn(path)
    elif part['type'] == 'video':
        path = suffix(path, '.mp4')

    if path.exists():
        print(part['Name'], 'already FOUND')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        print('Getting', path, '...')

        if part['type'] == 'pgn':
            download_amazon(part, path)
        elif part['type'] == 'quiz':
            download_quiz(part, path)
        elif part['type'] == 'video':
            download_video(part, path)


class Worker(Process):
    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue = queue

    def run(self):
        for part, path in iter(self.queue.get, None):
            download_part(part, path)


def download_course(path):
    data = json.load(open(path))
    name = data['Name']
    course_path = Path(COURSES_PATH) / name

    part_idx = 0
    items = []
    for idx, section in enumerate(data['Lessons']):
        section_name = f"{idx:02d} - {section['Name']}"
        section_path = course_path / section_name
        for lesson in section['Parts']:
            lesson_name = f"{part_idx:03d} - {lesson['Name']}"
            part_idx += 1
            lesson_path = section_path / lesson_name

            part = lesson
            path = lesson_path
            items.append((part, path))
            # print(part['Name'], path)
            # download_part(part, path)

    request_queue = Queue()
    for i in range(NUM_WORKERS):
        Worker(request_queue).start()
    for item in items:
        request_queue.put(item)

    # Sentinel objects to allow clean shutdown: 1 per worker.
    for i in range(NUM_WORKERS):
        request_queue.put(None)

    quiz_path =  course_path / 'General Quiz.json'
    if data['Quiz']:
        if not quiz_path.exists():
            quiz_part = {'url': f'quiz/{data["Quiz"]}'}
            download_quiz(quiz_part, quiz_path)
        else:
            # print(quiz_path, 'FOUND')
            pass


def main():
    for path in glob('../data/download/*json'):
        download_course(path)


if __name__ == '__main__':
    main()

# # TODO: Ver Pool.map para metadata

# # Pool of workers
# # https://stackoverflow.com/questions/9038711/python-pool-with-worker-processes
#






