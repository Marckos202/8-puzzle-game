import time
import numpy as np
from collections import deque
import heapq
from copy import deepcopy

class PuzzleNode:
    """
    Nodo que representa un estado del puzzle en el árbol de búsqueda.
    """
    def __init__(self, state, parent=None, action=None, depth=0, cost=0):
        """
        Inicializa un nodo del árbol de búsqueda.
        
        Args:
            state: Estado del tablero
            parent: Nodo padre
            action: Acción que llevó a este estado
            depth: Profundidad del nodo en el árbol
            cost: Costo acumulado hasta este nodo
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.cost = cost
        
        # Encontrar la posición del espacio vacío
        pos = np.where(self.state == 0)
        self.empty_pos = (pos[0][0], pos[1][0])
    
    def __lt__(self, other):
        """
        Comparador para la cola de prioridad en A*.
        """
        return self.cost < other.cost
    
    def __eq__(self, other):
        """
        Dos nodos son iguales si sus estados son iguales.
        """
        return np.array_equal(self.state, other.state)
    
    def __hash__(self):
        """
        Hash del nodo basado en su estado.
        """
        return hash(self.state.tobytes())
    
    def get_possible_actions(self):
        """
        Devuelve una lista de acciones posibles desde este estado.
        """
        row, col = self.empty_pos
        actions = []
        
        # Verificar movimientos posibles (arriba, abajo, izquierda, derecha)
        if row > 0:
            actions.append('up')
        if row < 2:
            actions.append('down')
        if col > 0:
            actions.append('left')
        if col < 2:
            actions.append('right')
        
        return actions
    
    def get_child_node(self, action):
        """
        Genera un nodo hijo aplicando la acción especificada.
        
        Args:
            action: Dirección del movimiento ('up', 'down', 'left', 'right')
            
        Returns:
            Un nuevo nodo con el estado resultante
        """
        row, col = self.empty_pos
        new_state = deepcopy(self.state)
        
        # Calcular la nueva posición según la acción
        if action == 'up':
            new_row, new_col = row - 1, col
        elif action == 'down':
            new_row, new_col = row + 1, col
        elif action == 'left':
            new_row, new_col = row, col - 1
        elif action == 'right':
            new_row, new_col = row, col + 1
        else:
            return None  # Acción inválida
        
        # Realizar el movimiento
        new_state[row, col] = new_state[new_row, new_col]
        new_state[new_row, new_col] = 0
        
        # Crear y devolver el nuevo nodo
        return PuzzleNode(
            state=new_state,
            parent=self,
            action=action,
            depth=self.depth + 1,
            cost=self.depth + 1  # Para BFS y DFS, el costo es igual a la profundidad
        )
    
    def get_path(self):
        """
        Reconstruye el camino desde el nodo raíz hasta este nodo.
        
        Returns:
            Lista de tuplas (acción, estado) que representan el camino
        """
        path = []
        current = self
        
        while current.parent is not None:
            path.append((current.action, current.state))
            current = current.parent
        
        # El camino se construyó en orden inverso, hay que revertirlo
        return list(reversed(path))


class PuzzleSolver:
    """
    Clase que implementa diferentes algoritmos de búsqueda para resolver el 8-puzzle.
    """
    def __init__(self, initial_state, goal_state):
        """
        Inicializa el solucionador con los estados inicial y objetivo.
        
        Args:
            initial_state: Estado inicial del tablero
            goal_state: Estado objetivo del tablero
        """
        self.initial_state = np.array(initial_state)
        self.goal_state = np.array(goal_state)
        
        # Métricas de rendimiento
        self.nodes_expanded = 0
        self.execution_time = 0
        self.path_length = 0
    
    def _is_goal(self, state):
        """
        Verifica si un estado es el estado objetivo.
        """
        return np.array_equal(state, self.goal_state)
    
    def _get_manhattan_distance(self, state):
        """
        Calcula la distancia de Manhattan para un estado dado.
        Esta es la suma de las distancias de Manhattan de cada ficha a su posición objetivo.
        """
        distance = 0
        
        # Crear un mapa de las posiciones objetivo
        goal_positions = {}
        for i in range(3):
            for j in range(3):
                goal_positions[self.goal_state[i, j]] = (i, j)
        
        # Calcular la distancia para cada ficha
        for i in range(3):
            for j in range(3):
                if state[i, j] != 0:  # Ignorar el espacio vacío
                    goal_i, goal_j = goal_positions[state[i, j]]
                    distance += abs(i - goal_i) + abs(j - goal_j)
        
        return distance
    
    def solve_bfs(self):
        """
        Resuelve el puzzle usando Búsqueda en Anchura (BFS).
        
        Returns:
            dict: Diccionario con los resultados y métricas de la búsqueda
        """
        start_time = time.time()
        
        # Inicializar el nodo raíz
        root = PuzzleNode(state=self.initial_state)
        
        # Verificar si el estado inicial ya es el objetivo
        if self._is_goal(root.state):
            self.execution_time = time.time() - start_time
            self.nodes_expanded = 0
            self.path_length = 0
            return {
                'success': True,
                'path': [],
                'nodes_expanded': 0,
                'path_length': 0,
                'execution_time': self.execution_time
            }
        
        # Inicializar la cola y el conjunto de visitados
        queue = deque([root])
        visited = set()
        visited.add(root)
        
        self.nodes_expanded = 0
        
        while queue:
            # Obtener el siguiente nodo de la cola
            node = queue.popleft()
            self.nodes_expanded += 1
            
            # Expandir el nodo actual
            for action in node.get_possible_actions():
                child = node.get_child_node(action)
                
                # Verificar si el estado ya ha sido visitado
                if child not in visited:
                    # Verificar si el nuevo estado es el objetivo
                    if self._is_goal(child.state):
                        path = child.get_path()
                        self.path_length = len(path)
                        self.execution_time = time.time() - start_time
                        return {
                            'success': True,
                            'path': path,
                            'nodes_expanded': self.nodes_expanded,
                            'path_length': self.path_length,
                            'execution_time': self.execution_time
                        }
                    
                    # Añadir el nodo a la cola y al conjunto de visitados
                    queue.append(child)
                    visited.add(child)
        
        # Si la cola se vacía sin encontrar la solución
        self.execution_time = time.time() - start_time
        return {
            'success': False,
            'path': [],
            'nodes_expanded': self.nodes_expanded,
            'path_length': 0,
            'execution_time': self.execution_time
        }
    
    def solve_dfs_limited(self, depth_limit=20):
        """
        Resuelve el puzzle usando Búsqueda en Profundidad Limitada (DFS limitada).
        
        Args:
            depth_limit: Límite de profundidad para la búsqueda
            
        Returns:
            dict: Diccionario con los resultados y métricas de la búsqueda
        """
        start_time = time.time()
        
        # Inicializar el nodo raíz
        root = PuzzleNode(state=self.initial_state)
        
        # Verificar si el estado inicial ya es el objetivo
        if self._is_goal(root.state):
            self.execution_time = time.time() - start_time
            self.nodes_expanded = 0
            self.path_length = 0
            return {
                'success': True,
                'path': [],
                'nodes_expanded': 0,
                'path_length': 0,
                'execution_time': self.execution_time
            }
        
        # Inicializar la pila y el conjunto de visitados
        stack = [root]
        visited = set()
        visited.add(root)
        
        self.nodes_expanded = 0
        
        while stack:
            # Obtener el siguiente nodo de la pila
            node = stack.pop()
            self.nodes_expanded += 1
            
            # No expandir nodos más allá del límite de profundidad
            if node.depth >= depth_limit:
                continue
            
            # Expandir el nodo actual (en orden inverso para preservar el orden de exploración)
            for action in reversed(node.get_possible_actions()):
                child = node.get_child_node(action)
                
                # Verificar si el estado ya ha sido visitado
                if child not in visited:
                    # Verificar si el nuevo estado es el objetivo
                    if self._is_goal(child.state):
                        path = child.get_path()
                        self.path_length = len(path)
                        self.execution_time = time.time() - start_time
                        return {
                            'success': True,
                            'path': path,
                            'nodes_expanded': self.nodes_expanded,
                            'path_length': self.path_length,
                            'execution_time': self.execution_time
                        }
                    
                    # Añadir el nodo a la pila y al conjunto de visitados
                    stack.append(child)
                    visited.add(child)
        
        # Si la pila se vacía sin encontrar la solución
        self.execution_time = time.time() - start_time
        return {
            'success': False,
            'path': [],
            'nodes_expanded': self.nodes_expanded,
            'path_length': 0,
            'execution_time': self.execution_time
        }
    
    def solve_astar(self):
        """
        Resuelve el puzzle usando el algoritmo A* con heurística de Manhattan.
        
        Returns:
            dict: Diccionario con los resultados y métricas de la búsqueda
        """
        start_time = time.time()
        
        # Inicializar el nodo raíz
        root = PuzzleNode(state=self.initial_state)
        
        # Verificar si el estado inicial ya es el objetivo
        if self._is_goal(root.state):
            self.execution_time = time.time() - start_time
            self.nodes_expanded = 0
            self.path_length = 0
            return {
                'success': True,
                'path': [],
                'nodes_expanded': 0,
                'path_length': 0,
                'execution_time': self.execution_time
            }
        
        # Inicializar la cola de prioridad y el conjunto de visitados
        # El costo es f(n) = g(n) + h(n), donde g(n) es el costo hasta ahora (profundidad)
        # y h(n) es la heurística (distancia de Manhattan)
        h_root = self._get_manhattan_distance(root.state)
        f_root = root.depth + h_root
        
        # Cola de prioridad como lista de tuplas (f(n), nodo)
        priority_queue = [(f_root, root)]
        visited = set()
        visited.add(root)
        
        self.nodes_expanded = 0
        
        while priority_queue:
            # Obtener el nodo con menor f(n) de la cola de prioridad
            _, node = heapq.heappop(priority_queue)
            self.nodes_expanded += 1
            
            # Expandir el nodo actual
            for action in node.get_possible_actions():
                child = node.get_child_node(action)
                
                # Verificar si el estado ya ha sido visitado
                if child not in visited:
                    # Verificar si el nuevo estado es el objetivo
                    if self._is_goal(child.state):
                        path = child.get_path()
                        self.path_length = len(path)
                        self.execution_time = time.time() - start_time
                        return {
                            'success': True,
                            'path': path,
                            'nodes_expanded': self.nodes_expanded,
                            'path_length': self.path_length,
                            'execution_time': self.execution_time
                        }
                    
                    # Calcular f(n) = g(n) + h(n) para el nodo hijo
                    h_child = self._get_manhattan_distance(child.state)
                    f_child = child.depth + h_child
                    
                    # Añadir el nodo a la cola de prioridad y al conjunto de visitados
                    heapq.heappush(priority_queue, (f_child, child))
                    visited.add(child)
        
        # Si la cola se vacía sin encontrar la solución
        self.execution_time = time.time() - start_time
        return {
            'success': False,
            'path': [],
            'nodes_expanded': self.nodes_expanded,
            'path_length': 0,
            'execution_time': self.execution_time
        }