import os
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import date, timedelta
from subprocess import check_call, STDOUT
from datetime import datetime

# GitHub uses Sunday-starting weeks, so add 1
offset = (date.today().weekday() + 1) % 7
rows = 7
cols = 52
size = (cols, rows)
numdays = rows * cols
devnull = open(os.devnull, 'w')
start_time = 0
finish_time = 0


def commit(days_ago, msg):
    d = date.today() - timedelta(days=days_ago)
    t = str(d) + ' 00:00:00'
    with open('.tmpfile', 'w') as f:
        f.write(msg)
    check_call('git add .tmpfile', shell=True, stdout=devnull, stderr=STDOUT)
    check_call('set GIT_COMMITTER_DATE="{t}" && set GIT_AUTHOR_DATE={t} && git commit -m {msg}'.format(t=t, msg=msg),
               shell=True, stdout=devnull, stderr=STDOUT)


def rgb2gray(rgb):
    r, g, b = rgb[0:3]  # Ignore alpha for now
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


def write_px(x, y, intensity, prefix=''):
    days_ago = numdays + offset - (x * rows + y)
    for i in range(0, int(intensity)):
        msg = prefix + os.urandom(8).hex()
        commit(days_ago, msg)


# Use this function to process a 52x7 image as grayscale
def process_image(path):
    img = Image.open(path)
    px = img.load()
    image_size = img.size
    if (52, 7) != image_size:
        raise Exception('Image should be 52x7, got ' + image_size)
    for x in range(image_size[0]):
        print('Processed line', x)
        for y in range(image_size[1]):
            val = 255 - int(rgb2gray(px[x, y]))
            val = val / 16
            write_px(x, y, val, prefix='ign-')


def process_text(txt, t_offset=2):
    f = 1
    image = Image.new('RGB', [x*f for x in size], (255, 255, 255))
    draw = ImageDraw.Draw(image)
    # See https://mail.python.org/pipermail/image-sig/2005-August/003497.html
    draw.fontmode = '1'
    font = ImageFont.truetype('font/5x5_pixel.ttf', 8)
    draw.text((t_offset, 1), txt, (0, 0, 0), font=font)
    image.save(txt + '.bmp')


def main():
    global start_time
    start_time = datetime.now()
    if sys.argv[1] == "--text":
        process_text(sys.argv[2])
    else:
        process_image(sys.argv[1])


if __name__ == '__main__':
    main()

