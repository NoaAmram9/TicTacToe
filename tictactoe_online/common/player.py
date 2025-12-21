"""
Player module - represents a player in the game.
"""

from typing import Optional


class Player:
    """
    Represents a player in the Tic-Tac-Toe game.
    
    Attributes:
        player_id: Unique identifier for the player
        name: Display name of the player
        symbol: Symbol used on the board (X, O, Δ, etc.)
        socket: Network socket for communication (server-side only)
    """
    
    # Available symbols for players
    SYMBOLS = ['X', 'O', 'Δ', '□', '◇', '★', '♠', '♣', '♥', '♦']
    
    def __init__(self, player_id: str, name: str, symbol: str, socket=None):
        """
        Initialize a player.
        
        Args:
            player_id: Unique identifier
            name: Player's display name
            symbol: Symbol to use on the board
            socket: Network socket (optional, server-side only)
        """
        self.player_id = player_id
        self.name = name
        self.symbol = symbol
        self.socket = socket
        self.is_active = True
    
    def to_dict(self) -> dict:
        """
        Convert player to dictionary for serialization.
        
        Returns:
            Dictionary representation of player
        """
        return {
            'player_id': self.player_id,
            'name': self.name,
            'symbol': self.symbol,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Player':
        """
        Create player from dictionary.
        
        Args:
            data: Dictionary containing player data
            
        Returns:
            Player instance
        """
        player = Player(
            player_id=data['player_id'],
            name=data['name'],
            symbol=data['symbol']
        )
        player.is_active = data.get('is_active', True)
        return player
    
    def __repr__(self) -> str:
        return f"Player(id={self.player_id}, name={self.name}, symbol={self.symbol})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Player):
            return False
        return self.player_id == other.player_id
    
    def __hash__(self) -> int:
        return hash(self.player_id)