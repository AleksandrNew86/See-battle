from random import randint


class WrongDots(Exception):
    pass


class TheDotIsOutOfBoard(WrongDots):
    def __str__(self):
        return f'Точка за пределами поля!'


class TheDotIsBusy(WrongDots):
    def __str__(self):
        return f'Точка на поле занята!'


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, length, first_dot, direction_ship):
        self.length = length
        self.first_dot = first_dot
        self.direction_ship = direction_ship
        self.lives = length

    def dots(self):
        dots_ship = []
        for i in range(self.length):
            if self.direction_ship == 0:
                x = self.first_dot.x
                y = self.first_dot.y + i
                dots_ship.append(Dot(x, y))
            else:
                x = self.first_dot.x + i
                y = self.first_dot.y
                dots_ship.append(Dot(x, y))
        return dots_ship


class Board:
    def __init__(self, size=6, hidden=True):
        self.size = size
        self.hidden = hidden
        self.count_alive_ship = 6
        self.field = [["0"] * size for _ in range(self.size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for ship_row in ship.dots():
            if self.out(ship_row):
                raise TheDotIsOutOfBoard()
            if ship_row in self.busy:
                raise TheDotIsBusy()
        for ship_row in ship.dots():
            self.field[ship_row.x][ship_row.y] = "■"

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, view=False):
        around_ship = [(-1, -1), (-1, 0), (-1, 1),
                       (0, -1), (0, 0), (0, 1),
                       (1, -1), (1, 0), (1, 1)]
        for i in ship.dots():
            for n, value in enumerate(around_ship):
                x = i.x + value[0]
                y = i.y + value[1]
                if Dot(x, y) not in self.busy and not self.out(Dot(x, y)):
                    self.busy.append(Dot(x, y))
                if (Dot(x, y) in ship.dots()) or self.out(Dot(x, y)):
                    continue
                if view:
                    self.field[x][y] = "*"

    def __str__(self):
        res = "  |"
        for i in range(1, self.size+1):
            if i == self.size:
                res += f' {i}'
            else:
                res += f' {i} |'

        for i in range(len(self.field)):
            res += f'\n{i+1}'
            for j, row in enumerate(self.field[i]):
                if self.hidden:
                    row = row.replace("■", "0")
                res += f' | {row}'
        return res

    def out(self, dot):
        if self.size <= dot.x or dot.x < 0 or self.size <= dot.y or dot.y < 0:
            return True
        else:
            return False

    def shot(self, dot):
        if dot in self.busy:
            raise TheDotIsBusy()
        elif self.out(dot):
            raise TheDotIsOutOfBoard()
        else:
            self.busy.append(dot)
            for ship in self.ships:
                if dot in ship.dots():
                    self.field[dot.x][dot.y] = "X"
                    ship.lives -= 1
                    if ship.lives == 0:
                        print(f'Ход {dot.x + 1} {dot.y + 1}: Корабль убит!')
                        self.count_alive_ship -= 1
                        self.contour(ship, view=True)
                        return "Destroyed"
                    else:
                        print(f'Ход {dot.x + 1} {dot.y + 1}: Корабль ранен!')
                        return "Wounded"
            else:
                print(f'Ход {dot.x + 1} {dot.y + 1}: Мимо!')
                self.field[dot.x][dot.y] = "T"
                return False

    def begin(self):
        self.busy = []


class User:
    def __init__(self, my_board, enemy_board):
        self.my_board = my_board
        self.enemy_board = enemy_board

    def ask(self):
        while True:
            target = input("Ваш ход: ").split()
            if len(target) != 2:
                print("Введено неверное количество координат!")
                continue
            if not target[0].isdigit() or not target[1].isdigit():
                print("Введеные координаты не числа!")
                continue
            x = int(target[0])
            y = int(target[1])
            return Dot(x-1, y-1)

    def move(self):
        while True:
            try:
                return self.enemy_board.shot(self.ask())
            except WrongDots as e:
                print(e)


class Computer:
    def __init__(self, my_board, enemy_board, size=6, wounded=False):
        self.size = size
        self.my_board = my_board
        self.enemy_board = enemy_board
        self.wounded = wounded
        self.last_shot = None
        self.direction = [True, True, True, True]
        self.attempt = 1

    def move(self):
        if not self.wounded:
            while True:
                x = randint(0, self.size - 1)
                y = randint(0, self.size - 1)
                self.last_shot = Dot(x, y)
                try:
                    return self.enemy_board.shot(self.last_shot)
                except WrongDots:
                    continue
        else:
            while True:
                if self.direction[0]:
                    local_direction = 0
                    dot_next_shot = Dot(self.last_shot.x - self.attempt, self.last_shot.y)
                elif self.direction[1]:
                    local_direction = 1
                    dot_next_shot = Dot(self.last_shot.x + self.attempt, self.last_shot.y)
                elif self.direction[2]:
                    local_direction = 2
                    dot_next_shot = Dot(self.last_shot.x, self.last_shot.y - self.attempt)
                else:
                    local_direction = 3
                    dot_next_shot = Dot(self.last_shot.x, self.last_shot.y + self.attempt)
                try:
                    dot = self.enemy_board.shot(dot_next_shot)
                except WrongDots:
                    self.direction[local_direction] = False
                    self.attempt = 1
                    continue
                if dot == "Wounded":
                    if local_direction == 0 or local_direction == 1:
                        self.direction[2] = False
                        self.direction[3] = False
                    else:
                        self.direction[0] = False
                        self.direction[1] = False
                    self.attempt += 1
                    continue
                elif dot == "Destroyed":
                    self.attempt = 1
                    for j in range(len(self.direction)):
                        self.direction[j] = True
                    self.wounded = False
                    return "Destroyed"
                else:
                    self.attempt = 1
                    self.direction[local_direction] = False
                    return False


class Game:
    def __init__(self):
        self.list_ships = [4, 2, 2, 1, 1, 1]
        self.size = 6
        self.user_board = self.ready_board()
        self.user_board.hidden = False
        self.comp_board = self.ready_board()
        self.user = User(self.user_board, self.comp_board)
        self.comp = Computer(self.comp_board, self.user_board, self.size)

    def attempt_board(self):
        b = Board()
        for i in self.list_ships:
            calls_number = 0
            while True:
                calls_number += 1
                try:
                    ship = Ship(i, Dot(randint(0, self.size-1), randint(0, self.size-1)), randint(0, 1))
                    b.add_ship(ship)
                    break
                except WrongDots:
                    if calls_number == 1000:
                        return None
                    continue
        b.begin()
        return b

    def ready_board(self):
        while True:
            b = self.attempt_board()
            if b is None:
                continue
            else:
                return b

    def greet(self):
        print(f'{"_" * 60}\n\
Приветствую тебя в игре Морской Бой!\n\
Ты играешь с компьютером.\n\
На полях расставлены твои корабли и корабли противника\n\
Твой первый ход в формате \"число пробел число\", например: 0 1\n\
Если ты попадаешь в корабль то твой ход повторяется\n\
В случае промаха ходит компьютер\n\
Кто первый убьет все корабли ({len(self.list_ships)} штук), тот выиграл\n\
Удачи Адмирал!!!')

    def loop(self):
        step = 1
        while True:
            if step % 2:
                print("_" * 60)
                print("Твоя доска:")
                print(self.user_board)
                print("_" * 60)
                print("Доска врага:")
                print(self.comp_board)
                repeat = self.user.move()
                if self.comp_board.count_alive_ship == 0:
                    print("Твоя доска:")
                    print(self.user_board)
                    print("_" * 60)
                    print("Доска врага:")
                    print(self.comp_board)
                    print("Поздравляю! Ты победил!")

                    break
                if repeat:
                    continue
                else:
                    step += 1
            else:
                print("_" * 60)
                print("Ход компьютера:")
                repeat = self.comp.move()
                if self.user_board.count_alive_ship == 0:
                    print("Твоя доска:")
                    print(self.user_board)
                    print("_" * 60)
                    print("Доска врага:")
                    print(self.comp_board)
                    print("К сожалению компьютер выиграл(")

                    break
                if repeat == "Wounded":
                    self.comp.wounded = True
                    continue
                elif repeat == "Destroyed":
                    continue
                else:
                    step += 1


g = Game()
g.greet()
g.loop()
