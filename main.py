#Подключаем библиотеку генератора случайных значений
from random import randint
from random import choice
#Создадим класс-исключение, которое будет активировать когда выстрел идет мимо игровой доски.
class BoardOutException(Exception):
    pass

#Создадим класс-исключение, которое будет активировать когда мы пытаемся установить корабль вплотную к другому кораблю.
class WrongShipPlacement(Exception):
    pass

#Создадим класс-исключение, которое будет активировать когда мы пытаемся установить корабль вплотную к другому кораблю.
class WrongShot(Exception):
    pass

#Создадим класс описывающий конкретную точку на доске со следующими свойствами:
#       x - координата по оси X
#       y - координата по оси Y
#       value - значение точки. Может принимать несколько значений (О-пустая точка (по умолчанию)/Х-в этой точке есть попадание в корабль/■ - стоит корабль/* - если промах)
class Dot:
    def __init__(self, x, y, value="O"):
        self.x = x
        self.y = y
        self.value = value

    #Создадим метод позволяющий сравнивать два объекта класса Dot
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    #Создадим метод позволяющий выводить представление объекта при преобразовании его в строку, как значение свойства value
    def __str__(self):
       return self.value

# Создадим класс Ship со следующими свойствами:
#       - length - длина
#       - dotBegin - начальная точка позиционирования корабля (началом считается самоя левая-верхняя точка корабля на игровой доске)
#       - direction - расположение корабля (либо 'v' - вертикальное, либо 'h' - горизонтальное)
#       - lives - количество жизней корабля (при создании равно его длине)
class Ship:
    def __init__(self, length, dotBegin, direction):
        self.length = length
        self.dotBegin = dotBegin
        self.direction = direction
        self.lives = length

    #Создадим метод, который будет возвращать список точек на доске, которые заняты этим кораблем.
    @property
    def dots(self):
        listOfDots = []
        listOfDots.append(self.dotBegin)
        if self.direction == 'h':
            i = 1
            while i < self.length:
                listOfDots.append(Dot(self.dotBegin.x, self.dotBegin.y+i))
                i += 1
        elif self.direction == 'v':
            i = 1
            while i < self.length:
                listOfDots.append(Dot(self.dotBegin.x+i, self.dotBegin.y))
                i += 1
        return listOfDots

    def __repr__(self):
        return f'{self.length}-ый корабль, с {self.lives} жизнью/жизнями, с начальной точкой в ({self.dotBegin.x}, {self.dotBegin.y})'

