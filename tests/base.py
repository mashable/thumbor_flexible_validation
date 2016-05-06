from tornado.testing import AsyncHTTPTestCase
from thumbor_proxy.app import ThumborServiceProxy
from PIL import Image
from preggy import create_assertions
from skimage.measure import compare_ssim
import cStringIO
import numpy as np

@create_assertions
def to_be_similar_to(topic, expected):
    im = Image.open(cStringIO.StringIO(topic))
    im = im.convert('RGBA')
    topic_contents = np.array(im)

    im = Image.open(cStringIO.StringIO(expected))
    im = im.convert('RGBA')
    expected_contents = np.array(im)

    return get_ssim(topic_contents, expected_contents) > 0.95

def get_ssim(actual, expected):
    im = Image.fromarray(actual)
    im2 = Image.fromarray(expected)

    if im.size[0] != im2.size[0] or im.size[1] != im2.size[1]:
        raise RuntimeError(
            "Can't calculate SSIM for images of different sizes (one is %dx%d, the other %dx%d)." % (
                im.size[0], im.size[1],
                im2.size[0], im2.size[1],
            )
        )
    return compare_ssim(np.array(im), np.array(im2), multichannel=True)

class TestCase(AsyncHTTPTestCase):
    _multiprocess_can_split_ = True

    def get_app(self):
        self.context = self.get_context()
        return ThumborServiceProxy(self.context)

    def get_context(self):
        return Context(None, Config(), None)

    def get(self, path, headers):
        return self.fetch(path,
                          method='GET',
                          body=urllib.urlencode({}, doseq=True),
                          headers=headers,
                          allow_nonstandard_methods=True)

    def post(self, path, headers, body):
        return self.fetch(path,
                          method='POST',
                          body=body,
                          headers=headers,
                          allow_nonstandard_methods=True)

    def put(self, path, headers, body):
        return self.fetch(path,
                          method='PUT',
                          body=body,
                          headers=headers,
                          allow_nonstandard_methods=True)

    def delete(self, path, headers):
        return self.fetch(path,
                          method='DELETE',
                          body=urllib.urlencode({}, doseq=True),
                          headers=headers,
                          allow_nonstandard_methods=True)

    def post_files(self, path, data={}, files=[]):
        multipart_data = encode_multipart_formdata(data, files)

        return self.fetch(path,
                          method='POST',
                          body=multipart_data[1],
                          headers={
                              'Content-Type': multipart_data[0]
                          },
                          allow_nonstandard_methods=True)
