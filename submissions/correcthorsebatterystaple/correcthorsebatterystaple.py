from aiarena21.client.classes import Player, Map

from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict, Set, Deque
from collections import deque
from enum import Enum
from heapq import heappush, heappop
from math import inf, floor
import random

# the "point cost" associated with each normal move
MOVE_COST = 1


@dataclass
class VertexData:
    location: Tuple[int, int]


class Vertex:
    _parent: "Graph"
    vId: int
    data: VertexData
    _neighbours: Set["Vertex"]

    def __init__(self, parent: "Graph", vId: int, data: VertexData) -> None:
        self._parent = parent
        self.vId = vId
        self.data = data
        self._neighbours = set()

    def add_neighbour(self, weight: float, neighbour: "Vertex") -> None:
        self._neighbours.add(neighbour)
        self._parent.set_edge(self.vId, neighbour.vId, weight)

    def get_neighbours(self) -> List[Tuple[float, "Vertex"]]:
        edges = self._parent._edges[self.vId]
        return [(edges[n.vId], n) for n in self._neighbours]


class Graph:
    _edges: List[List[float]] = []
    _vertices: List[Vertex] = []
    _loc_to_vertices: Dict[Tuple[int, int], List[Vertex]] = {}

    def __init__(self, size: int) -> None:
        self._edges = [[None]*size for _ in range(size)]
        self._vertices = []
        self._loc_to_vertices = {}

    def add_vertex(self, data: VertexData) -> None:
        vertex = Vertex(self, len(self._vertices), data)
        self._vertices.append(vertex)
        if data.location not in self._loc_to_vertices:
            self._loc_to_vertices[data.location] = []
        self._loc_to_vertices[data.location].append(vertex)

    def get_vertex(self, vId: int) -> Vertex:
        return self._vertices[vId]

    def get_vertices_by_location(self, location: Tuple[int, int]) -> List[Vertex]:
        return self._loc_to_vertices[location]

    def get_vertices(self) -> List[Tuple[int, Vertex]]:  # id, vertex
        return list(enumerate(self._vertices))
    
    def set_edge(self, fromId: int, toId: int, value: float) -> None:
        self._edges[fromId][toId] = value

def basic_moves_graph(game_map: Map) -> Graph:
    """Produces a graph of standard adjacent Manhattan moves."""
    map_size = game_map.rows * game_map.cols
    g = Graph(size=map_size)
    for row in range(game_map.rows):
        for col in range(game_map.cols):
            tile = game_map.get(row, col)
            if tile == Map.BLOCK_CHAR:
                continue
            g.add_vertex(VertexData((row, col)))

    for _, vertex in g.get_vertices():
        assert vertex.data.location is not None
        row, col = vertex.data.location
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < game_map.rows and \
                0 <= new_col < game_map.cols and \
                game_map.is_free(new_row, new_col):
                    neighbours_there = g.get_vertices_by_location((new_row, new_col))
                    assert len(neighbours_there) == 1
                    vertex.add_neighbour(MOVE_COST, neighbours_there[0])

    return g


def solution_graph(game_map: Map, items: List[List[int]]) -> Graph:
    """Produce the most insane multilayered graph for reaching a target number of points."""
    # graph = Graph()

    # TODO: deal with bieke/teleport introducing a bunch of edges of weight equal to cost to buy
    return basic_moves_graph(game_map)

def _prev_to_moves(graph: Graph, prev: List[Dict[int, Tuple[int, int]]], dest: int, points: int) -> List[Tuple[int, int]]:
    """Produce sequence of coordinates to move to given ``prev`` from ``calculate_path``.

    Produce series of steps to take as coordinates. If the coordinates are not adjacent,
    then the caller must figure out whether to buy a bike or portal gun.
    """
    v = graph.get_vertex(dest)
    path = [v.data.location]
    while points in prev[v.vId]:
        new_vId, new_points = prev[v.vId][points]
        points = new_points
        v = graph.get_vertex(new_vId)
        # detect duplicate moves (state transitions that might be in same location)
        if path[-1] != v.data.location:
            path.append(v.data.location)

    # add first vertex, so caller can determine if the path starts at source
    if path[-1] != v.data.location:
        path.append(v.data.location)

    path.reverse()
    return path

