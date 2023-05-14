from typing import TypeVar, Type, Optional

from django.db.models import Model


T = TypeVar('T', bound=Model)

def get_or_none(cls: Type[T], **kwargs) -> Optional[T]:
    try:
        return cls.objects.get(**kwargs)
    except cls.DoesNotExist:
        return None