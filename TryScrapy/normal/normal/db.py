from sqlalchemy import create_engine, Column, String, Integer, insert
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
Engine = create_engine(
    get_project_settings().get('DB_CONNECT_STR')
)
Session = sessionmaker(Engine)


class Options(object):

    @classmethod
    def insert(cls, **kwargs):
        """插入数据"""
        obj = cls()
        for key, val in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        with Session.begin() as sess:
            sess.add(obj)
        return obj


class SiteInfo(Base, Options):
    __tablename__ = 'site_info'

    id: int = Column(Integer, primary_key=True, comment='主键')
    title: str = Column(String, comment='网站标题', nullable=True, default=None)
    url: str = Column(String(300), comment='网页地址', nullable=True, default=None)
    domain: str = Column(String(300), comment='域名', nullable=True, default=None)
    port: int = Column(Integer, comment='端口号', nullable=True, default=None)
    ip: str = Column(String(20), comment='ip地址', nullable=True, default=None)

    def __repr__(self):
        return f'<SiteInfo {self.url}>'


Base.metadata.create_all(Engine, checkfirst=True)
