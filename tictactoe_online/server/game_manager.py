"""
Game Manager module - manages all active games on the server.
"""

import logging
from typing import Dict, Optional, List
from common.game import Game, GameState
from common.player import Player


class GameManager:
    """
    Manages all active games on the server.
    
    Attributes:
        games: Dictionary mapping game_id to Game objects
        player_to_game: Dictionary mapping player_id to game_id
    """
    
    def __init__(self):
        """Initialize the game manager."""
        self.games: Dict[str, Game] = {}
        self.player_to_game: Dict[str, str] = {}
        self.logger = logging.getLogger("GameManager")
    
    def create_game(self, num_players: int) -> Game:
        """
        Create a new game.
        
        Args:
            num_players: Number of players for the game
            
        Returns:
            Created game object
        """
        game = Game(None, num_players)
        self.games[game.game_id] = game
        self.logger.info(f"Created game {game.game_id} for {num_players} players")
        return game
    
    def get_game(self, game_id: str) -> Optional[Game]:
        """
        Get a game by ID.
        
        Args:
            game_id: Game identifier
            
        Returns:
            Game object or None if not found
        """
        return self.games.get(game_id)
    
    def join_game(self, game_id: str, player: Player) -> tuple[bool, Optional[str]]:
        """
        Add a player to a game.
        
        Args:
            game_id: Game to join
            player: Player to add
            
        Returns:
            Tuple of (success, error_message)
        """
        game = self.get_game(game_id)
        if not game:
            return False, "Game not found"
        
        if game.state != GameState.WAITING:
            return False, "Game already started"
        
        # Check if player is already in another game
        if player.player_id in self.player_to_game:
            old_game_id = self.player_to_game[player.player_id]
            old_game = self.get_game(old_game_id)
            
            # If old game is finished or doesn't exist, clean it up
            if not old_game or old_game.state == GameState.FINISHED:
                del self.player_to_game[player.player_id]
                self.logger.info(f"Cleaned up player {player.player_id} from finished/missing game")
            else:
                return False, "Player already in a game"
        
        if not game.add_player(player):
            return False, "Game is full"
        
        self.player_to_game[player.player_id] = game_id
        self.logger.info(f"Player {player.player_id} joined game {game_id}")
        
        return True, None
    
    def leave_game(self, player_id: str) -> Optional[Game]:
        """
        Remove a player from their current game.
        
        Args:
            player_id: Player to remove
            
        Returns:
            Game the player left, or None
        """
        game_id = self.player_to_game.get(player_id)
        if not game_id:
            return None
        
        game = self.get_game(game_id)
        if not game:
            return None
        
        # Find and remove the player
        player = None
        for p in game.players:
            if p.player_id == player_id:
                player = p
                break
        
        if player:
            game.remove_player(player)
            del self.player_to_game[player_id]
            self.logger.info(f"Player {player_id} left game {game_id}")
            
            # Clean up finished games with no active players
            if game.get_active_player_count() == 0:
                self._cleanup_game(game_id)
        
        return game
    
    def get_player_game(self, player_id: str) -> Optional[Game]:
        """
        Get the game a player is currently in.
        
        Args:
            player_id: Player identifier
            
        Returns:
            Game object or None
        """
        game_id = self.player_to_game.get(player_id)
        if game_id:
            return self.get_game(game_id)
        return None
    
    def list_available_games(self) -> List[Dict]:
        """
        Get list of games that can be joined.
        
        Returns:
            List of game dictionaries
        """
        available = []
        for game in self.games.values():
            if game.state == GameState.WAITING:
                available.append(game.to_dict(include_board=False))
        return available
    
    def make_move(self, player_id: str, row: int, col: int) -> tuple[bool, Optional[str], Optional[Game]]:
        """
        Process a player's move.
        
        Args:
            player_id: Player making the move
            row: Row index
            col: Column index
            
        Returns:
            Tuple of (success, error_message, game)
        """
        game = self.get_player_game(player_id)
        if not game:
            return False, "Not in a game", None
        
        # Find the player
        player = None
        for p in game.players:
            if p.player_id == player_id:
                player = p
                break
        
        if not player:
            return False, "Player not found in game", None
        
        success, error = game.make_move(player, row, col)
        
        # Clean up if game is finished
        if game.state == GameState.FINISHED:
            # Remove all player mappings so they can join new games
            for p in game.players:
                if p.player_id in self.player_to_game:
                    del self.player_to_game[p.player_id]
            self.logger.info(f"Game {game.game_id} finished - freed all players")
        
        return success, error, game
    
    def _cleanup_game(self, game_id: str):
        """
        Remove a game from the manager.
        
        Args:
            game_id: Game to remove
        """
        if game_id in self.games:
            game = self.games[game_id]
            
            # Remove all player mappings
            for player in game.players:
                if player.player_id in self.player_to_game:
                    del self.player_to_game[player.player_id]
            
            # Remove the game
            del self.games[game_id]
            self.logger.info(f"Cleaned up game {game_id}")
    
    def get_stats(self) -> Dict:
        """
        Get server statistics.
        
        Returns:
            Dictionary with server stats
        """
        return {
            'total_games': len(self.games),
            'waiting_games': sum(1 for g in self.games.values() if g.state == GameState.WAITING),
            'active_games': sum(1 for g in self.games.values() if g.state == GameState.PLAYING),
            'finished_games': sum(1 for g in self.games.values() if g.state == GameState.FINISHED),
            'total_players': len(self.player_to_game)
        }