def points_on_path(items: List[List[int]], path: List[Tuple[int, int]]) -> int:
    """Counts sum of points along path."""
    visited: Set[Tuple[int, int]] = set()
    points = 0
    for location in path:
        if location not in visited:
            points_here = items[location[0]][location[1]]
            points += points_here
            visited.add(location)

    return points


def total_path_moves(path: List[Tuple[int, int]]) -> int:
    """Returns how many moves are necessary to traverse the whole path."""
    return len(path) - 1  # because path has start and end coords


def total_path_weight(path: List[Tuple[int, int]]) -> float:
    """Returns sum of edge weights on path."""
    # TODO: account for bike/teleport
    return total_path_moves(path) * MOVE_COST


def path_badness(path: List[Tuple[int, int]]) -> float:
    """Returns adjusted path "opportunity/realism cost".

    This (should) take into account the fact that moing further is less likely
    because items might be taken by enemy, we might be teleported, game might end etc.
    """
    # TODO: make this implementation less naive (take into account how many rounds left etc
    total_moves = total_path_moves(path) + 1  # to prevent issues with not moving anywhere (-1)
    return total_path_weight(path) * (total_moves ** 0.4)


def path_score(items: List[List[int]], path: List[Tuple[int, int]]) -> float:
    """Give a score to a path, higher is better."""
    # TODO: think. Should we subtract, divide, use more fancy maths?
    points = points_on_path(items, path)
    badness = path_badness(path)
    score = points - badness
    # print(f"Score: {score}, points: {points}, badness: {badness}, path: {path}")
    return score


def calculate_path(graph: Graph, items: List[List[int]], source: int, min_points: int) -> List[Tuple[int, int]]:
    """Returns shortest path to some vertex which gives us at least min_points."""
    # the below lists of dicts are indexed as in
    # prev[vertex_id][points]

    num_vertices = len(graph.get_vertices())
    prev: List[Dict[int, Tuple[int, int]]] = [{} for _ in range(num_vertices)]  # vertex id and points to best previous vertex id and points
    dist: List[Dict[int, float]] = [{} for _ in range(len(prev))]
    visited: Set[Tuple[int, int]] = set()

    dist[source][0] = 0.0
    q: List[Tuple[float, int, int]] = [(0.0, 0, source)]  # total_distance,points,vId
    end_vId = -1
    took_points = False  
    while q:
        _, points, vId = heappop(q)

        if points >= min_points:
            end_vId = vId
            end_v = graph.get_vertex(end_vId)
            points_here = items[end_v.data.location[0]][end_v.data.location[1]]
            min_points = points
            break

        v = graph.get_vertex(vId)

        if (vId, points) in visited:
            continue
        visited.add((vId, points))

        # move to the next "layer" if we have (not already picked up) points here
        points_here = items[v.data.location[0]][v.data.location[1]]
        if not took_points and points_here > 0:
            prev_path = _prev_to_moves(graph, prev, v.vId, points)
            if len(prev_path) > 1 and v.data.location not in prev_path[:-1]:
                # there is certainly no better move than to pick up the points here
                # (indeed we have no choice) so we skip all neighbour traversals
                old_distance = dist[v.vId][points]
                dist[v.vId][points + points_here] = old_distance
                prev[v.vId][points + points_here] = (v.vId, points)

                # probably a more clean fix is possible but i'm too small brain
                heappush(q, (-1, points + points_here, v.vId))
                took_points = True
                continue
        took_points = False

        for weight, neighbour in v.get_neighbours():
            alt = dist[v.vId][points] + weight
            if points not in dist[neighbour.vId]:
                dist[neighbour.vId][points] = inf
            if alt < dist[neighbour.vId][points]:
                dist[neighbour.vId][points] = alt
                prev[neighbour.vId][points] = (v.vId, points)
                heappush(q, (alt, points, neighbour.vId))

    if end_vId == -1:  # could not satisfy min_points constraint
        return []
    path = _prev_to_moves(graph, prev, end_vId, min_points)
    # this assertion should always be true, but unfortunately it isnt
    # assert points_on_path(items, path) >= min_points
    return path


