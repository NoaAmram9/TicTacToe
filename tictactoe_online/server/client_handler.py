"""
Client Handler module - manages individual client connections.
"""

import socket
import threading
import logging
from typing import Optional, Callable, Dict, Any
from common.protocol import Protocol, MessageType


class ClientHandler:
    """
    Handles communication with a single client.
    
    Attributes:
        client_socket: Socket connected to the client
        client_address: Address of the client
        player_id: Unique identifier for this client
        current_game_id: ID of game this client is in
        message_callback: Callback for processing messages
    """
    
    def __init__(self, 
                 client_socket: socket.socket,
                 client_address: tuple,
                 player_id: str,
                 message_callback: Callable[[str, Dict[str, Any]], None]):
        """
        Initialize client handler.
        
        Args:
            client_socket: Connected socket
            client_address: Client's address
            player_id: Unique player identifier
            message_callback: Function to call when message received
        """
        self.client_socket = client_socket
        self.client_address = client_address
        self.player_id = player_id
        self.current_game_id: Optional[str] = None
        self.message_callback = message_callback
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None
        self.buffer = b''
        self.logger = logging.getLogger(f"ClientHandler-{player_id}")
    
    def start(self):
        """Start handling the client connection."""
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        self.logger.info(f"Started handling client {self.client_address}")
    
    def _receive_loop(self):
        """Main loop for receiving messages from client."""
        try:
            while self.running:
                # Receive data
                data = self.client_socket.recv(4096)
                if not data:
                    self.logger.info(f"Client {self.client_address} disconnected")
                    break
                
                # Add to buffer
                self.buffer += data
                
                # Process complete messages (delimited by newline)
                while Protocol.DELIMITER in self.buffer:
                    message_bytes, self.buffer = self.buffer.split(Protocol.DELIMITER, 1)
                    self._process_message(message_bytes)
        
        except ConnectionResetError:
            self.logger.warning(f"Connection reset by client {self.client_address}")
        except Exception as e:
            self.logger.error(f"Error in receive loop: {e}")
        finally:
            self.stop()
    
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
        
        # Call the callback to process the message
        if self.message_callback:
            try:
                self.message_callback(self.player_id, message)
            except Exception as e:
                self.logger.error(f"Error in message callback: {e}")
    
    def send_message(self, msg_type: MessageType, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a message to the client.
        
        Args:
            msg_type: Type of message
            data: Message data
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = Protocol.encode_message(msg_type, data)
            self.client_socket.sendall(message)
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def stop(self):
        """Stop handling the client and close connection."""
        if not self.running:
            return
        
        self.running = False
        
        try:
            self.client_socket.close()
        except:
            pass
        
        # Notify server that client disconnected
        if self.message_callback:
            try:
                self.message_callback(self.player_id, {
                    'type': MessageType.DISCONNECT.value,
                    'data': {}
                })
            except:
                pass
        
        self.logger.info(f"Stopped handling client {self.client_address}")
    
    def __repr__(self) -> str:
        return f"ClientHandler(player_id={self.player_id}, address={self.client_address})"