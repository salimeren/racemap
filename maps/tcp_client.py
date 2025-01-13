import json
from websockets.sync.client import connect
from typing import Optional, Any, Dict, Union
from websockets.exceptions import WebSocketException

def create_websocket_connection(host: str = "127.0.0.1", port: int = 1423) -> Any:
    try:
        return connect(f"ws://{host}:{port}")
    except WebSocketException as e:
        return None

def ensure_json_response(response: Optional[str]) -> str:
    if response is None:
        return json.dumps({"status": "error", "message": "No response from server"})
    try:
        # Test if it's already valid JSON
        json.loads(response)
        return response
    except json.JSONDecodeError:
        # If not, wrap the response in a JSON structure
        return json.dumps({"status": "success", "message": response})

def send_to_server(username: str, command: str, *args) -> str:

    if not username:
        return json.dumps({"status": "error", "message": "Username is required"})

    try:
        with create_websocket_connection() as wsock:
            if not wsock:
                return json.dumps({"status": "error", "message": "Could not connect to server"})

            initial_msg = wsock.recv()
            wsock.send(json.dumps({"username": username}))
            welcome_msg = wsock.recv()

            command_msg = {
                "command": command.lower().replace(" ", "_"),
                "params": list(args)
            }
            wsock.send(json.dumps(command_msg))
            response = wsock.recv()

            return ensure_json_response(response)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Communication error: {str(e)}"
        })

def send_component_to_server(username: str, map_id: str, component: str, row: str, col: str) -> str:
    if not map_id:
        return json.dumps({"status": "error", "message": "No map attached"})

    try:
        with create_websocket_connection() as wsock:
            if not wsock:
                return json.dumps({"status": "error", "message": "Could not connect to server"})

            initial_msg = wsock.recv()
            wsock.send(json.dumps({"username": username}))
            welcome_msg = wsock.recv()

            attach_command = {
                "command": "attach",
                "params": [map_id]
            }
            wsock.send(json.dumps(attach_command))
            attach_response = wsock.recv()

            create_command = {
                "command": "create",
                "params": [component.lower()]
            }
            wsock.send(json.dumps(create_command))

            create_response = wsock.recv()

            try:
                create_data = json.loads(create_response)
                print(create_data)
                component_id = create_data.get("component_id")
                print(component_id)
                if not component_id:
                    return json.dumps({"status": "error", "message": "Failed to create component"})
            except (json.JSONDecodeError, KeyError):
                return json.dumps({"status": "error", "message": "Invalid server response"})

            place_command = {
                "command": "place",
                "params": [str(component_id), row, col]
            }
            wsock.send(json.dumps(place_command))
            place_response = wsock.recv()

            detach_command = {
                "command": "detach",
                "params": [map_id]
            }
            wsock.send(json.dumps(detach_command))
            detach_response = wsock.recv()

            return ensure_json_response(place_response)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}"
        })

def send_delete_to_server(username: str, map_id: str, command: str, *args) -> str:
    try:
        with create_websocket_connection() as wsock:
            if not wsock:
                return json.dumps({"status": "error", "message": "Could not connect to server"})

            initial_msg = wsock.recv()
            wsock.send(json.dumps({"username": username}))
            welcome_msg = wsock.recv()

            attach_command = {
                "command": "attach",
                "params": [map_id]
            }
            wsock.send(json.dumps(attach_command))
            attach_response = wsock.recv()

            delete_command = {
                "command": command.lower().replace(" ", "_"),
                "params": list(args)
            }
            wsock.send(json.dumps(delete_command))
            delete_response = wsock.recv()

            detach_command = {
                "command": "detach",
                "params": [map_id]
            }
            wsock.send(json.dumps(detach_command))
            detach_response = wsock.recv()

            return ensure_json_response(delete_response)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}"
        })

def send_rotate_to_server(username: str, map_id: str, command: str, *args) -> str:
    """Send a rotate command to the server."""
    try:
        with create_websocket_connection() as wsock:
            if not wsock:
                return json.dumps({"status": "error", "message": "Could not connect to server"})

            initial_msg = wsock.recv()
            wsock.send(json.dumps({"username": username}))
            welcome_msg = wsock.recv()

            attach_command = {
                "command": "attach",
                "params": [map_id]
            }
            wsock.send(json.dumps(attach_command))
            attach_response = wsock.recv()

            rotate_args = list(args) + [map_id]
            rotate_command = {
                "command": command.lower().replace(" ", "_"),
                "params": rotate_args
            }
            wsock.send(json.dumps(rotate_command))
            rotate_response = wsock.recv()

            detach_command = {
                "command": "detach",
                "params": [map_id]
            }
            wsock.send(json.dumps(detach_command))
            detach_response = wsock.recv()

            return ensure_json_response(rotate_response)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}"
        })

def send_save_to_server(username: str, map_id: str, command: str) -> str:
    try:
        with create_websocket_connection() as wsock:
            if not wsock:
                return json.dumps({"status": "error", "message": "Could not connect to server"})

            initial_msg = wsock.recv()
            wsock.send(json.dumps({"username": username}))
            welcome_msg = wsock.recv()

            save_command = {
                "command": command.lower().replace(" ", "_"),
                "params": []
            }
            wsock.send(json.dumps(save_command))
            save_response = wsock.recv()

            return ensure_json_response(save_response)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}"
        })