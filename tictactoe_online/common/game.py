"""
Game module - represents a game room/session.
"""

from typing import List, Optional, Dict, Tuple
from enum import Enum
import uuid
from .board import Board
from .player import Player


class GameState(Enum):
    """Enumeration of possible game states."""
    WAITING = "WAITING"  # Waiting for players to join
    PLAYING = "PLAYING"  # Game in progress
    FINISHED = "FINISHED"  # Game finished (won or draw)


class Game:
    """
    Represents a game room/session.
    
    Attributes:
        game_id: Unique identifier for the game
        num_players: Total number of players needed
        players: List of players in the game
        board: Game board
        current_player_index: Index of current player
        state: Current game state
        winner: Winner player (if game finished)
    """
    
    def __init__(self, game_id: Optional[str], num_players: int):
        """
        Initialize a game.
        
        Args:
            game_id: Unique game identifier (generated if None)
            num_players: Number of players needed for this game
        """
        self.game_id = game_id or str(uuid.uuid4())[:8]
        self.num_players = num_players
        self.players: List[Player] = []
        self.board = Board(num_players)
        self.current_player_index = 0
        self.state = GameState.WAITING
        self.winner: Optional[Player] = None
        self.is_draw = False
    
    def add_player(self, player: Player) -> bool:
        """
        Add a player to the game.
        
        Args:
            player: Player to add
            
        Returns:
            True if player added successfully, False otherwise
        """
        if len(self.players) >= self.num_players:
            return False
        
        if player in self.players:
            return False
        
        self.players.append(player)
        
        # Start game when all players have joined
        if len(self.players) == self.num_players:
            self.state = GameState.PLAYING
        
        return True
    
    def remove_player(self, player: Player) -> bool:
        """
        Remove a player from the game.
        
        Args:
            player: Player to remove
            
        Returns:
            True if player removed successfully, False otherwise
        """
        if player not in self.players:
            return False
        
        player.is_active = False
        
        # If game was in progress, end it
        if self.state == GameState.PLAYING:
            self.state = GameState.FINISHED
        
        return True
    
    def get_current_player(self) -> Optional[Player]:
        """
        Get the current player whose turn it is.
        
        Returns:
            Current player or None if game not started
        """
        if self.state != GameState.PLAYING:
            return None
        
        # Skip inactive players
        attempts = 0
        while attempts < len(self.players):
            player = self.players[self.current_player_index]
            if player.is_active:
                return player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            attempts += 1
        
        return None
    
    def make_move(self, player: Player, row: int, col: int) -> Tuple[bool, Optional[str]]:
        """
        Make a move in the game.
        
        Args:
            player: Player making the move
            row: Row index
            col: Column index
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Validate game state
        if self.state != GameState.PLAYING:
            return False, "Game is not in progress"
        
        # Validate it's the player's turn
        current_player = self.get_current_player()
        if current_player != player:
            return False, "Not your turn"
        
        # Validate and make the move
        if not self.board.make_move(row, col, player.symbol):
            return False, "Invalid move"
        
        # Check for winner
        winner_symbol = self.board.check_winner(row, col)
        if winner_symbol:
            self.winner = player
            self.state = GameState.FINISHED
            return True, None
        
        # Check for draw
        if self.board.is_full():
            self.is_draw = True
            self.state = GameState.FINISHED
            return True, None
        
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        return True, None
    
    def get_active_player_count(self) -> int:
        """
        Get number of active players.
        
        Returns:
            Number of active players
        """
        return sum(1 for p in self.players if p.is_active)
    
    def is_ready(self) -> bool:
        """
        Check if game is ready to start.
        
        Returns:
            True if all players have joined
        """
        return len(self.players) == self.num_players
    
    def to_dict(self, include_board: bool = True) -> dict:
        """
        Convert game to dictionary for serialization.
        
        Args:
            include_board: Whether to include board state
            
        Returns:
            Dictionary representation of game
        """
        data = {
            'game_id': self.game_id,
            'num_players': self.num_players,
            'current_player_count': len(self.players),
            'state': self.state.value,
            'is_draw': self.is_draw
        }
        
        if include_board:
            data['board'] = self.board.to_dict()
            data['players'] = [p.to_dict() for p in self.players]
            data['current_player_index'] = self.current_player_index
            
            current_player = self.get_current_player()
            if current_player:
                data['current_player_id'] = current_player.player_id
            
            if self.winner:
                data['winner'] = self.winner.to_dict()
        
        return data
    
    def __repr__(self) -> str:
        return (f"Game(id={self.game_id}, players={len(self.players)}/{self.num_players}, "
                f"state={self.state.value})")