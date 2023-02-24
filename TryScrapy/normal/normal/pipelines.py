# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import asyncio

# useful for handling different item types with a single interface
from normal.db import SiteInfo
from pubhelper import retry_wraps


@retry_wraps(default=None, debug=False)
def insert_site_info(item: dict):
    assert isinstance(item, dict), 'invalid item type'
    return SiteInfo.insert(**item)


class TmpPipeline:
    async def process_item(self, item, spider):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, insert_site_info, item)

        return item
