from tests.base import TestCase
from os.path import abspath, join, dirname
import tempfile
import shutil
from preggy import expect
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context, ServerParameters
from thumbor.crypto import Cryptor
from tests.fixtures.images import default_image
from urllib import quote

from thumbor.url_signers.base64_hmac_sha1 import (
    UrlSigner
)

class BaseImagingTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kw):
        cls.root_path = tempfile.mkdtemp()
        cls.loader_path = abspath(join(dirname(__file__), '../fixtures/images/'))
        cls.base_uri = "/image"

    @classmethod
    def tearDownClass(cls, *args, **kw):
        shutil.rmtree(cls.root_path)

class UrlValidationPermtuationsTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "tests.stub_file_loader"
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.QUALITY = 'keep'
        cfg.SVG_DPI = 200

        self.image = 'http://test.domain/image.jpg'
        self.quoted_image = quote(self.image, safe='')
        self.transform = '400x400/smart'
        self.signature = UrlSigner(security_key="ACME-SEC").signature('%s/%s' % (self.transform, self.quoted_image))
        self.signed_prefix = "/%s/%s" % (self.signature, self.transform)
        self.full_image = "/%s/%s/%s" % (self.signature, self.transform, self.quoted_image)

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', 'thumbor_flexible_validation.app.ThumborServiceProxy')
        server.security_key = 'ACME-SEC'
        return Context(server, cfg, importer)

    def test_can_get_unsafe_image(self):
        response = self.fetch('/unsafe/smart/image.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_can_get_safe_image(self):
        response = self.fetch('%s/%s' % (self.signed_prefix, self.quoted_image))
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_can_get_unescaped_safe_image(self):
        response = self.fetch('%s/%s' % (self.signed_prefix, self.image))
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_can_get_unescaped_collapsed_safe_image(self):
        response = self.fetch('%s/http:/test.domain/image.jpg' % self.signed_prefix)
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_can_get_double_escaped_collapsed_safe_image(self):
        response = self.fetch('%s/%s' % (self.signed_prefix, "http%253A%252F%252Ftest.domain%252Fimage.jpg"))
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())