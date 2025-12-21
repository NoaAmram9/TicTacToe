"""
Protocol definitions for Tic-Tac-Toe network communication.
All messages are sent as JSON strings followed by newline delimiter.
"""

import json
from enum import Enum
from typing import Dict, Any, Optional, List


class MessageType(Enum):
    """Enumeration of all message types in the protocol."""
    # Client -> Server
    CREATE_GAME = "CREATE_GAME"
    JOIN_GAME = "JOIN_GAME"
    LIST_GAMES = "LIST_GAMES"
    MAKE_MOVE = "MAKE_MOVE"
    QUIT_GAME = "QUIT_GAME"
    DISCONNECT = "DISCONNECT"
    
    # Server -> Client
    GAME_CREATED = "GAME_CREATED"
    GAME_JOINED = "GAME_JOINED"
    GAME_LIST = "GAME_LIST"
    GAME_STATE = "GAME_STATE"
    MOVE_RESULT = "MOVE_RESULT"
    GAME_OVER = "GAME_OVER"
    ERROR = "ERROR"
    PLAYER_JOINED = "PLAYER_JOINED"
    PLAYER_LEFT = "PLAYER_LEFT"


class Protocol:
    """Protocol utilities for encoding/decoding messages."""
    
    DELIMITER = b'\n'
    ENCODING = 'utf-8'
    
    @staticmethod
    def encode_message(msg_type: MessageType, data: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Encode a message to bytes.
        
        Args:
            msg_type: Type of message
            data: Optional message data
            
        Returns:
            Encoded message as bytes
        """
        message = {
            'type': msg_type.value,
            'data': data or {}
        }
        json_str = json.dumps(message)
        return (json_str + '\n').encode(Protocol.ENCODING)
    
    @staticmethod
    def decode_message(data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decode a message from bytes.
        
        Args:
            data: Raw bytes to decode
            
        Returns:
            Decoded message dictionary or None if invalid
        """
        try:
            json_str = data.decode(Protocol.ENCODING).strip()
            return json.loads(json_str)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error decoding message: {e}")
            return None
    
    @staticmethod
    def create_game_request(num_players: int) -> bytes:
        """Create a CREATE_GAME request."""
        return Protocol.encode_message(
            MessageType.CREATE_GAME,
            {'num_players': num_players}
        )
    
    @staticmethod
    def join_game_request(game_id: str, player_name: str) -> bytes:
        """Create a JOIN_GAME request."""
        return Protocol.encode_message(
            MessageType.JOIN_GAME,
            {'game_id': game_id, 'player_name': player_name}
        )
    
    @staticmethod
    def list_games_request() -> bytes:
        """Create a LIST_GAMES request."""
        return Protocol.encode_message(MessageType.LIST_GAMES)
    
    @staticmethod
    def make_move_request(row: int, col: int) -> bytes:
        """Create a MAKE_MOVE request."""
        return Protocol.encode_message(
            MessageType.MAKE_MOVE,
            {'row': row, 'col': col}
        )
    
    @staticmethod
    def quit_game_request() -> bytes:
        """Create a QUIT_GAME request."""
        return Protocol.encode_message(MessageType.QUIT_GAME)
    
    @staticmethod
    def disconnect_request() -> bytes:
        """Create a DISCONNECT request."""
        return Protocol.encode_message(MessageType.DISCONNECT)


# GAME_OVER message can include these fields:
# - is_draw: bool - True if game ended in draw
# - winner: dict - Winner player data (if not draw and not abandoned)
# - abandoned: bool - True if game ended due to players leaving
# - reason: str - Explanation for game end (if abandoned)