from handlers.handle_message import handle_message
from handlers.handle_game_start import handle_game_start
from handlers.handle_change_level import handle_change_level
from handlers.handle_endturn import handle_endturn

route_dic = {
    "sendmessage": handle_message,
    "startgame": handle_game_start,
    "changelevel": handle_change_level,
    "endturn": handle_endturn

}

def routes(route_key, table, event, connection_id, apig_management_client):
    action = route_dic[route_key]
    action(table, event, connection_id, apig_management_client)
