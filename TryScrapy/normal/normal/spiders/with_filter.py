import logging
from pathlib import Path

import chardet
import scrapy
import lxml.etree
import urllib3

from normal.items import SiteItem
from pubhelper import retry_wraps

logger = logging.getLogger(
    Path(__file__).name
)
logger.setLevel(logging.DEBUG)


@retry_wraps(default=None, debug=False)
def build_request(url: str):
    return scrapy.Request(url)


@retry_wraps(default=None, debug=False)
def build_page(res):
    e = (
            res.encoding
            or chardet.detect(res.body).get('encoding')
    )
    body = e and res.body.decode(encoding=e) or res.body
    return lxml.etree.HTML(body)


class DemoSpider(scrapy.Spider):
    name = 'with_filter'
    start_urls = ['https://www.xxx.com']
    custom_settings = {
        'DUPEFILTER_CLASS': 'normal.filters.CountMinSketchFilter',
    }

    def parse(self, res, **kwargs):
        page = build_page(res)
        if page:
            filter_lst = set()
            for item in page.xpath('//a/@href'):
                uri = urllib3.util.parse_url(res.urljoin(item))
                if uri.scheme in ('http', 'https'):
                    filter_lst.add(f'{uri.scheme}://{uri.netloc}')

            ret = list(filter(None, map(lambda x: build_request(x), filter_lst)))

            title = page.xpath('//title/text()')
            title = title and title[0] or ''
            uri = urllib3.util.parse_url(res.url)
            port = (
                    uri.port
                    or (80 if uri.scheme == 'http' else None)
                    or (443 if uri.scheme == 'https' else None)
            )
            item = SiteItem(url=res.url, port=port, title=str(title).strip())
            item['ip'] = str(res.ip_address)
            item['domain'] = uri.host or uri.hostname
            ret.append(item)
            return ret
        else:
            logger.debug(f'{res.url} build page failed')
