

class ApiKeyManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ApiKeyManager, cls).__new__(cls)
            cls._instance.api_key = None
        return cls._instance

    def set_api_key(self, key):
        self.api_key = key
        return 

    def get_api_key(self):
        return self.api_key
    


