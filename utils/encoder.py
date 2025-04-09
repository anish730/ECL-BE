from datetime import time
from enum import Enum

from flask.json.provider import DefaultJSONProvider
from sqlalchemy import Row


class DobatoEncoder(DefaultJSONProvider):
    """this is custom encoder which encodes the sqlalchemy objects"""
    def default(self, obj):
        try:
            return super().default(obj)
        except Exception as e:
            if isinstance(obj, Row):
                return obj._asdict()
            elif isinstance(obj, time):
                return obj.isoformat()
                # Handle enum types
            elif isinstance(obj, Enum):
                return obj.name
            else:
                obj_dict = obj.__dict__
                obj_dict.pop('_sa_instance_state', None)

                return obj_dict
