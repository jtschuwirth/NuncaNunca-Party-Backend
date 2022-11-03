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
from handlers.handle_game_start import handle_game_start
from handlers.handle_endturn import handle_endturn
from tests.mock.mock_api import ApiMock
from tests.mock.mock_table import mock_table

class Test2PlayersGame(unittest.TestCase):
    def start_2_players_game(self, table, host, player_1, player_2, apig_management_client):
        #Test: host connects to room
        handle_connect(table, host, "host_id", apig_management_client)

        #Players connect to the room
        handle_connect(table, player_1, "test_id_1", apig_management_client)
        handle_connect(table, player_2, "test_id_2", apig_management_client)

        #Host starts game
        handle_game_start(table, host, "host_id", apig_management_client)


    @mock_dynamodb
    def test_2_players_gameplay_with_reconnection(self):
        host = {
            'queryStringParameters': {
                "name":"host_1",
                "host":1,
                "room":"AAAA"
            }
        }

        player_1 = {
            'queryStringParameters': {
                "name":"player_1",
                "host":0,
                "room":"AAAA"
            }
        }

        player_2 = {
            'queryStringParameters': {
                "name":"player_2",
                "host":0,
                "room":"AAAA"
            }
        }

        response_player_1 = {
            "body": """{
                "answer": 0,
                "guess": 0
            }"""
        }

        response_player_2 = {
            "body": """{
                "answer": 1,
                "guess": 1
            }"""
        }

        table = mock_table()
        apig_management_client = ApiMock()

        self.start_2_players_game(table, host, player_1, player_2, apig_management_client)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["turn_status"] == "playing")

        #First player ends his turn
        self.assertTrue(handle_endturn(table, response_player_1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "done")
        
        #Second player ends his turn
        self.assertTrue(handle_endturn(table, response_player_2, "test_id_2", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["turn_status"] == "playing")
        
        #Points are given correctly to each player
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["points"] == 50)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["points"] == 100)

        #Second player disconnects from game
        self.assertTrue(handle_disconnect(table, player_2, "test_id_2", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["turn_status"] == "disconnected")

        #First player ends his turn
        self.assertTrue(handle_endturn(table, response_player_1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["points"] == 150)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")

        #Second player reconnects
        self.assertTrue(handle_connect(table, player_2, "test_id_2b", apig_management_client) == 200)

        #First player ends his turn
        self.assertTrue(handle_endturn(table, response_player_1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["points"] == 250)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")


        #Now player 2 can play again
        self.assertTrue(handle_endturn(table, response_player_2, "test_id_2b", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2b"})["Item"]["turn_status"] == "done")

        #First player ends his turn
        self.assertTrue(handle_endturn(table, response_player_1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2b"})["Item"]["turn_status"] == "playing")

        #Points are given correctly to each player
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["points"] == 300)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2b"})["Item"]["points"] == 200)

        #When host disconnects everyone his kicked from the game
        self.assertTrue(handle_disconnect(table, host, "host_id", apig_management_client) == 200)
        self.assertTrue(table.scan()["Count"] == 0)

    @mock_dynamodb
    def test_2_players_gameplay_with_reconnection_after_turn_end(self):
        host = {
            'queryStringParameters': {
                "name":"host_1",
                "host":1,
                "room":"AAAA"
            }
        }

        player_1 = {
            'queryStringParameters': {
                "name":"player_1",
                "host":0,
                "room":"AAAA"
            }
        }

        player_2 = {
            'queryStringParameters': {
                "name":"player_2",
                "host":0,
                "room":"AAAA"
            }
        }

        response_player_1 = {
            "body": """{
                "answer": 0,
                "guess": 0
            }"""
        }

        table = mock_table()
        apig_management_client = ApiMock()

        self.start_2_players_game(table, host, player_1, player_2, apig_management_client)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["turn_status"] == "playing")

        #First player ends his turn
        self.assertTrue(handle_endturn(table, response_player_1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "done")

        #Second player disconnect after player 1 has already pased turn
        self.assertTrue(handle_disconnect(table, player_2, "test_id_2", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["turn_status"] == "disconnected")

        #The game handles turnend anyways
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["points"] == 100)

        #First player plays another turn
        self.assertTrue(handle_endturn(table, response_player_1, "test_id_1", apig_management_client) == 200)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["points"] == 200)

    @mock_dynamodb
    def test_ten_rounds_game(self):
        host = {
            'queryStringParameters': {
                "name":"host_1",
                "host":1,
                "room":"AAAA"
            }
        }

        player_1 = {
            'queryStringParameters': {
                "name":"player_1",
                "host":0,
                "room":"AAAA"
            }
        }

        player_2 = {
            'queryStringParameters': {
                "name":"player_2",
                "host":0,
                "room":"AAAA"
            }
        }

        response_player_1 = {
            "body": """{
                "answer": 0,
                "guess": 0
            }"""
        }

        response_player_2 = {
            "body": """{
                "answer": 1,
                "guess": 1
            }"""
        }

        table = mock_table()
        apig_management_client = ApiMock()

        self.start_2_players_game(table, host, player_1, player_2, apig_management_client)
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
        self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["turn_status"] == "playing")
        game = 0
        while game < 10:
            game+=1
            #First player ends his turn
            self.assertTrue(handle_endturn(table, response_player_1, "test_id_1", apig_management_client) == 200)
            self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "done")
            
            #Second player ends his turn
            self.assertTrue(handle_endturn(table, response_player_2, "test_id_2", apig_management_client) == 200)
            self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["turn_status"] == "playing")
            self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["turn_status"] == "playing")

            self.assertTrue(table.get_item(Key = {"connection_id": "test_id_1"})["Item"]["points"] == 50*game)
            self.assertTrue(table.get_item(Key = {"connection_id": "test_id_2"})["Item"]["points"] == 100*game)





if __name__ == '__main__':
    unittest.main()

