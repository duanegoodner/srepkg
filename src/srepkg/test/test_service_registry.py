import pytest
import srepkg.service_registry as sr


class TestServiceRegistry:

    def setup_method(self):
        self.registry = sr.ServiceRegistry()

    def test_valid_register_ops(self):
        self.registry.register({sr.ServiceObjectID.BUILDER: 'item'})
        existing_construction_dir =\
            self.registry.get_service(sr.ServiceObjectID.BUILDER)
        self.registry.reset()

    def test_register_duplicate_id(self):
        self.registry.register({sr.ServiceObjectID.BUILDER: 'item_a'})
        with pytest.raises(sr.DuplicateServiceObjectID):
            self.registry.register({sr.ServiceObjectID.BUILDER: 'item_b'})

    def test_get_unregistered_id(self):
        with pytest.raises(sr.UnregisteredServiceObjectID):
            self.registry.get_service(sr.ServiceObjectID.BUILDER)

    def test_print_duplicate_service_object_id_exception(self):
        dsoi_exception = sr.DuplicateServiceObjectID(
            sr.ServiceObjectID.BUILDER)
        print(dsoi_exception)

    def test_print_unregistered_service_object_id_exception(self):
        usoi_exception = sr.UnregisteredServiceObjectID(
            sr.ServiceObjectID.BUILDER)
        print(usoi_exception)



