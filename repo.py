from map import Map
from components import Component
from components import ComponentFactory
import json
import os


class Repo:

    _instance = None

    def __init__(self):

        self.objects = dict()   # id - object pairs
        self.users = dict()     # userid - list of ids of objects attched 
        self.objowners = dict()   # id - list of userids who use the object
        self.components = ComponentFactory()
        self.component_dict = {}
        self.component_dict2 = {}

    def load(self, filename='repo_data.json'):
        def cast_numbers(data):
            """Recursively cast numeric values and keys to integers."""
            if isinstance(data, dict):
                return {cast_numbers(key): cast_numbers(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [cast_numbers(item) for item in data]
            else:
                # Try to cast the value to an integer
                try:
                    return int(data)
                except (ValueError, TypeError):
                    return data

        try:
            with open(filename, 'r') as file:
                data = json.load(file)

                data = cast_numbers(data)

                self.objects = {
                    obj_id: Map.from_dict(obj_data) for obj_id, obj_data in data.get('objects', {}).items()
                }
                self.users = data.get('users', {})
                self.objowners = data.get('objowners', {})
                self.component_dict = data.get('component_dict', {})
                self.components.id_counter = data.get('id_counter', 0)

        except FileNotFoundError:
            print(f"Warning: The file '{filename}' was not found. A new file will be created.")
            self.objects = {}
            self.users = {}
            self.objowners = {}
            self.component_dict = {}

            self.save(filename)
        except json.JSONDecodeError:
            print(f"Error: The file '{filename}' is not a valid JSON file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def save(self, filename='repo_data.json'):

        k = {obj_id: obj.to_dict() for obj_id, obj in self.objects.items()}


        data = {

            'objects': k,
            'users': self.users,
            'objowners': self.objowners,
            'component_dict': {key: component.to_dict() for key, component in self.component_dict.items()},
            'id_counter' : self.components.id_counter
        }


        try:
            with open(filename, 'w') as file:

                json.dump(data, file, indent=4)
                print(f"Data saved to {filename}.")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def create(self, *args):

        self.objects[args[0]] = Map(*(args[1:]))

        obj_id = args[0]
        if obj_id not in self.objowners:
            self.objowners[obj_id] = []

    def list(self):

        return list(self.objects.items())

    def listattached(self, user:str):

        return self.users[user]

    def attach(self, id:int, user:str):
    
        #if user in list(self.users.keys()):

        if id in list(self.objects.keys()):

            if not user in list(self.users.keys()):
                self.users[user] = []

            if not id in list(self.objowners.keys()):
                self.objowners[id] = []

            self.users[user].append(id)
            self.objowners[id].append(user)

            return self.objects[id]


        else:
            raise ValueError(f"Object with given id {id} does not exist.")

    def detach(self, id:int, user:str):
        
        if user in list(self.users.keys()):
            
            if id in list(self.objects.keys()):
                
                self.users[user].remove(id)
                self.objowners[id].remove(user)

            else:
                raise f"Object with given id {id} does not exist."
            
        else:
            raise f"User with given id {user} does not exist."

    def delete(self, id: int):
        if id in self.objects:  # Check if the key exists in the dictionary
            del self.objects[id]
        else:
            raise KeyError(f"Object with given id {id} does not exist.")