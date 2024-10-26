from typing import Optional
from functools import reduce
from datetime import datetime
from requests import put
import json
import os
from requests.auth import HTTPBasicAuth

file_name = 'image/server-logger/test.txt'

debug = True

leaderboard_url = os.getenv("LEADERBOARD_URL")
leaderboard_name = os.getenv("LEADERBOARD_NAME")
game_name = os.getenv("GAME_NAME")
leaderboard_user = os.getenv("LEADERBOARD_USER")
leaderboard_password = os.getenv("LEADERBOARD_PASSWORD")
max_points = os.getenv("MAX_POINTS", 60)

class Player:
    current_rank = 0
    
    def __init__(self, name: str):
        self.name_: str = name
        self.active_: bool = True
        self.rank_: int = 0
        self.id_: int = -1
        self.points_: int = 0    
    
    def set_points(self, rank: int):
        self.rank_ = rank
        self.points_ = max_points - self.rank_ + 1
        if self.rank_ <=3:
            self.points_ += (3 - self.rank_ + 1)
        pass    
    
    def get_name(self) -> str:
        return self.name_
        pass
    
    def activate(self):
        self.active_ = True
        self.rank_ = 0
        
    def kill(self):
        self.deactivate()
    
    def deactivate(self):
        self.active_ = False
        self.rank_ = Player.current_rank = Player.current_rank + 1
    
    def is_active(self) -> bool:
        return self.active_
    
    def set_id(self, id: int):
        self.id_ = id
        
    def get_id(self) -> int:
        return self.id_
    
    def get_rank(self) -> int:
        return self.rank_
    
    def get_points(self) -> int:
        return self.points_
    
    def __str__(self) -> str:
        return f"{self.name_} (ID: {self.id_}) {self.points_}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
def action(func):
    def wrapper(self, *args, **kwargs):
        if not self.stopped_:
            func(self, *args, **kwargs)
    return wrapper

class Manager:
    
    def __init__(self):
        self.players_: list[Player] = []
        self.stopped_: bool = False 
        self.counter = 1
        
    def feed_line(self, line: str):
        if self.stopped_:
            return
        
        line = line.replace("\n", "").replace("\r", "")
        if line.startswith("[Server] - RoomInit from: "):
           self.player_join(line)
        elif line.startswith("[Server] - Player left: "):
            self.player_leave(line)
        elif len(line.split(':')) >= 2 and f"{reduce(lambda e1,e2: f'{e1}:{e2}', line.split(':')[0:1])}: Initing playerindex" in self.get_list_of_player_init_logs():
            self.assign_id(line)
        elif line.startswith("[Server] - Team:"):
            self.player_event(line)
        elif line == "[Server] - GameStateChangedCommand : Ended":
            self.stopped_ = True
            self.generate_points()
            self.print_to_file()
            send_to_leaderboard_service(list(map(lambda x: {'player_name': x.get_name(), 'points': x.get_points()}, self.get_all_players())))
        pass
    
    def print_to_file(self):
        if debug:
            print(self.__str__())
        else:
            with open(f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}", "w") as file:
                print(self.__str__())
                file.write(self.__str__())
                pass
        pass
    
    def generate_points(self):
        self.players_.sort(key=lambda x: x.get_rank(), reverse=True)
        counter = 0
        for p in self.players_:
            p.set_points((counter := counter + 1))
    
    @action
    def player_join(self, line: str):
        name = line.split(":")[1][1:-3]
        found_player: Optional[Player] = self.get_player_from_list(name)
        print(f"{name} joined")
        if found_player:
            found_player.activate()
        else:
            self.add_player(name)
       
    @action
    def player_leave(self, line: str):
        name = line[24:]
        found_player: Optional[Player] = self.get_player_from_list(name)
        if found_player:
            print(f"{found_player.get_name()} left")
            found_player.deactivate()
    
    @action
    def assign_id(self, line: str):
        id: int = int(line.split(":")[3])
        name: str = line.split(":")[0][11:]
        found_player: Player = self.get_player_from_list(name)
        if found_player:
            found_player.set_id(id)
            
    @action
    def player_event(self, line: str):
        id = int(line.split(":")[1].split(" ")[1])
        found_player: Player = self.get_player_from_list_with_id(id)
        if found_player:
            print(f"{found_player.name_} killed!")
            found_player.kill()
    
    def get_list_of_player_init_logs(self) -> list[str]:
        return list(map(lambda x: f"[Server] - {x.get_name()}: Initing playerindex", self.players_))

    def get_player_from_list(self, name: str) -> Optional[Player]:
        return next(filter(lambda x: x.get_name() == name, self.players_), None)
        pass
    
    def get_player_from_list_with_id(self, id: int) -> Optional[Player]:
        return next(filter(lambda x: x.get_id() == id, self.players_), None)
        pass
    
    def add_player(self, name: str) -> Player:
        p: Player = Player(name)
        self.players_.append(p)
        return p
        pass
    
    def get_all_players(self) -> list[Player]:
        return self.players_
        pass
    
    def __str__(self) -> str:
        self.players_.sort(key=lambda x: x.get_rank(), reverse=False)
        pos = 0
        res = "======================================\n"
        for p in self.players_:
            res += f"{(pos := pos + 1)}. {p}\n"
        res += "=====================================\n"
        return res
        pass
    
    def __repr__(self) -> str:
        return self.__str__()


def send_to_leaderboard_service(request: list[dict[str, any]]):
    if debug:
        print(request)
    else:
        # put(f"{leaderboard_url}/leaderboard/multigame/{leaderboard_name}/{game_name}", data=json.dumps(request), auth=HTTPBasicAuth("game", "1234"))
        pass
    pass

def main():
    global debug
    debug = True
    # Continuously read the output line by line
    with open(file_name, "r") as file:
        manager: Manager = Manager()
        for line in file.readlines():
            manager.feed_line(line)
            pass
        pass
        

    
if __name__ == "__main__":
    main()
    