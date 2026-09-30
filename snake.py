from dataclasses import dataclass
from typing import Literal
import random
import curses
import time

type Direction = Literal["UP", "DOWN", "RIGHT", "LEFT"]

_BASE : dict[Direction, Direction] = {"UP": "DOWN", "RIGHT": "LEFT"}
OPPOSITES: dict[Direction, Direction] = {v: k for k, v in _BASE.items() } | _BASE

@dataclass(frozen=True)
class Case:
    x: int
    y: int

@dataclass
class Food:
    position: Case

class Snake:
    def __init__(self):
        self.body: list[Case] = [Case(10, 2), Case(10, 1), Case(10, 0)]
        self.direction: Direction = "DOWN"
        self.last_direction: Direction = "DOWN"

    def get_head(self)-> Case:
        return self.body[0]

    def get_body_set(self)->set[Case]:
        return set(self.body)

    def increase_length(self):
        self.body.append(self.body[-1])
    
    def move(self):
        head: Case = self.body[0]
        match self.direction:
            case "UP":
                new_head: Case = Case(head.x, head.y-1)
            case "DOWN":
                new_head: Case = Case(head.x, head.y+1)
            case "RIGHT":
                new_head: Case = Case(head.x+1, head.y)
            case "LEFT":
                new_head: Case = Case(head.x-1, head.y)
        self.body.insert(0, new_head)
        self.body.pop()
        self.last_direction = self.direction

    def set_direction(self, direction: Direction):
        if OPPOSITES[self.last_direction] == direction:
            return
        self.direction = direction

class Game:
    width: int = 21
    height: int = 15

    def __init__(self):
        self.snake: Snake = Snake()
        self.is_running: bool = True
        self.won: bool = False
        self.speed: float = SPEED
        self.all_cases : set[Case] = {Case(x, y) for x in range(self.width) for y in range (self.height)}
        self.score : int = 0
        self.food: Food | None = self.spawn_food()

    def spawn_food(self) -> Food | None:
        free_cases = self.all_cases - self.snake.get_body_set()
        if not free_cases:
            return None
        position = random.choice(list(free_cases))
        return Food(position)

    def is_collision(self):
        snake_head = self.snake.get_head()
        if snake_head.x < 0 or snake_head.x >= self.width:
            return True
        elif snake_head.y < 0 or snake_head.y >= self.height:
            return True
        return snake_head in self.snake.body[1:]

    def end_game(self):
        self.is_running = False

    #snake char = "██"
    #food char  = "▓▓"
    #empty char = "░░"

    def display_grid(self):
        body_set: set[Case] = self.snake.get_body_set()
        grid: str = ""
        for i in range(self.height):
            for j in range(self.width):
                current_case = Case(j, i)
                if self.food is not None and self.food.position == current_case:
                    grid += "▓▓"
                elif current_case in body_set:
                    grid +="██"
                else:
                    grid += "░░"
            grid += "\n"
        return grid

SPEED = 0.15
MIN_SPEED = 0.05

def play(screen) -> Game:
    screen.nodelay(True)
    game = Game()
    next_tick = time.monotonic()

    while game.is_running:
        res = screen.getch()

        while res != -1:
            match res:
                case curses.KEY_UP:
                    game.snake.set_direction("UP")
                case curses.KEY_DOWN:
                    game.snake.set_direction("DOWN")
                case curses.KEY_RIGHT:
                    game.snake.set_direction("RIGHT")
                case curses.KEY_LEFT:
                    game.snake.set_direction("LEFT")
            res = screen.getch()
        if time.monotonic() >= next_tick:
            screen.erase()
            screen.addstr(0, 0, game.display_grid())
            screen.addstr(game.height + 1, 0, "Score: "+str(game.score))
            screen.refresh()
            game.snake.move()
            if game.food is not None and game.food.position == game.snake.get_head():
                game.score+=1
                game.snake.increase_length()
                game.speed = max(MIN_SPEED, game.speed * 0.95)
                game.food = game.spawn_food()
                if game.food is None:
                    game.won = True
                    game.end_game()
            if game.is_collision():
                game.end_game()
            next_tick += game.speed
        time.sleep(0.01)

    return game

def main(screen):
    curses.curs_set(0)

    while True:
        game = play(screen)
        screen.nodelay(False)
        if game.won:
            screen.addstr(game.height + 2, 0, "YOU WIN! Final score: "+str(game.score))
        else:
            screen.addstr(game.height + 2, 0, "GAME OVER, YOU LOSE. Final score: "+str(game.score))
        screen.addstr(game.height + 3, 0, "R: play again    Q: quit")
        screen.refresh()
        curses.flushinp()

        while True:
            res = screen.getch()
            if res == ord("r"):
                break
            if res == ord("q"):
                return

if __name__ == "__main__":
    curses.wrapper(main)