#Создадим класс игровой доски
class Board:
    #Создадим конструктор доски. Для этого при инициализации доски передадим размеры доски X и Y, а так же нужно показывать доску или нет
    def __init__(self,x,y,hid):
        self.x = x
        self.y = y
        self.hid = hid
        # Игровая доска
        self.desk = []
        # Список кораблей
        self.shipList = []
        self.listOfBusyDots = []
        # Количество выживших кораблей (по умолчанию все корабли живы, поэтому значение 7)
        self.shipsAlive = 7
        #Заполним нашу доску объектами класса Dot
        ix = 1
        while ix <= self.x:
            iy = 1
            listY = []
            while iy <= self.y:
                listY.append(Dot(ix, iy))
                iy += 1
            self.desk.append(listY)
            ix += 1

    #Создадим метод, который будет определять передаваемый объект класса Dot находится в пределах доски или нет. Если нет, то возвращаем True
    def out(self, dot):
        if dot.x in range(1, self.x + 1, 1) and dot.y in range(1, self.y + 1, 1):
            return False
        else:
            return True

    #Создадим метод, который "очертит" наш корабль точками, т.к. в эти точки нельзя ставить корабль или в них бессмысленно стрелять если корабль подбит.
    def contour(self, ship):
        listOfContours = []
        for dotsOfShip in ship.dots:
            for i in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    if self.out(Dot(dotsOfShip.x + i, dotsOfShip.y + y)) or Dot(dotsOfShip.x + i, dotsOfShip.y + y) in ship.dots:
                        pass
                    else:
                        listOfContours.append(Dot(dotsOfShip.x + i, dotsOfShip.y + y))
        return listOfContours

    #Создадим метод, который будет добавлять корабль на игровую доску
    def add_ship(self, newShip):
        # Проверим можно ли поставить корабль на доску. Для начала проверим помещается ли корабль на доску по заданным параметрам
        for shipDot in newShip.dots:
            if self.out(shipDot):
                raise BoardOutException()
        # Проверим можно ли поставить корабль на доску. Теперь проверим нет ли вплотную установленных других кораблей
        for contourDot in self.contour(newShip):
            if str(self.desk[contourDot.x-1][contourDot.y-1]) == '■':
                raise WrongShipPlacement()
        #Проверим не попадает ли нащ корабль в координаты уже установленного корабля (актуально для однопалубных)
        for shipDot in newShip.dots:
            for shipOnDesk in self.shipList:
                if shipDot in shipOnDesk.dots:
                    raise WrongShipPlacement()
        for shipDot in newShip.dots:
            self.desk[shipDot.x-1][shipDot.y-1].value = '■'
        self.shipList.append(newShip)

    #Создадим метод, который будет осуществлять выстрел и отмечать его на игровой доске
    def shot(self, dot):
        #Проверим в пределах ли доски осуществляется выстрел
        if self.out(dot):
            raise BoardOutException()
        #Проверим не ошибочный ли выстрел (в уже стреленную клетку или клетку обведенную вокруг убитого корабля
        elif dot in self.listOfBusyDots:
            raise WrongShot()
        #Иначе производим выстрел
        else:
            #Сразу добавим эту точку в список занятых точек
            self.listOfBusyDots.append(dot)
            #Установим проверочный признак промаха в значение Истина
            miss = True
            kill_ship = False
            #Проверим есть ли попадание в корабль
            for ship in self.shipList:
                if dot in ship.dots:
                    #Если есть попадание то уменьшим на одну жизнь корабля и пометим эту точку попаданием "Х"
                    ship.lives -= 1
                    self.desk[dot.x-1][dot.y-1].value = 'X'
                    #Если корабль убит, то обведем его по контуру и добавим все точки контура в список занятых точек
                    if ship.lives == 0:
                        self.shipsAlive -= 1
                        kill_ship = True
                        for dotContour in self.contour(ship):
                            self.desk[dotContour.x - 1][dotContour.y - 1].value = '*'
                            self.listOfBusyDots.append(dotContour)
                    else:
                        kill_ship = False
                    #Установим проверочный признак промаха в значение Ложь и прервем выполнения цикла по поиску попадания в корабль, т.к. это уже не имеет смысла.
                    miss = False
                    break
            #Если проверочное значение промаха осталось истинным, то установим у точки значение промаха. А так же передаем необходим ли повторный выстрел (когда было попадание и был убит корабль или нет. Это повлияет на поведение AI)
            if miss:
                self.desk[dot.x - 1][dot.y - 1].value = '*'
                return {'move':False, 'kill_ship':False}
            else:
                return {'move':True, 'kill_ship':kill_ship}

    #Создадим метод, который будет выводить в консоль игровую доску и привидение его к строке.
    def __str__(self):
        i = 1
        strDesk = ' |'
        while i <= self.x:
            strDesk = strDesk + str(i) + '|'
            i += 1
        i = 1
        strDesk = strDesk + '\n'
        while i <= self.x:
            r = 1
            strDesk = strDesk + str(i) + '|'
            while r <= self.y:
                if self.hid and str(self.desk[i - 1][r - 1]) == '■':
                    strDesk = strDesk + 'O' + '|'
                else:
                    strDesk = strDesk + str(self.desk[i - 1][r - 1]) + '|'
                r += 1
            strDesk = strDesk+'\n'
            i += 1
        return strDesk

#Создадим класс который будет описывать свойства и методы игроков
class Player:
    def __init__(self, my_board, enemy_board):
        self.my_board = my_board
        self.enemy_board = enemy_board
        #В этом свойстве мы будем фиксировать последний удачный выстрел компьютера, чтоб в дальнейшем его следующий выстрел был в ближайшую точку
        self.ai_last_target = None
    #Метод который мы переопределим для подклассов AI и User
    def ask(self, ai_last_target=None):
        pass

    #Создадим метод который будет описывать ходы в игре
    def move(self):
        #Определим потенциальную цель
        target = self.ask()
        #Переменная, которая будет фиксировать было ли попадание и нужен ли повторный выстрел
        need_move = False
        #В обработке исключений совершим выстрел
        try:
            need_move_dict = self.enemy_board.shot(target)
            print(f'Выстрел по координатам: строка:{target.x}, столбец:{target.y}')
            #Если выстрел осуществляет компьютер проверим нужен ли дополнительный выстрел и если он нужен определим предыдущий удачный выстрел при условии, что последний выстрел не был окончательным для этого корабля
            if isinstance(self, AI) and need_move_dict['move'] and not need_move_dict['kill_ship']:
                self.ai_last_target = target
            else:
                self.ai_last_target = None
            need_move = need_move_dict['move']
        #Обработаем исключения. Если они произошли то совершаем повторный запрос на выстрел
        except BoardOutException:
            if isinstance(self, User):
                print('Вы выбрали координаты, которые находятся за пределами доски. Попробуйте еще раз!')
            else:
                print('Ошибочный выстрел компьютера!')
            need_move = True
        except WrongShot:
            if isinstance(self, User):
                print('Вы пытаетесь повторно выстрелить в ранее помеченную точку. Попробуйте еще раз!')
            else:
                print('Ошибочный выстрел компьютера!')
            need_move = True
        else:
            #Проинформируем о произведенном выстреле и веведем доску противника для повторного
            if need_move_dict['move'] and not need_move_dict['kill_ship']:
                print('Попал! Ранен!')
                print(self.enemy_board)
            elif need_move_dict['move'] and need_move_dict['kill_ship']:
                print('Убит!')
                print(self.enemy_board)
            elif not need_move_dict['move']:
                print('Промазал!')
        #Прервем выполнение выстрелов если у противника не осталось живых кораблей
        if self.enemy_board.shipsAlive == 0:
            return False
        #Вернем признак необходимости повторного выстрела
        return need_move

