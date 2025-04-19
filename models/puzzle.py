import random
import numpy as np
from copy import deepcopy

class Puzzle:
    """
    Clase que representa el juego 8-puzzle.
    """
    def __init__(self, state=None):
        """
        Inicializa el tablero del 8-puzzle.
        
        Args:
            state: Estado inicial del tablero. Si es None, se crea el estado objetivo.
        """
        # Estado objetivo: números del 1-8 en orden y 0 representa el espacio vacío
        self.goal_state = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        
        if state is not None:
            self.state = np.array(state)
        else:
            # Por defecto, iniciar con el estado objetivo
            self.state = deepcopy(self.goal_state)
        
        # Encontrar la posición del espacio vacío (0)
        self.empty_pos = self._find_empty_position()
        
        # Contador de movimientos
        self.moves_count = 0
    
    def _find_empty_position(self):
        """Encuentra la posición del espacio vacío (0) en el tablero."""
        pos = np.where(self.state == 0)
        return (pos[0][0], pos[1][0])
    
    def is_goal(self):
        """Verifica si el estado actual es el estado objetivo."""
        return np.array_equal(self.state, self.goal_state)
    
    def get_possible_moves(self):
        """
        Devuelve una lista de movimientos posibles (up, down, left, right)
        basados en la posición actual del espacio vacío.
        """
        row, col = self.empty_pos
        moves = []
        
        # Comprueba si se puede mover hacia arriba
        if row > 0:
            moves.append('up')
        
        # Comprueba si se puede mover hacia abajo
        if row < 2:
            moves.append('down')
        
        # Comprueba si se puede mover hacia la izquierda
        if col > 0:
            moves.append('left')
        
        # Comprueba si se puede mover hacia la derecha
        if col < 2:
            moves.append('right')
        
        return moves
    
    def move(self, direction):
        """
        Mueve el espacio vacío en la dirección especificada.
        
        Args:
            direction: Dirección del movimiento ('up', 'down', 'left', 'right')
            
        Returns:
            bool: True si el movimiento fue válido, False en caso contrario.
        """
        row, col = self.empty_pos
        
        # Calcular la nueva posición según la dirección
        if direction == 'up':
            new_row, new_col = row - 1, col
        elif direction == 'down':
            new_row, new_col = row + 1, col
        elif direction == 'left':
            new_row, new_col = row, col - 1
        elif direction == 'right':
            new_row, new_col = row, col + 1
        else:
            return False  # Dirección inválida
        
        # Verificar si la nueva posición está dentro de los límites
        if new_row < 0 or new_row > 2 or new_col < 0 or new_col > 2:
            return False
        
        # Realizar el movimiento (intercambiar valores)
        self.state[row, col] = self.state[new_row, new_col]
        self.state[new_row, new_col] = 0
        
        # Actualizar la posición del espacio vacío
        self.empty_pos = (new_row, new_col)
        
        # Incrementar el contador de movimientos
        self.moves_count += 1
        
        return True
    
    def move_tile(self, tile_row, tile_col):
        """
        Mueve una ficha a la posición vacía si es adyacente.
        
        Args:
            tile_row: Fila de la ficha a mover
            tile_col: Columna de la ficha a mover
            
        Returns:
            bool: True si el movimiento fue válido, False en caso contrario.
        """
        empty_row, empty_col = self.empty_pos
        
        # Verificar si la ficha es adyacente al espacio vacío
        if (abs(tile_row - empty_row) == 1 and tile_col == empty_col) or \
           (abs(tile_col - empty_col) == 1 and tile_row == empty_row):
            
            # Intercambiar la ficha con el espacio vacío
            self.state[empty_row, empty_col] = self.state[tile_row, tile_col]
            self.state[tile_row, tile_col] = 0
            
            # Actualizar la posición del espacio vacío
            self.empty_pos = (tile_row, tile_col)
            
            # Incrementar el contador de movimientos
            self.moves_count += 1
            
            return True
        
        return False
    
    def shuffle(self, num_moves=100):
        """
        Aleatoriza el tablero realizando una serie de movimientos aleatorios válidos.
        
        Args:
            num_moves: Número de movimientos aleatorios a realizar
        """
        # Reiniciar el contador de movimientos
        self.moves_count = 0
        
        for _ in range(num_moves):
            # Obtener los movimientos posibles
            possible_moves = self.get_possible_moves()
            
            # Seleccionar un movimiento aleatorio
            move = random.choice(possible_moves)
            
            # Realizar el movimiento (sin incrementar el contador)
            row, col = self.empty_pos
            if move == 'up':
                new_row, new_col = row - 1, col
            elif move == 'down':
                new_row, new_col = row + 1, col
            elif move == 'left':
                new_row, new_col = row, col - 1
            else:  # move == 'right'
                new_row, new_col = row, col + 1
            
            self.state[row, col] = self.state[new_row, new_col]
            self.state[new_row, new_col] = 0
            self.empty_pos = (new_row, new_col)
    
    def reset(self):
        """Reinicia el tablero al estado objetivo."""
        self.state = deepcopy(self.goal_state)
        self.empty_pos = self._find_empty_position()
        self.moves_count = 0
    
    def set_state(self, new_state):
        """
        Establece un nuevo estado para el tablero.
        
        Args:
            new_state: Nuevo estado del tablero
        """
        self.state = np.array(new_state)
        self.empty_pos = self._find_empty_position()
        self.moves_count = 0
    
    def is_solvable(self):
        """
        Verifica si el estado actual tiene solución.
        Un 8-puzzle es resoluble si el número de inversiones es par.
        """
        # Aplanar el estado actual en una lista
        flat_state = self.state.flatten()
        
        # Contar inversiones (pares de números fuera de orden)
        inversions = 0
        for i in range(9):
            for j in range(i + 1, 9):
                # Ignorar el espacio vacío (0)
                if flat_state[i] != 0 and flat_state[j] != 0 and flat_state[i] > flat_state[j]:
                    inversions += 1
        
        # Un 8-puzzle tiene solución si el número de inversiones es par
        return inversions % 2 == 0
    
    def __str__(self):
        """Representación en cadena del estado actual del tablero."""
        s = ""
        for row in self.state:
            s += " ".join(str(tile) for tile in row) + "\n"
        return s