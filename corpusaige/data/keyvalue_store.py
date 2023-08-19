
import pickle
from typing import Any, Optional, Union
from sqlalchemy import Column, Integer, Sequence, String, LargeBinary, select
from corpusaige.data import Base

class KeyValue(Base):
    __tablename__ = 'key_value'
    id = Column(Integer, Sequence('kv_id_seq'), primary_key=True)
    key = Column(String(50), unique=True)
    value = Column(LargeBinary)  # Use BLOB for serialized data

def _get_kv_item(session, key: str) -> Optional[KeyValue]:

        return session.execute(select(KeyValue).where(KeyValue.key == key)).scalar_one_or_none()


def get(session, key: str) -> Union[Any, None]:
    kv_item = _get_kv_item(session, key)
    if kv_item:
        return pickle.loads(kv_item.value)
    return None

def put(session, key: str, data: Any) -> None:
    serialized_data = pickle.dumps(data)
    kv_item = _get_kv_item(session, key)

    if kv_item:
        kv_item.value = serialized_data
    else:
        kv_item = KeyValue(key=key, value=serialized_data)
        session.add(kv_item)
    session.commit()

def delete(session, key: str) -> None:
    kv_item = _get_kv_item(session, key)

    if kv_item:
        session.delete(kv_item)
        session.commit()

# Sample usage


