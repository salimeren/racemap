from abc import ABC, abstractmethod
import random
import math
import json
import pickle

class Component(ABC):

    _registry = {"friction": "Friction cell slows the car down",
                 "Booster": "Booster cell increases speed.",
                 "Rock": "Stops the car",
                 "Slippery": "Changes the angle",
                 "turn90": "Rotates the car",
                 "straight": "Goes straight",
                 "fuel": "Fuel cell to refuel the cars",
                 "Ferrari": "A sports car",
                 "Merso" : "A sports car"
                 }
    
    @abstractmethod
    def __init__(self):
        super().__init__()

    @abstractmethod
    def desc(self):
        pass

    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def attrs(self):
        pass
    """
    @abstractmethod
    def __getattr__(self, attr):
        pass

    @abstractmethod
    def __setattr__(self, attr, value):
        pass
    """
    @abstractmethod
    def draw(self):
        pass

    @classmethod
    def list(self):

        return list(self._registry.items())

    @classmethod
    def create(self, type):

        if type == "booster":
            return BoosterCell()
        elif type == "checkpoint":
            return CheckpointCell()
        elif type == "friction":
            return FrictionCell()
        elif type == "rock":
            return ObstacleCell()
        elif type == "slippery":
            return SlipperyCell()
        elif type == "turn90":
            return Turn90Cell()
        elif type == "straight":
            return StraightCell()
        elif type == "fuel":
            return FuelCell()
        elif type == "Ferrari":
            return Ferrari()
        elif type == "Merso":
            return Merso()
        else:
            raise ValueError(f"Unknown component type: {type}, check components using list_components")

    @classmethod
    def register(type, cls):
        cls._registry[type] = cls

    @classmethod
    def unregister(type, cls):
        del cls._registry[type]

    def from_dict(self):
        pass

class ComponentFactory(Component):

    last_id = 0

    def __init__(self):
        self._components = {}
        self.owner = None

    def __getattr__(self, attr):
        return super().__getattr__(attr)
    def __setattr__(self, attr, value):
        return super().__setattr__(attr, value)
    def attrs(self):
        return super().attrs()
    def desc(self):
        print("Interface class of Component for the Repo")
    def draw(self):
        return super().draw()
    def type(self):
        return super().type()
    
    def create(self, type):
        
        print("OBJ TYPE " ,type)
        print("OBJ ID " , ComponentFactory.last_id)
        obj = super().create(type=type)
        
        print("OBJ CREATED")
        
        obj.id = ComponentFactory.last_id
        obj.map = self.owner
        
        self.owner.objects.append(obj)
        
        #if isinstance(obj, Car):
        print("rtyjuıopğg")
        ComponentFactory.last_id += 1

        print("fegtyrjkuı")
        self._components[type] =  obj
        
        print("şiwgrlemtnhojf")
        return obj

    def to_dict(self):
        if self._components is None:
            return {}
        return {
            component_type: component.to_dict()
            for component_type, component in self._components.items()
        }

    @classmethod
    def from_dict(cls, components_dict):
        factory = cls()
        for component_type, component_data in components_dict.items():
            component = Component.from_dict(component_data)
            factory._components[component_type] = component
        return factory


