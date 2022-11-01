class ExceptionMock(Exception):
    GoneException = Exception

class ApiMock(ExceptionMock):
    def __init__(self, ):
        self.post_to_connection_runs = 0
        self.exceptions = ExceptionMock
        self.messages = []

    def post_to_connection(self, Data, ConnectionId):
        self.messages.append(Data)
        self.post_to_connection_runs += 1

