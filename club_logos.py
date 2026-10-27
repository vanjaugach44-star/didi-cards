"""Fetch API-Sports crests once; an unavailable crest keeps the old badge."""
import hashlib
import io
import os
import re
import sys
from functools import lru_cache
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

CACHE = os.path.join(os.path.dirname(__file__), 'assets', 'club_logos')
MAX_BYTES = 2 * 1024 * 1024


def valid_url(url):
    if not isinstance(url, str):
        return False
    p = urlparse(url)
    return (p.scheme == 'https' and p.netloc == 'media.api-sports.io'
            and re.fullmatch(r'/football/teams/[0-9]+\.png', p.path) is not None
            and not p.query and not p.fragment)


@lru_cache(maxsize=512)
def load_logo(url):
    if not valid_url(url):
        return None
    path = os.path.join(CACHE, hashlib.sha256(url.encode()).hexdigest() + '.png')
    try:
        if os.path.isfile(path):
            with Image.open(path) as im:
                return im.convert('RGBA')
        req = Request(url, headers={'User-Agent': 'DIDI-Football-Cards/1.0'})
        with urlopen(req, timeout=5) as response:
            if not valid_url(response.url):
                return None
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            return None
        with Image.open(io.BytesIO(data)) as source:
            if source.width * source.height > 4_000_000:
                return None
            logo = source.convert('RGBA')
        box = logo.getbbox()
        if not box:
            return None
        logo = logo.crop(box)
        os.makedirs(CACHE, exist_ok=True)
        logo.save(path)
        return logo
    except Exception as exc:
        print(f'Crest unavailable; using club badge ({type(exc).__name__})', file=sys.stderr)
        return None


def draw_logo(img, cx, cy, size, url):
    logo = load_logo(url)
    if logo is None:
        return False
    fitted = ImageOps.contain(logo, (int(size), int(size)), Image.Resampling.LANCZOS)
    img.alpha_composite(fitted, (round(cx - fitted.width / 2), round(cy - fitted.height / 2)))
    return True