def BFS_points(game_map: Map, source: Tuple[int, int], items: List[List[int]], max_radius: int) -> int:
    # returns locations of fruit within 20 distance
    row, col = source
    visited: List[List[bool]] = [[False] * game_map.cols for _ in range(game_map.rows)]
    visited[row][col] = True
    total_points = 0
    q: Deque[Tuple[int, int, int]] = deque()
    q.append((row, col, 0))
    while q:
        row, col, d = q.popleft()
        if d >= max_radius:
            break
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < game_map.rows and \
                0 <= new_col < game_map.cols and \
                not visited[new_row][new_col] and \
                game_map.is_free(new_row, new_col):
                    if items[new_row][new_col] > 0:  # there is an item (>0 points) here
                        total_points += items[new_row][new_col]
                        # print(f"Added ({new_row}, {new_col}) with points: {items[new_row][new_col]}")
                    visited[new_row][new_col] = True
                    q.append((new_row, new_col, d + 1))
    return total_points

def BFS_heatmap(game_map: Map, source: Tuple[int, int], heatmap, max_radius: int) -> Tuple[int, int]:
    # returns location of most likely heatmap spot
    max_location = None
    max_value = None

    row, col = source
    visited: List[List[bool]] = [[False] * game_map.cols for _ in range(game_map.rows)]
    visited[row][col] = True
    q: Deque[Tuple[int, int, int]] = deque()
    q.append((row, col, 0))
    while q:
        row, col, d = q.popleft()
        if d >= max_radius:
            break
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < game_map.rows and \
                0 <= new_col < game_map.cols and \
                not visited[new_row][new_col] and \
                game_map.is_free(new_row, new_col):
                    value = heatmap[new_row][new_col]
                    if max_value is None or value > max_value:
                        max_value = value
                        max_location = (new_row, new_col)

                    visited[new_row][new_col] = True
                    q.append((new_row, new_col, d + 1))
    return max_location

def how_to_get(game_map: Map, source: Tuple[int, int], to: Tuple[int, int]) -> Tuple[int, int]:
    row, col = source
    visited: List[List[bool]] = [[False] * game_map.cols for _ in range(game_map.rows)]
    visited[row][col] = True
    q: Deque[Tuple[int, int, int]] = deque()
    q.append((row, col, (0, 0)))
    while q:
        row, col, d = q.popleft()
        
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < game_map.rows and \
                0 <= new_col < game_map.cols and \
                visited[new_row][new_col] == False and \
                game_map.is_free(new_row, new_col):
                    if row == to[0] and col == to[1]:
                        return (source[0] + d[0], source[1] + d[1])

                    visited[new_row][new_col] = True
                    q.append((new_row, new_col, (dr, dc) if d == (0, 0) else d))
    return source


enclosed_spaces = None
enclosed_spaces_map = {}
def get_enclosed_spaces(game_map: Map):
    global enclosed_spaces
    global enclosed_spaces_map
    if enclosed_spaces is not None:
        return enclosed_spaces
    
    points = set()
    for row in range(game_map.rows):
        for col in range(game_map.cols):
            if game_map.is_free(row, col):
                points.add((row, col))
    areas = []
    while len(points) > 0:
        start_point = points.pop()
        size = 0
        inside_points = set()
        q = deque()
        q.append(start_point)
        visited: List[List[bool]] = [[False] * game_map.cols for _ in range(game_map.rows)]
        while q:
            point = q.popleft()
            size += 1
            inside_points.add(point)
            row, col = point
            if point in points:
                points.remove(point)

            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                new_row = row + dr
                new_col = col + dc
                if 0 <= new_row < game_map.rows and \
                    0 <= new_col < game_map.cols and \
                    visited[new_row][new_col] == False and \
                    game_map.is_free(new_row, new_col):
                        visited[new_row][new_col] = True
                        q.append((new_row, new_col))
        areas.append([start_point, size, inside_points])
    
    areas.sort(key=lambda x: x[1])

    for a in areas:
        for p in a[2]:
            enclosed_spaces_map[p] = a

    enclosed_spaces = areas
    return enclosed_spaces

