class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MongoDB(metaclass=SingletonMeta):

    def __init__(self, host: str, port: str, user: str, password: str, database: str) -> None:
        self.value = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        try:
            self.connect()
        except Exception as e:
            print(e)

    def connect(self):
        """
        Finally, any singleton should define some business logic, which can be
        executed on its instance.
        """

        # ...


    def insert_into(self, collection: str, document: dict):
        pass