import unicodedata
from os.path import abspath, join, dirname

def get_abs_path(img):
    return abspath(join(dirname(__file__), img))

default_image_path = get_abs_path(u'image.jpg')

def get_image(img):
    encode_formats = ['NFD', 'NFC', 'NFKD', 'NFKC']
    for format in encode_formats:
        try:
            with open(unicodedata.normalize(format, img), 'r') as stream:
                body = stream.read()
                break
        except IOError:
            pass
    else:
        raise IOError('%s not found' % img)
    return body

def default_image():
    return get_image(default_image_path)