#Определим класс для Пользователя от родительского класса Игрока (Player)
class User(Player):
    #Переопределим метод для запроса координат выстрела для Пользователя
    def ask(self):
        x = int(input('Введите номер строки точки, в которую хотите попасть: '))
        y = int(input('Введите номер колонки точки, в которую хотите попасть: '))
        target_dot = Dot(x, y)
        return target_dot

#Создадим класс AI - искуственного интелекта. В котором опишем логику стрельбы компьютером
class AI(Player):
    def ask(self):
        #Если ai_last_target ровна None значит предыдущий выстрел AI был промахом и мы можем стрелять в любое доступное место доски
        if self.ai_last_target is None:
            #Генерируем точку в рамках доски случайным образом с помощью библиотеки генератора случайных чисел
            x = randint(1,self.enemy_board.x)
            y = randint(1,self.enemy_board.y)
            return Dot(x, y)
        #Если ai_last_target принадлежит классу Dot, значит предыдущий выстрел был попаданием и корабль еще полностью не уничтожен. В этом случае стреляем в ближайшие точки рядом с попаданием
        elif isinstance(self.ai_last_target, Dot):
            if self.ai_last_target.x == 1:
                x = randint(self.ai_last_target.x, self.ai_last_target.x+1)
            elif self.ai_last_target.x == self.enemy_board.x:
                x = randint(self.ai_last_target.x-1, self.ai_last_target.x)
            else:
                x = randint(self.ai_last_target.x-1, self.ai_last_target.x+1)
            if self.ai_last_target.y == 1:
                y = randint(self.ai_last_target.y, self.ai_last_target.y+1)
            elif self.ai_last_target.y == self.enemy_board.y:
                y = randint(self.ai_last_target.y-1, self.ai_last_target.y)
            else:
                y = randint(self.ai_last_target.y-1, self.ai_last_target.y+1)
            return Dot(x, y)

