from random import *
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException): # для размещения
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        # Переопределяем метод сравнения для точек
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f'({self.x},{self.y})'

class Ship:
    def __init__(self, length, Dot, direction):
        self.length = length
        self.bow = Dot
        self.direction = direction
        self.lives = length  # Изначально количество жизней равно длине корабля

    def hit(self,dot):
        return dot in self.get_ship_dots

    @property
    def get_ship_dots(self):    # Метод для получения всех точек корабля
        ship_points = []  # тут хранятся экземпляры нашего класса Dot(x,y)
        x, y = self.bow.x, self.bow.y # распакуем точки полученные от ЭК Dot атрибутом bow
        for i in range(self.length):
            ship_points.append(Dot(x, y))
            if self.direction == "г": #горизонтально
                x += 1
            if self.direction == "в":  #вертикально
                y += 1 # добавляем в список экземпляры нашего класса Dot(x,y)
        return ship_points

    def __repr__(self):
        return f'Длина {self.length}, жизни {self.lives}, координаты {self.get_ship_dots}'


class Board:
    def __init__(self, hid=False, size = 7):
        self.size = size
        self.hid = hid
        self.dead_ships =0
        self.field = [[' ' if (j==0 and i ==0) else i if j == 0 else j if i == 0 else  '0' for j in range(7)] for i in range(7)]
        self.ships = []
        self.busy = []

    def __str__(self):
        # Метод для отображения доски в консоли
        result = ""
        for i in self.field:
            for j in i:
                result += str(j) + ' | '
            result += '\n'
        if self.hid == False:
            result = result.replace("■", '0')
        return result

    def out(self,dot):
        return 1 <= dot.x < self.size and 1 <= dot.y < self.size

    def contour(self, ship, in_game=False):
        # Метод для обводки корабля по контуру
        for dot in ship.get_ship_dots:
            x, y = dot.x, dot.y
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (self.out(Dot(x+i,y+j))) and Dot(x+i,y+j) not in self.busy:
                        if in_game == True:
                            self.field[x + i][y + j] = "."  #если атрибут для отображения True - меняем все 0 на .
                        self.busy.append(Dot(x+i,y+j)) # в любом случае добавили все точки, контура в наши занятые точки,
                        #чтобы не было проблем с добавлением кораблей

    def add_ship(self,ship, in_game = False):
        for dot in ship.get_ship_dots:
            if not self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.get_ship_dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship) # сразу добавили корабль в наш список кораблей доски.
        self.contour(ship, in_game) #сразу обвели контру этого корабля

    def shot(self,dot):
        if not self.out(dot):
            raise BoardOutException()
        if dot in self.busy:
            raise BoardUsedException()
        self.busy.append(dot)

        for ship in self.ships:
            if ship.hit(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = 'X'
                if ship.lives == 0:
                    self.contour(ship,True)
                    self.dead_ships += 1
                    print('Корабль потоплен!')
                    return False
                else:
                    print('Попал по кораблю!')
                    return True
        self.field[dot.x][dot.y] = 'T'
        print('Мимо!')
        return False

    def new_game(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board
    def ask(self):
        pass
    def move(self):
        while True:
            try:
                move = self.ask()
                repeat = self.enemy_board.shot(move)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        dot = Dot(randint(1,6),randint(1,6))
        print(f'Компьютер походил так: {dot.x} {dot.y}')
        return dot
class User(Player):
    def ask(self):
        while True:
            dots = input("Ваш ход: ").split()

            if len(dots) != 2:
                print('Ввели не правильные координаты')
                continue
            x = dots[0]
            y = dots[1]
            if not x.isdigit() and y.isdigit():
                print('Вы ввели не числа')
                continue
            return Dot(int(x),int(y))


class Game:
    def __init__(self):
        player = self.random_board() # передаем созданные доски в атрибуты
        ai = self.random_board()
        ai.hid = False
        player.hid = True #скрываем у компьютера и открываем у себя корабли

        self.ai = AI(ai, player)
        self.us = User(player, ai)#  Кидаем доски в наследованные классы от Player и передаем 2 доски свою, чужую, и наоборот


    def board_add_ship(self): # генератор доски
        x = [3,2,1,1,1,1] #наши корабли
        board = Board() # создаем ЭК класса доски в переменной, ничего не передаем и создаем обычную доску с размером 6х6
        count = 0
        for i in x:
            while True:
                count += 1
                if count >2000:
                    return None
                derection = ['г','в']
                ship = Ship(i,Dot(randint(0,6),randint(0,6)),choice(derection))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.new_game() # очистили наши занятые точки
        return board

    def random_board(self): # Если доска еще не создана - генерируем ее
        board = None
        while board is None:
            board = self.board_add_ship()
            return board


    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")


    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print(self.us.board.busy)  #проверял очистился ли у меня список занятых точек на досках.
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            print(self.ai.board.busy)
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.dead_ships == 6:
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.us.board.dead_ships == 6:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

