"""
Board module - represents the Tic-Tac-Toe game board.
"""

from typing import Optional, List, Tuple
import copy


class Board:
    """
    Represents a Tic-Tac-Toe game board.
    
    The board size is (num_players + 1)^2 squares.
    Players need to get num_players symbols in a row to win.
    
    Attributes:
        num_players: Number of players in the game
        size: Size of the board (num_players + 1)
        grid: 2D list representing the board state
        win_length: Number of symbols needed in a row to win (equals num_players)
    """
    
    def __init__(self, num_players: int):
        """
        Initialize a game board.
        
        Args:
            num_players: Number of players (2-10)
        """
        if num_players < 2 or num_players > 10:
            raise ValueError("Number of players must be between 2 and 10")
        
        self.num_players = num_players
        self.size = num_players + 1
        self.win_length = num_players + 1  # Win length equals number of players!
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.move_count = 0
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """
        Check if a move is valid.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            
        Returns:
            True if the move is valid, False otherwise
        """
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        return self.grid[row][col] is None
    
    def make_move(self, row: int, col: int, symbol: str) -> bool:
        """
        Make a move on the board.
        
        Args:
            row: Row index
            col: Column index
            symbol: Player's symbol
            
        Returns:
            True if move was successful, False otherwise
        """
        if not self.is_valid_move(row, col):
            return False
        
        self.grid[row][col] = symbol
        self.move_count += 1
        return True
    
    def check_winner(self, row: int, col: int) -> Optional[str]:
        """
        Check if the last move resulted in a win.
        
        Args:
            row: Row of last move
            col: Column of last move
            
        Returns:
            Winning symbol if there's a winner, None otherwise
        """
        symbol = self.grid[row][col]
        if symbol is None:
            return None
        
        # Check all four directions: horizontal, vertical, diagonal, anti-diagonal
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal
            (1, -1)   # Anti-diagonal
        ]
        
        for dr, dc in directions:
            count = 1  # Count the current cell
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == symbol:
                count += 1
                r += dr
                c += dc
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == symbol:
                count += 1
                r -= dr
                c -= dc
            
            # Win requires exactly num_players symbols in a row
            if count >= self.win_length:
                return symbol
        
        return None
    
    def is_full(self) -> bool:
        """
        Check if the board is full (draw condition).
        
        Returns:
            True if board is full, False otherwise
        """
        return self.move_count >= self.size * self.size
    
    def get_state(self) -> List[List[Optional[str]]]:
        """
        Get the current board state.
        
        Returns:
            Deep copy of the board grid
        """
        return copy.deepcopy(self.grid)
    
    def to_dict(self) -> dict:
        """
        Convert board to dictionary for serialization.
        
        Returns:
            Dictionary representation of board
        """
        return {
            'num_players': self.num_players,
            'size': self.size,
            'win_length': self.win_length,
            'grid': self.grid,
            'move_count': self.move_count
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Board':
        """
        Create board from dictionary.
        
        Args:
            data: Dictionary containing board data
            
        Returns:
            Board instance
        """
        board = Board(data['num_players'])
        board.grid = data['grid']
        board.move_count = data['move_count']
        return board
    
    def __repr__(self) -> str:
        """String representation of the board."""
        lines = []
        for row in self.grid:
            line = " | ".join([cell if cell else " " for cell in row])
            lines.append(line)
        return "\n".join(lines)