class Cell(Component):

    def __init__(self): #(self, row:int, col:int, rotation:int):
        print("INIT CELL")
        super().__init__()
        self.id = None
        self.map = None
        self.row = 0
        self.col = 0
        self.rotation = 0 # 0, 1, 2, 3
        print("INIT CELL FINISHED")

    def __getattr__(self, attr):
        
        raise f"{attr} is not supported"

    def __setattr__(self, attr, value):
        
        if attr == "row":
            object.__setattr__(self, attr, value)#self.row = value
        elif attr == "col":
            object.__setattr__(self, attr, value)#self.col = value
        elif attr == "rotation":
            object.__setattr__(self, attr, value)#self.rotation = value
        elif attr == "id":
            object.__setattr__(self, attr, value)
        elif attr == "map":
            object.__setattr__(self, attr, value)
        elif attr == "tip":
            object.__setattr__(self, attr, value)
        else:
            raise "Unsupported attribute."

    def attrs(self):
                
        return([("row",int), ("col", int), ("rotation", int)])

    def desc(self):
        return "Cell base class"

    def draw(self):
        pass

    def interact(self, car, y:int, x:int):
        pass

    def to_dict(self):
        return {
            "type":self.type(),
            "id": self.id,
            "row": self.row,
            "col": self.col,
            "rotation": self.rotation
        }

    @staticmethod
    def from_dict(data):
        if(data["type"] == "friction"):
            cell = FrictionCell()
        elif(data["type"] == "slippery"):
            cell = SlipperyCell()
        elif(data["type"] == "turn90"):
            cell = Turn90Cell()
        elif(data["type"] == "straight"):
            cell = StraightCell()
        elif(data["type"] == "fuel"):
            cell = FuelCell()

        cell.id = data["id"]
        cell.row = data["row"]
        cell.col = data["col"]
        cell.rotation = data["rotation"]
        return cell

class BoosterCell(Cell):

    def __init__(self):
    
        super().__init__()
        self.tip = "booster"

    def interact(self, car, y:int, x:int):
        
        car.speed *= 1.1

    def desc(self):
        return "Booster cell to increase speed"
    
    def type(self):
        return "booster"
    
    def draw(self):
        return "🚀"

class CheckpointCell(Cell):
    checkpoints = []
    def __init__(self):

        super().__init__()
        self.tip = "checkpoint"
        CheckpointCell.checkpoints.append(self)


    def interact(self, car, y:int, x:int):
        if self == CheckpointCell.checkpoints[car.next_checkpoint]:
            car.next_checkpoint += 1
            if(car.next_checkpoint == len(CheckpointCell.checkpoints)):
                car.stop()



    def desc(self):
        return "Checkpoint cell to create a checkpoint."

    def type(self):
        return "checkpoint"
    
    def draw(self):
        return "🏁"

    def to_dict(self):
        data = super().to_dict()
        data["checkpoints_index"] = CheckpointCell.checkpoints.index(self)
        return data

    @staticmethod
    def from_dict(data):
        checkpoint_cell = CheckpointCell()
        checkpoint_index = data.get("checkpoints_index", -1)
        if checkpoint_index != -1:
            CheckpointCell.checkpoints.insert(checkpoint_index, checkpoint_cell)
        return checkpoint_cell

class FuelCell(Cell):

    def __init__(self):
    
        super().__init__()
        self.tip = "fuel"

    def interact(self, car, y:int, x:int):
        
        car.fuel = car.maxfuel

    def desc(self):
        return "Fuel cell to refuel the cars."

    def type(self):
        return "fuel"
    
    def draw(self):
        return "⛽"

class FrictionCell(Cell):

    def __init__(self):
    
        super().__init__()
        self.tip = "friction"

    def interact(self, car, y:int, x:int):
        
        car.speed *= 0.8

    def desc(self):
        return "Friction cell to slow the car down."

    def type(self):
        return "friction"

    def draw(self):
        return "F"

class ObstacleCell(Cell):

    def __init__(self):
        
        print("INSIDE INIT ROCK")
        super().__init__()
        self.tip = "rock"
        print("ROCK INITED")

    def interact(self, car, y:int, x:int):
        
        car.speed = 0

    def desc(self):
        return "Obstacle cell to stop the car."

    def type(self):
        return "obstacle"

    def draw(self):
        return "🪨"

class SlipperyCell(Cell):

    def __init__(self):
        super().__init__()
        self.tip = "slippery"

    def interact(self, car, y: int, x: int):
        car.rotation += 1
        car.rotation = random.choice([0, 1, 2, 3])

    def desc(self):
        return "Slippery cell to change the direction"

    def type(self):
        return "slippery"

    def draw(self):
        return "❄️"

