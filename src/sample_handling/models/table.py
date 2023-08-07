from ispyb.models import Container
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER


class NewContainer(Container):
    parentContainerId = Column(INTEGER(10))
