"""
Server module - main server implementation.
"""

import socket
import threading
import logging
import uuid
from typing import Dict, Optional
from common.protocol import Protocol, MessageType
from common.player import Player
from .client_handler import ClientHandler
from .game_manager import GameManager


class Server:
    """
    Main Tic-Tac-Toe game server.
    
    Manages client connections and game sessions.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5555):
        """
        Initialize the server.
        
        Args:
            host: Host address to bind to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.accept_thread: Optional[threading.Thread] = None
        
        # Client management
        self.clients: Dict[str, ClientHandler] = {}
        self.clients_lock = threading.Lock()
        
        # Game management
        self.game_manager = GameManager()
        
        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("Server")
    
    def start(self):
        """Start the server."""
        try:
            # Create and configure socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"Server started on {self.host}:{self.port}")
            
            # Start accepting connections
            self.accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.accept_thread.start()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def _accept_connections(self):
        """Accept incoming client connections."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.logger.info(f"New connection from {client_address}")
                
                # Create unique player ID
                player_id = str(uuid.uuid4())[:8]
                
                # Create client handler
                handler = ClientHandler(
                    client_socket,
                    client_address,
                    player_id,
                    self._handle_client_message
                )
                
                with self.clients_lock:
                    self.clients[player_id] = handler
                
                handler.start()
            
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error accepting connection: {e}")
    
    def _handle_client_message(self, player_id: str, message: Dict):
        """
        Handle a message from a client.
        
        Args:
            player_id: ID of the client
            message: Message dictionary
        """
        msg_type = message.get('type')
        msg_data = message.get('data', {})
        
        try:
            if msg_type == MessageType.CREATE_GAME.value:
                self._handle_create_game(player_id, msg_data)
            
            elif msg_type == MessageType.JOIN_GAME.value:
                self._handle_join_game(player_id, msg_data)
            
            elif msg_type == MessageType.LIST_GAMES.value:
                self._handle_list_games(player_id)
            
            elif msg_type == MessageType.MAKE_MOVE.value:
                self._handle_make_move(player_id, msg_data)
            
            elif msg_type == MessageType.QUIT_GAME.value:
                self._handle_quit_game(player_id)
            
            elif msg_type == MessageType.DISCONNECT.value:
                self._handle_disconnect(player_id)
        
        except Exception as e:
            self.logger.error(f"Error handling message from {player_id}: {e}")
            self._send_error(player_id, str(e))
    
    def _handle_create_game(self, player_id: str, data: Dict):
        """Handle CREATE_GAME request."""
        num_players = data.get('num_players', 2)
        
        if num_players < 2 or num_players > 10:
            self._send_error(player_id, "Invalid number of players (2-10)")
            return
        
        # Create game
        game = self.game_manager.create_game(num_players)
        
        # Send confirmation
        handler = self.clients.get(player_id)
        if handler:
            handler.send_message(MessageType.GAME_CREATED, {
                'game_id': game.game_id,
                'num_players': num_players
            })
    
    def _handle_join_game(self, player_id: str, data: Dict):
        """Handle JOIN_GAME request."""
        game_id = data.get('game_id')
        player_name = data.get('player_name', f'Player-{player_id[:4]}')
        
        if not game_id:
            self._send_error(player_id, "Game ID required")
            return
        
        game = self.game_manager.get_game(game_id)
        if not game:
            self._send_error(player_id, "Game not found")
            return
        
        # Determine symbol for this player
        symbol = Player.SYMBOLS[len(game.players)]
        
        # Create player
        handler = self.clients.get(player_id)
        player = Player(player_id, player_name, symbol, handler)
        
        # Join game
        success, error = self.game_manager.join_game(game_id, player)
        
        if not success:
            self._send_error(player_id, error)
            return
        
        # Send confirmation to joining player
        if handler:
            handler.current_game_id = game_id
            handler.send_message(MessageType.GAME_JOINED, {
                'game_id': game_id,
                'player_id': player_id,
                'symbol': symbol
            })
        
        # Notify all players in the game
        self._broadcast_game_state(game_id)
        self._broadcast_to_game(game_id, MessageType.PLAYER_JOINED, {
            'player': player.to_dict()
        })
    
    def _handle_list_games(self, player_id: str):
        """Handle LIST_GAMES request."""
        games = self.game_manager.list_available_games()
        
        handler = self.clients.get(player_id)
        if handler:
            handler.send_message(MessageType.GAME_LIST, {
                'games': games
            })
    
    def _handle_make_move(self, player_id: str, data: Dict):
        """Handle MAKE_MOVE request."""
        row = data.get('row')
        col = data.get('col')
        
        if row is None or col is None:
            self._send_error(player_id, "Row and column required")
            return
        
        success, error, game = self.game_manager.make_move(player_id, row, col)
        
        if not success:
            self._send_error(player_id, error)
            return
        
        # Broadcast updated game state to all players
        self._broadcast_game_state(game.game_id)
        
        # If game is finished, send game over message and clean up
        if game.state.value == "FINISHED":
            game_over_data = {
                'is_draw': game.is_draw
            }
            if game.winner:
                game_over_data['winner'] = game.winner.to_dict()
            
            self._broadcast_to_game(game.game_id, MessageType.GAME_OVER, game_over_data)
            
            # Note: Player mappings are already cleaned up in game_manager.make_move()
            # when the game finishes, so players can join new games immediately
    
    def _handle_quit_game(self, player_id: str):
        """Handle QUIT_GAME request."""
        game = self.game_manager.leave_game(player_id)
        
        if game:
            # Update client handler
            handler = self.clients.get(player_id)
            if handler:
                handler.current_game_id = None
            
            # Notify other players that someone left
            self._broadcast_to_game(game.game_id, MessageType.PLAYER_LEFT, {
                'player_id': player_id
            })
            
            # Broadcast updated game state (with player marked as inactive)
            self._broadcast_game_state(game.game_id)
            
            # If game was in progress and now finished due to player leaving
            if game.state.value == "FINISHED":
                # Check if there's actually a winner or if game ended due to abandonment
                active_players = game.get_active_player_count()
                
                if active_players == 0:
                    # All players left - just end silently
                    self.logger.info(f"All players left game {game.game_id}")
                elif active_players == 1 and not game.winner:
                    # Only one player left and no winner - game abandoned
                    self._broadcast_to_game(game.game_id, MessageType.GAME_OVER, {
                        'is_draw': False,
                        'abandoned': True,
                        'reason': 'Other players left the game'
                    })
                    # Clean up player mappings
                    for p in game.players:
                        if p.player_id in self.game_manager.player_to_game:
                            del self.game_manager.player_to_game[p.player_id]
                elif game.winner:
                    # There's an actual winner
                    self._broadcast_to_game(game.game_id, MessageType.GAME_OVER, {
                        'is_draw': False,
                        'winner': game.winner.to_dict()
                    })
                    # Clean up player mappings
                    for p in game.players:
                        if p.player_id in self.game_manager.player_to_game:
                            del self.game_manager.player_to_game[p.player_id]
    
    def _handle_disconnect(self, player_id: str):
        """Handle client disconnect."""
        self.logger.info(f"Client {player_id} disconnecting")
        
        # Remove from game if in one
        self._handle_quit_game(player_id)
        
        # Remove client handler
        with self.clients_lock:
            if player_id in self.clients:
                handler = self.clients[player_id]
                handler.stop()
                del self.clients[player_id]
    
    def _broadcast_game_state(self, game_id: str):
        """
        Broadcast current game state to all players in a game.
        
        Args:
            game_id: Game to broadcast to
        """
        game = self.game_manager.get_game(game_id)
        if not game:
            return
        
        game_data = game.to_dict(include_board=True)
        self._broadcast_to_game(game_id, MessageType.GAME_STATE, game_data)
    
    def _broadcast_to_game(self, game_id: str, msg_type: MessageType, data: Dict):
        """
        Send a message to all players in a game.
        
        Args:
            game_id: Game ID
            msg_type: Message type
            data: Message data
        """
        game = self.game_manager.get_game(game_id)
        if not game:
            return
        
        with self.clients_lock:
            for player in game.players:
                handler = self.clients.get(player.player_id)
                if handler:
                    handler.send_message(msg_type, data)
    
    def _send_error(self, player_id: str, error_message: str):
        """
        Send an error message to a client.
        
        Args:
            player_id: Client ID
            error_message: Error message
        """
        handler = self.clients.get(player_id)
        if handler:
            handler.send_message(MessageType.ERROR, {
                'message': error_message
            })
    
    def stop(self):
        """Stop the server."""
        self.logger.info("Stopping server...")
        self.running = False
        
        # Close all client connections
        with self.clients_lock:
            for handler in list(self.clients.values()):
                handler.stop()
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info("Server stopped")
    
    def get_stats(self) -> Dict:
        """Get server statistics."""
        stats = self.game_manager.get_stats()
        stats['connected_clients'] = len(self.clients)
        return stats