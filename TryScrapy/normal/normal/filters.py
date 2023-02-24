import logging
from pathlib import Path

import scrapy.dupefilters
import urllib3.util
import tldextract
from threading import Lock
from pubhelper import md5
from probables import CountMinSketch
from concurrent.futures import ThreadPoolExecutor
from scrapy.utils.project import get_project_settings

filter_export_lock = Lock()
subtask = ThreadPoolExecutor(5)
settings = get_project_settings()


def export(dup_filter):
    if filter_export_lock.acquire(blocking=False):
        dup_filter.export(
            settings.get('FILTER_FILE_PATH')
        )
        filter_export_lock.release()


class CountMinSketchFilter(scrapy.dupefilters.BaseDupeFilter):
    def __init__(self):
        cm_path = Path(settings.get('FILTER_FILE_PATH'))
        if cm_path.exists():
            self.cm = CountMinSketch.frombytes(cm_path.read_bytes())
        else:
            self.cm = CountMinSketch(width=10000000, depth=5)
        self.logger = logging.getLogger(Path(__file__).name)

    @classmethod
    def from_settings(cls, settings):
        return cls()

    def request_seen(self, request):
        uri = urllib3.util.parse_url(request.url)
        net_loc_hash = md5(uri.netloc)

        ret = True
        tld = tldextract.extract(request.url)
        if tld.registered_domain:
            domain_hash = md5(tld.registered_domain)
            if self.cm.check(domain_hash) < 20:
                if self.cm.check(net_loc_hash) < 1:
                    self.cm.add(domain_hash)
                    self.cm.add(net_loc_hash)
                    ret = False
        elif self.cm.check(net_loc_hash) < 1:
            self.cm.add(net_loc_hash)
            ret = False

        # 保存去重数据
        if not ret:
            # subtask.submit(export, self.cm)
            self.logger.debug(f'dup filter, new target: {request}')

        if ret:
            self.logger.debug(f'dup filter, target exists: {request}')

        return ret
