import subprocess

def get_m3u8(url, fname, resolution):

    def get_codes(url):
        nada = subprocess.check_output(['yt-dlp', '-F', url])

        ans = {}
        for line in nada.decode('utf-8').split('\n'):
            if line.find('x') != -1:
                code = line.split()[0]
                res = line.split()[2].split('x')[-1]
                ans[res] = code
        print(ans)
        return ans

    if os.path.exists(fname):
        return

    audio = 'bestaudio'
    # low_audio = 'audio-medium-audio'
    # audio = low_audio

    code = get_codes(url)[str(resolution)]
    cmd = [
        'yt-dlp',
        '-f', f'{code}[ext=mp4]+{audio}[ext=m4a]/{code}+{audio}',
        '--merge-output-format', 'mp4',
        '-o', fname,
        '-N 8',
        url,
    ]
    subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


fout = open('links-daily.txt', 'w')
for link in soup.select('a[class*=episode-link]'):
    video_id = link.get('data-video_id')
    youtube_url = f'https://youtube.com/watch?v={video_id}'
    title = link.select('span[class*=play-title]')[0].text.strip()
    print(title, youtube_url)
    print(title, youtube_url, file=fout)
    try:
        pass
        get_m3u8(youtube_url, f'daily/{title}.mp4', 360)
    except:
        print('FAILED')
fout.close()
