"""
Network Client module - handles communication with the server.
"""

import socket
import threading
import logging
from typing import Optional, Callable, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal
from tictactoe_online.common.protocol import Protocol, MessageType



class NetworkClient(QObject):
    """
    Network client for communicating with the game server.
    
    Signals:
        message_received: Emitted when a message is received (msg_type, data)
        connection_lost: Emitted when connection is lost
        connected: Emitted when connected successfully
    """
    
    message_received = pyqtSignal(str, dict)  # msg_type, data
    connection_lost = pyqtSignal()
    connected = pyqtSignal()
    
    def __init__(self):
        """Initialize the network client."""
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None
        self.buffer = b''
        self.logger = logging.getLogger("NetworkClient")
        self.host: Optional[str] = None
        self.port: Optional[int] = None
    
    def connect(self, host: str, port: int) -> tuple[bool, Optional[str]]:
        """
        Connect to the server.
        
        Args:
            host: Server hostname or IP
            port: Server port
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # 5 second timeout for connection
            self.socket.connect((host, port))
            self.socket.settimeout(None)  # Remove timeout after connection
            
            self.host = host
            self.port = port
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            self.logger.info(f"Connected to server at {host}:{port}")
            self.connected.emit()
            
            return True, None
        
        except socket.timeout:
            return False, "Connection timeout"
        except ConnectionRefusedError:
            return False, "Connection refused - is the server running?"
        except Exception as e:
            return False, f"Connection error: {e}"
    
    def _receive_loop(self):
        """Main loop for receiving messages from server."""
        try:
            while self.running:
                # Receive data
                data = self.socket.recv(4096)
                if not data:
                    self.logger.info("Server closed connection")
                    break
                
                # Add to buffer
                self.buffer += data
                
                # Process complete messages (delimited by newline)
                while Protocol.DELIMITER in self.buffer:
                    message_bytes, self.buffer = self.buffer.split(Protocol.DELIMITER, 1)
                    self._process_message(message_bytes)
        
        except ConnectionResetError:
            self.logger.warning("Connection reset by server")
        except Exception as e:
            if self.running:
                self.logger.error(f"Error in receive loop: {e}")
        finally:
            self.disconnect()
            self.connection_lost.emit()
    
    def _process_message(self, message_bytes: bytes):
        """
        Process a received message.
        
        Args:
            message_bytes: Raw message bytes
        """
        message = Protocol.decode_message(message_bytes)
        if not message:
            self.logger.warning("Received invalid message")
            return
        
        msg_type = message.get('type')
        msg_data = message.get('data', {})
        
        self.logger.debug(f"Received message: {msg_type}")
        
        # Emit signal for message handling in GUI thread
        self.message_received.emit(msg_type, msg_data)
    
    def send_message(self, msg_type: MessageType, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a message to the server.
        
        Args:
            msg_type: Type of message
            data: Message data
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.socket or not self.running:
            self.logger.warning("Cannot send message - not connected")
            return False
        
        try:
            message = Protocol.encode_message(msg_type, data)
            self.socket.sendall(message)
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def create_game(self, num_players: int) -> bool:
        """Send CREATE_GAME request."""
        return self.send_message(MessageType.CREATE_GAME, {'num_players': num_players})
    
    def join_game(self, game_id: str, player_name: str) -> bool:
        """Send JOIN_GAME request."""
        return self.send_message(MessageType.JOIN_GAME, {
            'game_id': game_id,
            'player_name': player_name
        })
    
    def list_games(self) -> bool:
        """Send LIST_GAMES request."""
        return self.send_message(MessageType.LIST_GAMES)
    
    def make_move(self, row: int, col: int) -> bool:
        """Send MAKE_MOVE request."""
        return self.send_message(MessageType.MAKE_MOVE, {
            'row': row,
            'col': col
        })
    
    def quit_game(self) -> bool:
        """Send QUIT_GAME request."""
        return self.send_message(MessageType.QUIT_GAME)
    
    def disconnect(self):
        """Disconnect from the server."""
        if not self.running:
            return
        
        self.running = False
        
        # Send disconnect message
        try:
            if self.socket:
                self.send_message(MessageType.DISCONNECT)
        except:
            pass
        
        # Close socket
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        
        self.logger.info("Disconnected from server")
    
    def is_connected(self) -> bool:
        """Check if connected to server."""
        return self.running and self.socket is not None