#Создадим класс, который будет отвечать за генерацию самой игры
class Game:
    #Создадим конструктор класса с необходимыми свойствами
    def __init__(self):
        self.human_board = Board(6, 6, False)
        self.ai_board = Board(6, 6, True)
        self.player_human = User(self.human_board, self.ai_board)
        self.player_ai = AI(self.ai_board, self.human_board)
        self.player_name = ''
        #Свойство определяет кто должен сейчас ходить
        self.who_move = choice([self.player_human, self.player_ai])

    #Создадим метод генерации кораблей на игровой доске
    def random_board(self, board):
        #Опишем каких и сколько кораблей необходимо разместить на доске и как корабль может позиционироваться.
        listOfShipsForAdd = [3, 2, 2, 1, 1, 1, 1]
        listOfDirection = ['v', 'h']
        #В цикле попробуем поставить корабли на доску
        for ship_length in listOfShipsForAdd:
            a = True
            #Для исключения возможности бесконечного цикла установим количество попыток размещения
            trying = 50
            #Запустим цикл на размещение корабля и если попытка неудачная, то будем повторять, пока попытка не будет удачной или количество попыток не достигнет 50
            while a:
                trying -= 1
                try:
                    #С помощью генератора случайных значений выставим координаты и направление
                    x = randint(1, board.x)
                    y = randint(1, board.y)
                    direction = choice(listOfDirection)
                    #Создадим объект Ship (корабль)
                    new_ship = Ship(ship_length, Dot(x, y), direction)
                    #Попытаемся его разместить на игровую доску
                    board.add_ship(new_ship)
                #При возникновении исключений пропустим их в данном случае, т.к. нам важно разместить все корабли и если попытка не удачная, то повторить размещение с другими координатами
                except WrongShipPlacement:
                    pass
                except BoardOutException:
                    pass
                else:
                    a = False
                #Если количество попыток исчерпано прервем выполнение цикла исключением
                if trying == 0:
                    raise StopIteration

    #Создадим метод, который будет описывать преветствие пользователя
    def greet(self):
        print('Вас приветствует игра "Морской-бой"!!!')
        self.player_name = input('Введите ваше имя: ')
        print(f'{self.player_name}, игра происходит по следующим правилам:')
        print('1) Игровое поле 6х6 клеток, где у вас и у компьютера следующие корабли:')
        print('- Один 3-х палубный корабль')
        print('- Два 2-х палубных корабля')
        print('- Четыре однопалубных палубных корабля')
        print('2) Ходы осуществляются по-очереди между Вами и компьютером')
        print('3) Пустые и "непроверянные" клетки отмечаются - "О", клетка с кораблем обозначается - "■", промах либо контур подбитого корабля - "*"')
        print('4) Первый выстрел определяется случайным образом между Вами и компьютером')
        print('5) Корабли как у вас, так и у компьютера раставляются автоматически в случайном порядке')
        print('6) Игра идет до того момента пока все корабли у Вас или у компьютера не будут уничтожены.')
        print('Удачи!!!')

    #Опишем метод, который в цикле будет запускать ходы по-очереди пользователь/компьютер
    def loop(self):
        #Счетчик ходов
        n = 1
        #Запустим цикл ходов
        while True:
            #Если у игрока или компьютера все корабли подбиты прервем выполнение цикла
            if self.human_board.shipsAlive == 0 or self.ai_board.shipsAlive == 0:
                break
            #Выведем в интерфейс доску игрока и компьютера
            print(f'------------------Ход № {n}-----------------------')
            print('Ваша игровая доска:')
            print(self.human_board)
            print('Игровая доска противника:')
            print(self.ai_board)
            #Выполним ход, при этом если нужен дополнительный ход, то он будет выполнятся пока противник не промахнется
            while self.who_move.move():
                pass
            #Если текущий ход выполнял компьютер, то поменяем значение свойста who_move на игрока и наоборот, чтоб чередовать ходы
            if isinstance(self.who_move, AI):
                self.who_move = self.player_human
            elif isinstance(self.who_move, User):
                self.who_move = self.player_ai
            print('---------------------------------------------------')
            n += 1

    #Определим метод стартующий игру
    def start(self):
        #Для начала сгенерируем игровые доски, т.к. у нас есть 50 попыток на генерацию доски, то повторим генерацию если предыдущие попытки были неудачными
        a = True
        #Генерируем доску игрока
        while a:
            try:
                #"Очистим" доску
                self.human_board = Board(6, 6, False)
                #Попробуем сгенерировать на ней корабли
                self.random_board(self.human_board)
            #При возникновении исключения "а" остается в равным False и попытка генерации повторяется
            except StopIteration:
                pass
            #Если генерация прошла успешно выходим из цикла
            else:
                a = False
        #Генерируем доску игрока
        a = True
        while a:
            try:
                # "Очистим" доску
                self.ai_board = Board(6, 6, True)
                #Попробуем сгенерировать на ней корабли
                self.random_board(self.ai_board)
            # При возникновении исключения "а" остается в равным False и попытка генерации повторяется
            except StopIteration:
                pass
            # Если генерация прошла успешно выходим из цикла
            else:
                a = False
        #Переопределим свойства объекта Game после заполнения игровых досок
        self.player_human = User(self.human_board, self.ai_board)
        self.player_ai = AI(self.ai_board, self.human_board)
        self.who_move = choice([self.player_human, self.player_ai])
        #Запустим приветствие
        self.greet()
        #Запустим сам игровой процесс
        self.loop()
        #Определим победителя и сообщим об этом в консоль
        if self.ai_board.shipsAlive == 0:
            print(f'{self.player_name}, поздравляем!! Вы победили!!')
        else:
            print(f'{self.player_name}, к сожалению вы проиграли!')
        #Спросим игрока хочет ли он запустить игру вновь
        restart_game = input('Хотите повторить? (Y/N): ').upper()
        #Если игрок хочет поиграть вновь вернем значение True
        if restart_game == 'Y':
            return True
        else:
            return False

if __name__ == '__main__':
    #Инициализируем игру
    new_game = Game()
    #Пока игрок хочет играть будем перезапускать игру.
    while new_game.start():
        pass
