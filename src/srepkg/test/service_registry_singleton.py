from srepkg.utils.thread_safe_singletong import ThreadSafeSingleton


class MyStuff(ThreadSafeSingleton):
    registry = {}

    def __init__(self):
        print(self.registry)


a = MyStuff()
a.registry.update({'first': 4})


b = MyStuff()



