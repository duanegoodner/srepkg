from enum import Enum, auto


class ServiceObjectID(Enum):
    ORIG_SRC_PREPARER = auto()
    RETRIEVER = auto()
    PROVIDER = auto()
    CONSTRUCTION_DIR = auto()
    SDIST_COMPLETER = auto()
    WHEEL_COMPLETER = auto()
    BUILDER = auto()


class ServiceRegistry:

    def __init__(self):
        self._registry = {}

    def register(self, new_items: dict[ServiceObjectID, object]):
        for item in new_items:
            if item in self._registry:
                raise DuplicateServiceObjectID(item)
        self._registry.update(new_items)

    def get_service(self, object_id: ServiceObjectID):
        try:
            return self._registry[object_id]
        except KeyError:
            raise UnregisteredServiceObjectID(object_id)

    def reset(self):
        self._registry.clear()


class DuplicateServiceObjectID(Exception):
    def __init__(
            self,
            service_object_id: ServiceObjectID,
            msg="Service object ID already entered in ServiceRegistry"):
        self._service_object_id = service_object_id
        self._msg = msg

    def __str__(self):
        return f"{str(self._service_object_id)} -> {self._msg}"


class UnregisteredServiceObjectID(Exception):
    def __init__(
            self,
            service_object_id: ServiceObjectID,
            msg="Object ID not found in service registry"):
        self._service_object_id = service_object_id
        self._msg = msg

    def __str__(self):
        return f"{str(self._service_object_id)} -> {self._msg}"
