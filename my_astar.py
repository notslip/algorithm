import warnings
from typing import Tuple, List


class Node:
    def __init__(self, parent: object = None, position: Tuple[int, int] = None, cost: int = 0):
        self.parent = parent
        self.position = position
        #цена( высота) каждой клетки
        self.cost = cost
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other: object):
        return self.position == other.position


def _return_path(current_node: Node) -> Tuple[List, int]:
    """
    returns a list containing the coordinates of each point in the path,
    and the amount of "fuel" spent on the way
    :param current_node:
    :return:
    """
    ret_path = []
    current = current_node
    fuel = 0
    while current is not None:
        #подсчет топлива затраченного на подьем или спуск на текущую ячейку
        #если высота текущей ячейки равна предыдущей, то топливо тратится
        #только на переход ячейки, а это равно количество ходов
        if current.parent:
            if current.cost > current.parent.cost:
                fuel += current.cost - current.parent.cost
            elif current.cost < current.parent.cost:
                fuel += current.parent.cost - current.cost
        #добавление в список пути текущей ячейки
        ret_path.append(current)
        #делаем родителя текущей ячейки, текущей ячейкой)))
        current = current.parent
    return ret_path[::-1], fuel+len(ret_path)-1


def _generate_children(current_node: Node, maze: List) -> List:
    """
    returnы a list of "children" of the current point
    :param current_node:
    :param maze:
    :return:
    """
    children = []
    # список позиций, вокруг точки, для проверки
    move_position = [(0, -1),
                     (0, 1),
                     (-1, 0),
                     (1, 0),
                     ]
    #циклом идем по позициям
    for new_position in move_position:
        node_position = (current_node.position[0] + new_position[0],
                         current_node.position[1] + new_position[1])
        # проверка выхода за рамки матрицы
        if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (
                len(maze[len(maze) - 1]) - 1) or node_position[1] < 0:
            continue
        # создания точки у которой родитель текущая точка
        new_node = Node(current_node, node_position, cost=maze[node_position[0]][node_position[1]])
        # добавляем в список детей
        children.append(new_node)
    return children


def _consider_child(children: List, current_node: Node,
              end_node: Node, open_list: List,
              closed_list: List):
    """
    calculates the price for each "point-child"
    :param children:
    :param current_node:
    :param end_node:
    :param open_list:
    :param closed_list:
    :return:
    """
    # прогоняем через список детей точки
    for child in children:
        # если ребенок-точка в списке закрытых то пропускаем её
        for closed_child in closed_list:
            if child == closed_child:
                continue
        # создаем значения коофициэнтов
        # сумма пути + высота каждой точки
        child.g += current_node.g + 1 + child.cost
        # "прямое" расстояние до конечной точки
        child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                (child.position[1] - end_node.position[1]) ** 2)
        # конечная "цена" для алгоритма
        child.f = child.g + child.h
        # если у ребенока-точки путь больше чем у точек в открытом списке то пропускаем её
        for open_node in open_list:
            if child == open_node and child.g > open_node.g:
                continue
        # добовляем ребенка точку в лист для посещения
        open_list.append(child)


def search(start: Tuple, end: Tuple, maze: List[List]) -> Tuple[List, int]:
    """
    looking for a path by choosing the best point
    :param start:
    :param end:
    :param maze:
    :return:
    """
    #  инициализируем начальные переменные,
    # список точек для посещения и список посещенных точек,
    # начальную и конечную точки
    open_list = []
    closed_list = []
    start_node = Node(position=start, cost=maze[start[0]][start[1]])
    end_node = Node(position=end, cost=maze[end[0]][end[1]])
    # добавляем начальную точку в список для посещения
    open_list.append(start_node)
    # цикл который проходит точки для посещения, можно заменить работой с кучей
    while len(open_list) > 0:
        current_node = open_list[0]
        current_index = 0
        #проверяем на лучшую "цену" точку и делаем её текущей точкой
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index
        # удаляем из списка для посещения и добавляем в список посещенных точек
        open_list.pop(current_index)
        closed_list.append(current_node)
        # условие конца программы, пердаем в функцию для подсчета пути и топлива
        if current_node == end_node:
            return _return_path(current_node)
        # генерируем дочерние точки для посещения
        children = _generate_children(current_node, maze)
        #считаем для точек детей их "стоимость"
        _consider_child(children, current_node, end_node, open_list, closed_list)

    warnings.warn("Ненашел путь")
    return None


def example():
    # задаем начальные параметры
    maze = [
        [1, 2, 6, 9, 9, 4, 6],
        [2, 3, 4, 5, 5, 1, 1],
        [5, 6, 3, 9, 1, 3, 5],
        [3, 1, 1, 1, 1, 3, 6],
        [4, 2, 1, 1, 6, 6, 5]
    ];
    # maze = [
    #     [0, 4],
    #     [1, 3]
    # ]
    start = (0, 0)
    end = (len(maze) - 1, len(maze[0]) - 1)
    #прогоняем алгоритм
    path_list, fuel = search(start, end, maze)
    #раскрашиваем путь на матрице
    for _ in path_list:
        x, y = _.position
        maze[x][y] = "*"
    # выводим в консоль матрицу
    for i in maze:
        print(*i)
    #выводим в косоль шаги по координатам
    for i, v in enumerate(path_list):
        if i != len(path_list)-1:
            print(f"[{v.position[0]}][{v.position[1]}]->", end="")
        else:
            print(f"[{v.position[0]}][{v.position[1]}]")
    #выводим доп. параметры
    print(f"Топлива : {fuel} \nХодов: {len(path_list)-1}")


example()









