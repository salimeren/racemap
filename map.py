import components
import threading
import time

class Map:

    def __init__(self, cols:int, rows:int, cellsize:int, bgcolor:str):
        
        self.cols = cols
        self.rows = rows
        self.cellsize = cellsize
        self.bgcolor = bgcolor


        self.cells = [self.cols*[None] for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j] = []

        self.components = components.ComponentFactory()# component, pos pairs
        self.components.owner = self
        
        self.objects = []

        self.game_active = False
        self.tick_count = 0
        self.notification_period = -1
        self.server = None

    def __getitem__(self, pos:tuple):

        row, col = pos
        
        try:
            return self.cells[row][col][-1]
        except IndexError:
            raise "Given index exceeds map size"

    def __setitem__(self, pos:tuple, component):

        row, col = pos
        
        if isinstance(component, components.Cell):
            component.row = row
            component.col = col
            
            self.cells[row][col].append(component)
            
        elif isinstance(component, components.Car):            
            component.pos = (row*self.cellsize, col*self.cellsize)
            #component.pos[1] = col*self.cellsize
            
            self.cells[row][col].append(component)

    def __delitem__(self, pos:tuple):

        row, col = pos
        self.cells[row][col] = []

    def delobj(self, id):
        
        for row in self.cells:
            for col in row:
                for elem in col:
                    if elem.id == id:
                        col.remove(elem)

    def getxy(self, y:int, x:int):

        return self.cells[x%self.cellsize][y%self.cellsize][-1]

    def place(self, obj, y:int, x:int):

        self.components[obj] = (x, y)

    def view(self, y:int, x:int, height:int, width:int):

        pass

    def to_dict(self):


        a = [
            [
                [
                    cell.to_dict() if cell and isinstance(cell, components.Component) else None
                    for cell in col  # Iterate through each component in a cell
                ]
                for col in row  # Iterate through each column in the row
            ]
            for row in self.cells  # Iterate through each row in self.cells
        ]

        b = self.components.to_dict() if self.components else {}

        map_dict = {
            "cols": self.cols,
            "rows": self.rows,
            "cellsize": self.cellsize,
            "bgcolor": self.bgcolor,
            "cells": a,
            "components": b,
            "game_active": self.game_active,
            "tick_count": self.tick_count,
            "notification_period": self.notification_period,
            "server": None,
        }
        return map_dict


    @classmethod
    def from_dict(cls, map_dict):
        # Initialize the Map object
        map_obj = cls(
            cols=map_dict["cols"],
            rows=map_dict["rows"],
            cellsize=map_dict["cellsize"],
            bgcolor=map_dict["bgcolor"],
        )

        map_obj.cells = [
            [
                [
                    components.Component.from_dict(map_dict["components"][cell_data["type"]])
                    if cell_data else None
                    for cell_data in col  # Iterate through each component in a cell
                ]
                for col in row  # Iterate through each column in the row
            ]
            for row in map_dict["cells"]  # Iterate through each row in map_dict["cells"]
        ]

        map_obj.components = components.ComponentFactory.from_dict(map_dict["components"])

        map_obj.game_active = map_dict["game_active"]
        map_obj.tick_count = map_dict["tick_count"]
        map_obj.notification_period = map_dict["notification_period"]
        map_obj.server = map_dict["server"]

        return map_obj

    def start(self, tick_interval=0.5, notification_interval=2, users = []):

        if hasattr(self, "game_active") and self.game_active:
            print("Game mode is already active for this map.")
            return
        self.game_active = True
        self.tick_count = 0
        self.notification_period = notification_interval / tick_interval
        try:
            while self.game_active:
                # Call tick on all cars
                for _, component in self.components._components.items():
                    if isinstance(component, components.Car):
                        component.tick()
                self.tick_count += 1
                # Notify users every P tick completions
                if self.tick_count >= self.notification_period:
                    self.notify_users(users)
                    self.tick_count = 0
                time.sleep(tick_interval)
        except Exception as e:
            print(f"Error during game loop on map {id(self)}: {e}")
            self.game_active = False
        print(f"Game mode ended for the map (ID: {id(self)}).")


    def stop(self):
        if hasattr(self, "game_active") and self.game_active:
            self.game_active = False
            print(f"Game mode stopped for the map (ID: {id(self)}).")
        else:
            print("Game mode is not active for this map.")

    def notify_users(self,users):

        if hasattr(self, "server") and self.server:
            message = f"Game mode update for map {id(self)}:\n{self.draw()}"
            # Notify all attached users
            self.server.notify_users_on_map(users, message)

    def draw(self):
        result = []

        cars = []

        for _, component_obj in self.components._components.items():
            if isinstance(component_obj, components.Car):
                cars.append((component_obj,
                             (int(component_obj.pos[0] / self.cellsize), int(component_obj.pos[1] / self.cellsize))))

        bar = "\n" + "----" * self.cols
        result.append(bar)

        for i in range(self.rows):
            row_representation = " | "
            for j in range(self.cols):
                car_printed = False

                for car in cars:
                    if car[1][0] == i and car[1][1] == j:
                        car_printed = True
                        row_representation += car[0].draw() + " | "
                        break

                if not car_printed:
                    if len(self.cells[i][j]) > 0 and isinstance(self.cells[i][j][-1], components.Cell):
                        row_representation += self.cells[i][j][-1].draw()
                        row_representation += " | "
                    else:
                        row_representation += "X | "

            result.append(row_representation)
            result.append(bar)
        for car in cars:

            car_obj = car[0]
            car_info = f"Model: {car_obj.model} Driver: {car_obj.driver} Position: {car_obj.pos} Speed: {car_obj.speed} Fuel: {car_obj.fuel}"
            result.append(car_info)  # Add car information at the end

        cars.sort(key=lambda car: car[0].next_checkpoint, reverse=True)

        car_ids_ordered = [f"{car[0].model},({car[0].next_checkpoint})" for car in cars]
        result.append(f"\nCars ordered by next_checkpoint: {car_ids_ordered}")

        return "\n".join(result)

    def view(self, y, x, height, width):

        return View(self, y, x, height, width)


class View:
    def __init__(self, parent_map, start_row, start_col, height, width):
       

        self.parent_map = parent_map
        self.start_row = start_row // parent_map.cellsize
        self.start_col = start_col // parent_map.cellsize
        self.view_rows = height // parent_map.cellsize
        self.view_cols = width // parent_map.cellsize

    def __getitem__(self, pos):
        row, col = pos
        actual_row = self.start_row + row
        actual_col = self.start_col + col
        return self.parent_map[actual_row, actual_col]

    def __setitem__(self, pos, component):
        row, col = pos
        actual_row = self.start_row + row
        actual_col = self.start_col + col
        self.parent_map[actual_row, actual_col] = component

    def __delitem__(self, pos):
        row, col = pos
        actual_row = self.start_row + row
        actual_col = self.start_col + col
        del self.parent_map[actual_row, actual_col]

    def draw(self):

        bar = "\n" + "----" * self.view_cols
        for i in range(self.view_rows):
            print(" | ", end="")
            for j in range(self.view_cols):
                actual_row = self.start_row + i
                actual_col = self.start_col + j
                if len(self.parent_map.cells[actual_row][actual_col]) > 0 and isinstance(
                    self.parent_map.cells[actual_row][actual_col][-1], components.Cell
                ):
                    self.parent_map.cells[actual_row][actual_col][-1].draw()
                    print(" | ", end="")
                else:
                    print("X", end="")
                    print(" | ", end="")
            print(bar)