"""
Smart routing engine using Dijkstra and A* algorithms.
Simulates road network as a grid graph over Saudi Arabia coordinates.
"""
from __future__ import annotations

import heapq
import json
import math
from dataclasses import dataclass
from typing import Callable

# Average road speed km/h (simulation)
BASE_SPEED_KMH = 60.0
EARTH_RADIUS_KM = 6371.0


@dataclass
class Node:
    lat: float
    lng: float
    grid_id: str


@dataclass
class RouteResult:
    path: list[tuple[float, float]]
    distance_km: float
    eta_minutes: float
    algorithm: str
    polyline_json: str


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two GPS points."""
    rlat1, rlng1, rlat2, rlng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = rlat2 - rlat1
    dlng = rlng2 - rlng1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _grid_key(lat: float, lng: float, step: float = 0.01) -> str:
    return f"{round(lat / step)}_{round(lng / step)}"


def _neighbors(lat: float, lng: float, step: float = 0.01) -> list[tuple[float, float]]:
    """8-directional grid neighbors for simulated road network."""
    return [
        (lat + step, lng),
        (lat - step, lng),
        (lat, lng + step),
        (lat, lng - step),
        (lat + step, lng + step),
        (lat + step, lng - step),
        (lat - step, lng + step),
        (lat - step, lng - step),
    ]


def _heuristic(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    return haversine_km(lat1, lng1, lat2, lng2)


def _build_graph(
    start: tuple[float, float],
    end: tuple[float, float],
    traffic_penalty: Callable[[float, float], float] | None = None,
    step: float = 0.008,
    max_nodes: int = 800,
) -> dict[str, list[tuple[str, float]]]:
    """
    Build a local directed graph between start and end bounding box.
    Edge weight = distance * traffic penalty factor.
    """
    slat, slng = start
    elat, elng = end
    min_lat = min(slat, elat) - 0.05
    max_lat = max(slat, elat) + 0.05
    min_lng = min(slng, elng) - 0.05
    max_lng = max(slng, elng) + 0.05

    graph: dict[str, list[tuple[str, float]]] = {}
    nodes: dict[str, tuple[float, float]] = {}

    lat = min_lat
    count = 0
    while lat <= max_lat and count < max_nodes:
        lng = min_lng
        while lng <= max_lng and count < max_nodes:
            gid = _grid_key(lat, lng, step)
            nodes[gid] = (lat, lng)
            graph.setdefault(gid, [])
            for nlat, nlng in _neighbors(lat, lng, step):
                if not (min_lat <= nlat <= max_lat and min_lng <= nlng <= max_lng):
                    continue
                nid = _grid_key(nlat, nlng, step)
                dist = haversine_km(lat, lng, nlat, nlng)
                penalty = traffic_penalty(lat, lng) if traffic_penalty else 1.0
                weight = dist * penalty
                graph[gid].append((nid, weight))
            lng += step
            count += 1
        lat += step

    # Ensure start/end connected
    for point in [start, end]:
        gid = _grid_key(point[0], point[1], step)
        nodes[gid] = point
        graph.setdefault(gid, [])
        for nlat, nlng in _neighbors(point[0], point[1], step):
            nid = _grid_key(nlat, nlng, step)
            dist = haversine_km(point[0], point[1], nlat, nlng)
            penalty = traffic_penalty(point[0], point[1]) if traffic_penalty else 1.0
            graph[gid].append((nid, dist * penalty))
            graph.setdefault(nid, []).append((gid, dist * penalty))

    return graph, nodes


def dijkstra(
    start: tuple[float, float],
    end: tuple[float, float],
    traffic_penalty: Callable[[float, float], float] | None = None,
) -> RouteResult | None:
    """Find shortest path using Dijkstra's algorithm on simulated grid graph."""
    step = 0.012
    graph, nodes = _build_graph(start, end, traffic_penalty, step=step)
    start_id = _grid_key(start[0], start[1], step)
    end_id = _grid_key(end[0], end[1], step)

    if start_id not in nodes:
        nodes[start_id] = start
        graph[start_id] = []
    if end_id not in nodes:
        nodes[end_id] = end
        graph[end_id] = []

    dist: dict[str, float] = {start_id: 0.0}
    prev: dict[str, str | None] = {start_id: None}
    pq: list[tuple[float, str]] = [(0.0, start_id)]
    visited: set[str] = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if u == end_id:
            break
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if end_id not in dist:
        return _fallback_direct(start, end, "dijkstra")

    path_ids: list[str] = []
    cur: str | None = end_id
    while cur:
        path_ids.append(cur)
        cur = prev.get(cur)
    path_ids.reverse()

    path = [nodes[pid] for pid in path_ids if pid in nodes]
    if len(path) < 2:
        path = [start, end]

    distance = sum(
        haversine_km(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])
        for i in range(len(path) - 1)
    )
    avg_penalty = 1.0
    if traffic_penalty:
        samples = [traffic_penalty(p[0], p[1]) for p in path[:: max(1, len(path) // 5)]]
        avg_penalty = sum(samples) / len(samples) if samples else 1.0
    eta = (distance / BASE_SPEED_KMH) * 60 * avg_penalty

    return RouteResult(
        path=path,
        distance_km=round(distance, 2),
        eta_minutes=round(eta, 1),
        algorithm="dijkstra",
        polyline_json=json.dumps([[p[0], p[1]] for p in path]),
    )


def astar(
    start: tuple[float, float],
    end: tuple[float, float],
    traffic_penalty: Callable[[float, float], float] | None = None,
) -> RouteResult | None:
    """Find optimal path using A* with haversine heuristic."""
    step = 0.01
    graph, nodes = _build_graph(start, end, traffic_penalty, step=step)
    start_id = _grid_key(start[0], start[1], step)
    end_id = _grid_key(end[0], end[1], step)
    elat, elng = end

    if start_id not in nodes:
        nodes[start_id] = start
    if end_id not in nodes:
        nodes[end_id] = end

    g_score: dict[str, float] = {start_id: 0.0}
    f_score: dict[str, float] = {start_id: _heuristic(start[0], start[1], elat, elng)}
    prev: dict[str, str | None] = {start_id: None}
    open_set: list[tuple[float, str]] = [(f_score[start_id], start_id)]
    closed: set[str] = set()

    while open_set:
        _, u = heapq.heappop(open_set)
        if u in closed:
            continue
        if u == end_id:
            break
        closed.add(u)
        ulat, ulng = nodes.get(u, start)
        for v, w in graph.get(u, []):
            tentative = g_score.get(u, float("inf")) + w
            if tentative < g_score.get(v, float("inf")):
                prev[v] = u
                g_score[v] = tentative
                vlat, vlng = nodes.get(v, (elat, elng))
                f = tentative + _heuristic(vlat, vlng, elat, elng)
                f_score[v] = f
                heapq.heappush(open_set, (f, v))

    if end_id not in g_score:
        return _fallback_direct(start, end, "astar")

    path_ids: list[str] = []
    cur: str | None = end_id
    while cur:
        path_ids.append(cur)
        cur = prev.get(cur)
    path_ids.reverse()
    path = [nodes[pid] for pid in path_ids if pid in nodes]
    if len(path) < 2:
        path = [start, end]

    distance = sum(
        haversine_km(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])
        for i in range(len(path) - 1)
    )
    avg_penalty = 1.0
    if traffic_penalty:
        samples = [traffic_penalty(p[0], p[1]) for p in path[:: max(1, len(path) // 5)]]
        avg_penalty = sum(samples) / len(samples) if samples else 1.0
    eta = (distance / BASE_SPEED_KMH) * 60 * avg_penalty

    return RouteResult(
        path=path,
        distance_km=round(distance, 2),
        eta_minutes=round(eta, 1),
        algorithm="astar",
        polyline_json=json.dumps([[p[0], p[1]] for p in path]),
    )


def _fallback_direct(start: tuple[float, float], end: tuple[float, float], algo: str) -> RouteResult:
    """Straight-line fallback when graph search fails."""
    dist = haversine_km(start[0], start[1], end[0], end[1])
    path = [start, end]
    eta = (dist / BASE_SPEED_KMH) * 60
    return RouteResult(
        path=path,
        distance_km=round(dist, 2),
        eta_minutes=round(eta, 1),
        algorithm=algo,
        polyline_json=json.dumps([[start[0], start[1]], [end[0], end[1]]]),
    )


def compute_route(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    algorithm: str = "astar",
    traffic_penalty: Callable[[float, float], float] | None = None,
) -> RouteResult:
    """Public API: compute route with selected algorithm."""
    start = (start_lat, start_lng)
    end = (end_lat, end_lng)
    if algorithm.lower() == "dijkstra":
        result = dijkstra(start, end, traffic_penalty)
    else:
        result = astar(start, end, traffic_penalty)
    return result or _fallback_direct(start, end, algorithm)
