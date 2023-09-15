

_name = "First plugin"
_exported_items = ["DemoClass"]

class DemoClass:
    def __init__(self):
        self.name = "Demo class"
    
    def get_name(self):
        return self.name


class PrivateClass:
    pass