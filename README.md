## About

This is a custom app which fixes issues with misbehaving clients quoting and unquoting parts of URLs, which can break Thumbor's signature checking.

## The problem

When you generate a signed Thumbor URL, it might be something like:

    /nj18coYIvJKQ7QbhFueMFuseuMM=/fit-in/575x4096/https%3A%2F%2Fdomain.com%2Fpath%2Fto%2Fimage.jpg

But misbehaving clients might double-quote or unquote the URL, resulting in variants like:

    /nj18coYIvJKQ7QbhFueMFuseuMM=/fit-in/575x4096/https://domain.com/path/to/image.jpg
    /nj18coYIvJKQ7QbhFueMFuseuMM=/fit-in/575x4096/https:/domain.com/path/to/image.jpg
    /nj18coYIvJKQ7QbhFueMFuseuMM=/fit-in/575x4096/https%3A//domain.com/path/to/image.jpg

This replaces the default Thumbor request handler, and attempts to validate the signature of variants of the URL given, which will cause all of the above variants to be internally rewritten to the variant generated, so long as a variant the matches the given signature can be found.

## Usage

    git clone git@github.com:mashable/thumbor_flexible_validation.git
    pip install thumbor_flexible_validation

Then to use it:

    thumbor -c /your/thumbor.conf -a thumbor_flexible_validation.app.ThumborServiceProxy