def get_enclosed_space_for_point(game_map: Map, point: Tuple[int, int]):
    global enclosed_spaces_map
    get_enclosed_spaces(game_map)
    return enclosed_spaces_map.get(point)

def find_best_worst_position(game_map: Map, items: List[List[int]], remaining_turns: int):
    search_radius = min(6, remaining_turns)

    max_points = None
    max_location = None
    min_points = None
    min_location = None
    for row in range(game_map.rows):
        for col in range(game_map.cols):
            if not game_map.is_free(row, col):
                continue
            location = (row, col)
            points = BFS_points(game_map, location, items, search_radius)
            if max_points is None or points > max_points:
                max_points = points
                max_location = location
            if min_points is None or points < min_points:
                min_points = points
                min_location = location
    
    return min_location, min_points, max_location, max_points

def play_powerup(game_map: Map, me: Player, opponent: Player, items: List[List[int]], new_items: list, heatmap, remaining_turns):
    my_space = get_enclosed_space_for_point(game_map, (me.location[0], me.location[1]))
    if my_space[1] < 20 and me.score >= 100:
        return 'portal gun'

    return ''


def play_turn(game_map: Map, me: Player, opponent: Player, items: List[List[int]], new_items: list, heatmap, remaining_turns):
    if me.portal_gun:
        _, _, max_position, _ = find_best_worst_position(game_map, items, remaining_turns)
        return f'{max_position[0]},{max_position[1]}'

    graph = solution_graph(game_map, items)
    here = graph.get_vertices_by_location(tuple(me.location))[0].vId # type: ignore
    path = calculate_path(graph, items, here, 0)  # worst case - no points (no items)
    for desired_points in (2, 5, 10, 20, 30, 40, 50, 60):  # huge optimisation potential
        new_path = calculate_path(graph, items, here, desired_points)
        if path_score(items, new_path) > path_score(items, path):
            path = new_path

    score = path_score(items, path)
    # print(f"Chosen path {path} has score {score}")
    if score <= 0.0:
        # print(f"Bot is pessimistic (all paths suck!)")
        pass

    if len(path) > 1 and path[0] == graph.get_vertex(here).data.location:
        new_row, new_col = path[1]
    else:
        # already here or nowhere to go
        # Move towards the likeliest future points
        new_row, new_col = me.location
        target_loc = BFS_heatmap(game_map, me.location, heatmap, 20)
        new_row, new_col = how_to_get(game_map, me.location, target_loc)
    return f'{new_row},{new_col}'


worst_position = (0, 0)
def play_auction(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    global worst_position
    search_radius = min(6, remaining_turns)

    enclosed_spaces = get_enclosed_spaces(game_map)
    if len(enclosed_spaces) > 1 and enclosed_spaces[0][1] < 20:
        worst_space = enclosed_spaces[0]
        worst_position = worst_space[0]
        if (opponent.location[0], opponent.location[1]) in worst_space[2]:
            return 2

        min_points = BFS_points(game_map, worst_position, items, search_radius)
    else:
        min_location, min_points, max_location, max_points = find_best_worst_position(game_map, items, remaining_turns)
        worst_position = min_location
    
    current_points = BFS_points(game_map, me.location, items, search_radius)
    points_diff = current_points - min_points

    if current_points < 20:
        return 0

    return floor(max(points_diff, 0) * 0.25)


def play_transport(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    return f'{worst_position[0]},{worst_position[1]}'