class Turn90Cell(Cell):

    def __init__(self):
    
        super().__init__()
        self.tip = "turn"

    def interact(self, car, y:int, x:int):
        
        car.speed *= 0.95
        """
        if self.rotation == 0:
            car.angle = 90
        elif self.rotation == 1:
            car.angle = 180
        elif self.rotation == 2:
            car.angle = 360
        else:
            car.angle = 0"""
        

    def desc(self):
        return "Change the direction of the car"        

    def type(self):
        return "turn90"

    def draw(self):

        if self.rotation == 0:
            return"┏"
        elif self.rotation == 1:
            return "┓"
        elif self.rotation == 2:
            return "┛"
        elif self.rotation == 3:
            return "┗"

class StraightCell(Cell):

    def __init__(self):
    
        super().__init__()
        self.tip = "straight"

    def interact(self, car, y:int, x:int):
        
        car.speed *= 0.95

    def desc(self):
        return "Straight cell, go straight ahead"     
    
    def type(self):
        return "straight"

    def draw(self):

        if self.rotation % 2 == 0:
            return "-"
        else:
            return "|"

class Car(Component):

    def __init__(self, model:str, map, driver:str, pos:tuple = (0,0), angle:int=0, topspeed:int=100, topfuel:int=100, speed:float=0.0, fuel:float=100.0):

        super().__init__()
        self.id = None
        self.model = model
        self.map = map
        self.driver = driver 
        self.pos = pos
        self.angle = angle
        self.topspeed = topspeed
        self.topfuel = topfuel
        self.speed = speed
        self.fuel = fuel

        self.carStarted = False
        self.accelFlag = False
        self.breakFlag = False
        self.turnLeftFlag = False
        self.turnRightFlag = False
        self.next_checkpoint = 0

    def attrs(self):

        attr_list = [(attr, type(value)) for attr, value in vars(self).items()]
        return attr_list
    
    def desc(self):
        return "Default car."

    def type(self):
        return type(self)

    def start(self):
        self.carStarted = True

    def stop(self):
        self.carStarted = False

    def accel(self):
        self.accelFlag = True    

    def breakd(self):
        self.breakFlag = True        

    def left(self):
        self.turnLeftFlag = True
    
    def right(self):        
        self.turnRightFlag = True

    def tick(self):
        if self.carStarted:
            row = int(self.pos[0] // self.map.cellsize)
            col = int(self.pos[1] // self.map.cellsize)
            if not self.map.cells[row][col]:
                self.speed = 2 ## set a minimum value
            else:
                for cell in self.map.cells[row][col]:
                    cell.interact(self, self.pos[0] % self.map.cellsize, self.pos[1] % self.map.cellsize)  

            ## assume tick per  0.1 second
                    
            if self.turnLeftFlag:
                self.turnLeftFlag = False   
                self.angle += 90
                if self.angle >=360:
                    self.angle -= 360
            
            if self.turnRightFlag:
                self.turnRightFlag = False
                self.angle -= 90
                if self.angle < 0:
                    self.angle += 360
            
            def get_acceleration(speed,  max_accel=30, decay_rate=0.015):
                    if speed >= self.topspeed:
                        return 0  # Acceleration is 0 at or beyond max_speed
                    accel = (max_accel * math.exp(-decay_rate * speed)) / 10
                    return accel  
                  
            if(self.accelFlag):
                acceleration = get_acceleration(self.speed) / 2
                self.speed += acceleration


            if(self.breakFlag):
                self.speed -= 2 

            distance = self.speed / 10 ## assuming tick per 0.1 second
            if self.fuel < ((distance / 100 ) * (self.speed / 100)): ## not enough fuel, go till zero, set fuel to zero
                distance = (self.fuel / ((distance / 100 ) * (self.speed / 100))) * distance
                self.fuel = 0 
            else:
                self.fuel = self.fuel - ((distance / 100 ) * (self.speed / 100)) ## have enough fuel, reduce it
            def move(distance_to_travel):
                

                yexceeded = False
                xexceeded = False
                negativey = False
                negativex = False
                
                
                newy = -self.speed * math.sin(math.radians(self.angle)) + self.pos[0]
                newx = self.speed * math.cos(math.radians(self.angle)) + self.pos[1]

                

                # Check for exceeding map boundaries and calculate remaining distance
                if newy > self.map.rows * self.map.cellsize:
                    distance_traveled = (self.map.rows * self.map.cellsize - self.pos[0]) / math.sin(math.radians(self.angle))
                    remaining_distance = distance_to_travel - distance_traveled
                    newy = self.map.rows * self.map.cellsize
                    yexceeded = True

                elif newy < 0:
                    distance_traveled = -self.pos[0] / math.sin(math.radians(self.angle))
                    remaining_distance = distance_to_travel - distance_traveled
                    newy = 0
                    negativey = True
                else:
                    remaining_distance = 0

                if newx > self.map.cols * self.map.cellsize:
                    distance_traveled = (self.map.cols * self.map.cellsize - self.pos[1]) / math.cos(math.radians(self.angle))
                    remaining_distance = distance_to_travel - distance_traveled
                    newx = self.map.cols * self.map.cellsize
                    xexceeded = True

                elif newx < 0:
                    distance_traveled = -self.pos[1] / math.cos(math.radians(self.angle))
                    remaining_distance = distance_to_travel - distance_traveled
                    newx = 0
                    negativex = True
                else:
                    remaining_distance = 0

                # Reflect the car's direction according to edge normal
                if xexceeded or negativex:
                    self.angle = 180 - self.angle
                    if self.angle < 0:
                        self.angle += 360  # Keep angle in [0, 360)

                if yexceeded or negativey:
                    self.angle = 360 - self.angle

                self.pos = (newy,newx)

                # Calculate new position after reflection using the remaining distance


                if remaining_distance > 0:
                    move(remaining_distance)
            
            move(distance)

            if(self.breakFlag):
                self.speed -= 10 
                self.breakFlag = False

            ## move it with average speed, then set normal speed

            if(self.accelFlag):
                self.speed += acceleration
                self.accelFlag = False

            self.accelFlag = False
            self.breakFlag = False
            self.turnLeftFlag = False
            self.turnRightFlag = False

    def to_dict(self):
        return {
            "id": self.id,
            "model": self.model,
            "driver": self.driver,
            "pos": self.pos,
            "angle": self.angle,
            "topspeed": self.topspeed,
            "topfuel": self.topfuel,
            "speed": self.speed,
            "fuel": self.fuel,
            "carStarted": self.carStarted,
            "accelFlag": self.accelFlag,
            "breakFlag": self.breakFlag,
            "turnLeftFlag": self.turnLeftFlag,
            "turnRightFlag": self.turnRightFlag,
            "next_checkpoint": self.next_checkpoint,
        }

    @staticmethod
    def from_dict(data):
        car = Car(
            model=data["model"],
            driver=data["driver"],
            pos=tuple(data["pos"]),
            angle=data["angle"],
            topspeed=data["topspeed"],
            topfuel=data["topfuel"],
            speed=data["speed"],
            fuel=data["fuel"]
        )
        car.id = data["id"]
        car.carStarted = data["carStarted"]
        car.accelFlag = data["accelFlag"]
        car.breakFlag = data["breakFlag"]
        car.turnLeftFlag = data["turnLeftFlag"]
        car.turnRightFlag = data["turnRightFlag"]
        car.next_checkpoint = data["next_checkpoint"]



        return car


class Ferrari(Car):

    def __init__(self, model="Ferrari", map=None, driver=None, pos=(0,0), angle=0, topspeed=250, topfuel=100, speed=0.0, fuel=100):
        super().__init__(model, map, driver, pos, angle, topspeed, topfuel, speed, fuel)
        self.tip = "ferrari"
        
    def draw(self):

        return "🏎️"

    def desc(self):
        return "Ferrari, sports car."

class Merso(Car):

    def __init__(self, model="Merso", map=None, driver=None, pos=(0,0), angle=0, topspeed=250, topfuel=100, speed=0.0, fuel=100):
        super().__init__(model, map, driver, pos, angle, topspeed, topfuel, speed, fuel)
        self.tip = "merso"

    def draw(self):

        return "M"

    def desc(self):
        return "Merso, sports car."

