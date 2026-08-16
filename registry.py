class CapabilityRegistry:
    def __init__(self):
        self._items = {}

    def register(self, capability):
        self._items[capability["name"]] = capability

    def get(self, name):
        return self._items.get(name)

    def list(self):
        return list(self._items.values())

    def count(self):
        return len(self._items)
