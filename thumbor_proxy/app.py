import tornado.web
import tornado.ioloop
import re

from thumbor.url import Url
from thumbor.handlers.imaging import ImagingHandler
from thumbor.app import ThumborServiceApp
from thumbor.context import RequestParameters
from urllib import quote, unquote

class RewriteHandler(ImagingHandler):
    def validate_url(self, url):
        url_signature = self.context.request.hash
        if url_signature:
            signer = self.context.modules.url_signer(self.context.server.security_key)

            url_to_validate = url.replace('/%s/' % self.context.request.hash, '') \
                                 .replace('/%s/' % quote(self.context.request.hash), '')
            valid = signer.validate(unquote(url_signature), url_to_validate)

        return valid

    def validate_image_permutations(self, kw):
        self.context.request = RequestParameters(**kw)

        if self.validate_url(self.request.path):
            return
        else:
            load_target = kw['image']
            # Undo collapsed slashes
            collapsed_slash = re.match("(https?:\/)[^/]", load_target)
            if collapsed_slash:
                load_target = load_target.replace(collapsed_slash.group(1), collapsed_slash.group(1) + "/")
                unescaped_url = self.request.path.replace(kw['image'], load_target)
                if self.validate_url(unescaped_url):
                    kw['image'] = load_target
                    self.request.path = unescaped_url
                    return

            # Undo URL unquoting
            if load_target.find("://") >= 0:
                load_target = quote(load_target, safe='')
                unescaped_url = self.request.path.replace(kw['image'], load_target)
                if self.validate_url(unescaped_url):
                    # We don't want to update the unquoted image at this point, but we do want to update the request path
                    # back to the normal form
                    self.request.path = unescaped_url
                    return

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