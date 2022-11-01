import sys
import unittest
from moto import mock_dynamodb
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from handlers.handle_connect import handle_connect
from handlers.handle_disconnect import handle_disconnect
from tests.mock.mock_api import ApiMock
from tests.mock.mock_table import mock_table

class TestHandleConnectDisconnect(unittest.TestCase):

    @mock_dynamodb
    def test_two_hosts(self):
        event1 = {
            'queryStringParameters': {
                "name":"host 1",
                "host":1,
                "room":"AAAA"
            }
        }

        event2 = {
            'queryStringParameters': {
                "name":"host 2",
                "host":1,
                "room":"AAAA"
            }
        }

        table = mock_table()
        apig_management_client = ApiMock()

        #Test: two host connecting to the same room
        self.assertTrue(handle_connect(table, event1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(handle_connect(table, event2, "test_id_2", apig_management_client) == 503)

        #Test: after first host disconnects from room new host should be able to enter the room that is now empty
        self.assertTrue(handle_disconnect(table, event1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(handle_connect(table, event2, "test_id_2", apig_management_client) == 200)
    
    @mock_dynamodb
    def test_player_connection_to_no_host_room(self):
        connection_id = "test_id"
        event = {
            'queryStringParameters': {
                "name":"user_name",
                "host":0,
                "room":"AAAA"
            }
        }
        table = mock_table()
        apig_management_client = ApiMock()

        self.assertTrue(handle_connect(table, event, connection_id, apig_management_client) == 503)
    
    @mock_dynamodb
    def test_double_player_connection(self):
        event1 = {
            'queryStringParameters': {
                "name":"host",
                "host":1,
                "room":"AAAA"
            }
        }

        event2 = {
            'queryStringParameters': {
                "name":"test_name",
                "host":0,
                "room":"AAAA"
            }
        }

        table = mock_table()
        apig_management_client = ApiMock()

        #Test: after host connects, player should be able to connect to the room
        self.assertTrue(handle_connect(table, event1, "host_id", apig_management_client) == 200)
        self.assertTrue(handle_connect(table, event2, "test_id", apig_management_client) == 200)

        #Test: no account should be able to connect using a name that is already used
        self.assertTrue(handle_connect(table, event2, "test_id", apig_management_client) == 503)
        self.assertTrue(handle_connect(table, event2, "test_id_2", apig_management_client) == 503)
        self.assertTrue(table.scan()["Count"] == 2)

        #Test: after user disconnects, should be able to reconnect to the same room with a new id
        self.assertTrue(handle_disconnect(table, event2, "test_id", apig_management_client) == 200)
        self.assertTrue(handle_connect(table, event2, "test_id_2", apig_management_client) == 200)
        self.assertTrue(table.scan()["Count"] == 2)

        #Test: after user disconnects, should error if trying to connect with the same id
        self.assertTrue(handle_disconnect(table, event2, "test_id_2", apig_management_client) == 200)
        self.assertTrue(handle_connect(table, event2, "test_id_2", apig_management_client) == 503)
        self.assertTrue(table.scan()["Count"] == 2)

        #Test: after host disconnect the room should be empty
        self.assertTrue(handle_disconnect(table, event1, "host_id", apig_management_client) == 200)
        self.assertTrue(table.scan()["Count"] == 0)
    

if __name__ == '__main__':
    unittest.main()







