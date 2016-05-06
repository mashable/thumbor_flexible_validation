import tornado.web
import tornado.ioloop
import tornado.gen as gen
import re

from thumbor.url import Url
from thumbor.handlers.imaging import ImagingHandler
from thumbor.app import ThumborServiceApp
from thumbor.context import RequestParameters
from urllib import quote, unquote

class RewriteHandler(ImagingHandler):
    def validate_url(self, url, security_key):
        valid = True

        url_signature = self.context.request.hash
        if url_signature:
            signer = self.context.modules.url_signer(self.context.server.security_key)

            url_to_validate = url.replace('/%s/' % self.context.request.hash, '') \
                                 .replace('/%s/' % quote(self.context.request.hash), '')
            valid = signer.validate(unquote(url_signature), url_to_validate)

            if not valid and security_key is not None:
                signer = self.context.modules.url_signer(security_key)
                valid = signer.validate(url_signature, url_to_validate)

        return valid


    @gen.coroutine
    def validate_image_permutations(self, kw):
        security_key = None
        if self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            security_key = yield gen.maybe_future(self.context.modules.storage.get_crypto(self.context.request.image_url))

        self.context.request = RequestParameters(**kw)

        if self.validate_url(self.request.path, security_key):
            return
        else:
            # From the kw args given, generate a URL options fragment
            args = kw.copy()
            del args['hash']
            del args['image']
            del args['unsafe']
            args = dict((k, v) for k, v in args.iteritems() if v)
            url_options = Url.generate_options(**args)

            load_target = kw['image']

            # Undo collapsed slashes
            collapsed_slash = re.match("(https?:\/)[^/]", load_target)
            if collapsed_slash:
                load_target = load_target.replace(collapsed_slash.group(1), collapsed_slash.group(1) + "/")
                unescaped_url = "/%s/%s/%s" % (kw['hash'], url_options, load_target)
                if self.validate_url(unescaped_url, security_key):
                    kw['image'] = load_target
                    self.request.path = unescaped_url
                    return

            # Undo URL unquoting
            if load_target.find("://") >= 0:
                load_target = quote(load_target, safe='')
                unescaped_url = "/%s/%s/%s" % (kw['hash'], url_options, load_target)
                if self.validate_url(unescaped_url, security_key):
                    kw['image'] = unquote(load_target)
                    self.request.path = unescaped_url
                    return

            # Undo double-quoting
            if load_target.find("%3A%2F") >= 0:
                load_target = unquote(kw['image'])
                unescaped_url = "/%s/%s/%s" % (kw['hash'], url_options, quote(load_target, safe=''))
                if self.validate_url(unescaped_url, security_key):
                    self.request.path = unescaped_url
                    kw['image'] = load_target


    @tornado.web.asynchronous
    def get(self, **kw):
        self.validate_image_permutations(kw)
        self.check_image(kw)

    @tornado.web.asynchronous
    def head(self, **kw):
        self.validate_image_permutations(kw)
        self.check_image(kw)

class ThumborServiceProxy(ThumborServiceApp):
    def __init__(self, context):
        ThumborServiceApp.__init__(self, context)

    def get_handlers(self):
        handlers = ThumborServiceApp.get_handlers(self)

        # Remove the default image handler
        handlers.pop()

        # Then install our own image handler
        handlers.append(
            (Url.regex(), RewriteHandler, {'context': self.context})
        )
        return handlers