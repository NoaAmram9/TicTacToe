"""
Main Window - Main GUI application for the Tic-Tac-Toe client.
Beautiful modern design with home page navigation.
"""

from typing import Optional, Dict, List
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QLineEdit, QSpinBox, 
                              QListWidget, QMessageBox, QGroupBox,
                              QDialog, QDialogButtonBox, QFormLayout, QStackedWidget,
                              QListWidgetItem, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QIcon
from .network_client import NetworkClient
from .board_widget import BoardWidget
from ..common.protocol import MessageType
from ..common.game import GameState
import json
import os


# Modern color palette
COLOR_BG = "#FCF9EA"
COLOR_BG_SECONDARY = "#F8F9FA"
COLOR_PRIMARY = "#BADFDB"
COLOR_SUCCESS = "#B4DEB8"
COLOR_WARNING = "#F6E58D"
COLOR_DANGER = "#F7E3E3"
COLOR_TEXT = "#234C6A"
COLOR_TEXT_LIGHT = "#7F8C8D"
COLOR_BORDER = "#E0E0E0"
COLOR_CARD = "#FFFFFF"


class ConnectDialog(QDialog):
    """Dialog for connecting to server."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Server")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BG};
            }}
            QLabel {{
                color: {COLOR_TEXT};
                font-size: 11pt;
                font-weight: 500;
            }}
            QLineEdit, QSpinBox {{
                background-color: {COLOR_BG_SECONDARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 10px;
                font-size: 11pt;
                color: {COLOR_TEXT};
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #3A7BC8;
            }}
        """)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.host_input = QLineEdit("localhost")
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(5555)
        
        layout.addRow("Server Host:", self.host_input)
        layout.addRow("Port:", self.port_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_connection_info(self):
        """Get host and port from dialog."""
        return self.host_input.text(), self.port_input.value()


class HomePageWidget(QWidget):
    """Home page with navigation options."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        header.setStyleSheet(f"""
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
             stop:0 #F5AFAF, 
             stop:0.5 #F9DFDF, 
             stop:1 #FBEFEF,  
             border-radius: 100px
             );
""")

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(40, 50, 40, 50)
        
        title = QLabel("Tic-Tac-Toe Bar Ilan")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 38pt;
            font-weight: 700;
            color: white;
            padding: 10px;
            background: transparent;
        """)
        header_layout.addWidget(title)
    
        
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Menu Cards Container
        cards_container = QWidget()
        cards_container.setStyleSheet(f"background-color: {COLOR_BG_SECONDARY};")
        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setContentsMargins(60, 60, 60, 60)
        
        # Menu Grid
        grid = QGridLayout()
        grid.setSpacing(30)
        
        # Card 1: Create Game
        self.create_card = self._create_menu_card(
            "Create Game",
            "Start a new game and invite friends",
            COLOR_PRIMARY
        )
        grid.addWidget(self.create_card, 0, 0)
        
        # Card 2: Join Game
        self.join_card = self._create_menu_card(
            "Join Game",
            "Join an existing game room",
            COLOR_SUCCESS
        )
        grid.addWidget(self.join_card, 0, 1)
        
        # Card 3: Personal Info
        self.profile_card = self._create_menu_card(
            "Personal Info",
            "Update your name and email",
            COLOR_WARNING
        )
        grid.addWidget(self.profile_card, 1, 0)
        
        # Card 4: Exit
        self.exit_card = self._create_menu_card(
            " Exit",
            "Close the application",
            COLOR_DANGER
        )
        grid.addWidget(self.exit_card, 1, 1)
        
        cards_layout.addLayout(grid)
        cards_layout.addStretch()
        
        cards_container.setLayout(cards_layout)
        layout.addWidget(cards_container, 1)
        
        self.setLayout(layout)
    
    def _create_menu_card(self, title: str, description: str, color: str) -> QPushButton:
        """Create a menu card button."""
        card = QPushButton()
        card.setMinimumSize(250, 130)
        card.setCursor(Qt.PointingHandCursor)
        
        # Create layout for card content
        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 18pt;
            font-weight: 700;
            color: {color};
        """)
        
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            font-size: 10pt;
            color: {COLOR_TEXT_LIGHT};
        """)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        container = QWidget()
        container.setLayout(card_layout)
        
        card_main_layout = QVBoxLayout()
        card_main_layout.addWidget(container)
        card.setLayout(card_main_layout)
        
        card.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 3px solid {COLOR_BORDER};
                border-radius: 16px;
                padding: 20px;
            }}
            QPushButton:hover {{
                background-color: {color};
                border: 3px solid {color};
            }}
            QPushButton:hover QLabel {{
                color: white !important;
            }}
            QPushButton:pressed {{
                background-color: {color};
                
            }}
        """)
        
        return card


class CreateGameWidget(QWidget):
    """Create game screen."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Back button
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Home")
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_SECONDARY};
            }}
        """)
        back_layout.addWidget(self.back_btn)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        # Title
        title = QLabel("Create New Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 22pt;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            padding: 10px;
        """)
        layout.addWidget(title)
        
        # Card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLOR_BORDER};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(25)
        
        # Number of players
        players_layout = QHBoxLayout()
        players_label = QLabel("Number of Players:")
        players_label.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 10pt; font-weight: 500;")
        players_layout.addWidget(players_label)
        
        self.num_players_spin = QSpinBox()
        self.num_players_spin.setRange(2, 10)
        self.num_players_spin.setValue(2)
        self.num_players_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLOR_BG_SECONDARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 10px;
                font-size: 12pt;
                font-weight: 500;
                min-width: 100px;
                color: {COLOR_PRIMARY};
            }}
        """)
        players_layout.addWidget(self.num_players_spin)
        players_layout.addStretch()
        card_layout.addLayout(players_layout)
        
        # Info text
        info = QLabel("Choose how many players can join this game.\n After creating, you can join the game from the tab 'Join Game'.\n Share the Game ID with your friends to invite them!")
        info.setStyleSheet(f"color: {COLOR_TEXT_LIGHT}; font-size: 11pt;")
        info.setWordWrap(True)
        card_layout.addWidget(info)
        
        # Create button
        self.create_btn = QPushButton(" Create Game")
        self.create_btn.setMinimumHeight(50)
        self.create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px;
                font-size: 14pt;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: #3A7BC8;
            }}
            QPushButton:pressed {{
                background-color: #2A6AB8;
            }}
        """)
        card_layout.addWidget(self.create_btn)
        
        card.setLayout(card_layout)
        layout.addWidget(card)
        layout.addStretch()
        
        self.setLayout(layout)


class JoinGameWidget(QWidget):
    """Join game screen."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Back button
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Home")
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_SECONDARY};
            }}
        """)
        back_layout.addWidget(self.back_btn)
        back_layout.addStretch()
        
        self.refresh_btn = QPushButton(" Refresh")
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #40B868;
            }}
        """)
        back_layout.addWidget(self.refresh_btn)
        layout.addLayout(back_layout)
        
        # Title
        title = QLabel("Join Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 24pt;
            font-weight: 600;
            color: {COLOR_SUCCESS};
            padding: 10px;
        """)
        layout.addWidget(title)
        
        # Games list
        self.games_list = QListWidget()
        self.games_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLOR_BG_SECONDARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 12px;
                padding: 15px;
                font-size: 10pt;
            }}
            QListWidget::item {{
                background-color: white;
                border: 2px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 10px;
                margin: 8px;
                color: {COLOR_TEXT};
            }}
            QListWidget::item:selected {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: 2px solid {COLOR_SUCCESS};
            }}
            QListWidget::item:hover {{
                background-color: #E8F8EF;
            }}
        """)
        self.games_list.setMinimumHeight(100)
        layout.addWidget(self.games_list)
        
        # Join button
        self.join_btn = QPushButton("Join Selected Game")
        self.join_btn.setEnabled(False)
        self.join_btn.setMinimumHeight(50)
        self.join_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px;
                font-size: 16pt;
                font-weight: 700;
            }}
            QPushButton:hover:enabled {{
                background-color: #40B868;
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BG_SECONDARY};
                color: {COLOR_TEXT_LIGHT};
            }}
        """)
        layout.addWidget(self.join_btn)
        
        self.setLayout(layout)
        
        # Connect signals
        self.games_list.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """Handle game selection change."""
        self.join_btn.setEnabled(len(self.games_list.selectedItems()) > 0)


class ProfileWidget(QWidget):
    """Personal info screen."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Back button
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Home")
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_SECONDARY};
            }}
        """)
        back_layout.addWidget(self.back_btn)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        # Title
        title = QLabel("Personal Information")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 28pt;
            font-weight: 700;
            color: {COLOR_WARNING};
            padding: 20px;
        """)
        layout.addWidget(title)
        
        # Card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLOR_BORDER};
                border-radius: 16px;
                padding: 40px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        
        # Name
        name_label = QLabel("Your Name:")
        name_label.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12pt; font-weight: 500;")
        card_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name...")
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_BG_SECONDARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 12pt;
                color: {COLOR_TEXT};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_WARNING};
            }}
        """)
        card_layout.addWidget(self.name_input)
        
        # Email
        email_label = QLabel("Email Address:")
        email_label.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12pt; font-weight: 500;")
        card_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email...")
        self.email_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_BG_SECONDARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 12pt;
                color: {COLOR_TEXT};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_WARNING};
            }}
        """)
        card_layout.addWidget(self.email_input)
        
        # Save button
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WARNING};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px;
                font-size: 16pt;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: #E89616;
            }}
            QPushButton:pressed {{
                background-color: #D88606;
            }}
        """)
        card_layout.addWidget(self.save_btn)
        
        card.setLayout(card_layout)
        layout.addWidget(card)
        layout.addStretch()
        
        self.setLayout(layout)


class GamePlayWidget(QWidget):
    """Widget for playing the game."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_widget: Optional[BoardWidget] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Top bar
        top_layout = QHBoxLayout()
        
        self.game_id_label = QLabel("Game")
        self.game_id_label.setStyleSheet(f"""
            font-size: 13pt;
            color: {COLOR_TEXT};
            font-weight: 600;
        """)
        top_layout.addWidget(self.game_id_label)
        top_layout.addStretch()
        
        self.quit_btn = QPushButton("← Leave Game")
        self.quit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_SECONDARY};
                color: {COLOR_TEXT};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 10pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_DANGER};
                color: white;
                border: 2px solid {COLOR_DANGER};
            }}
        """)
        top_layout.addWidget(self.quit_btn)
        
        layout.addLayout(top_layout)
        
        # Status label
        self.status_label = QLabel("Waiting for players...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"""
            background-color: {COLOR_BG_SECONDARY};
            color: {COLOR_TEXT};
            font-size: 15pt;
            font-weight: 600;
            padding: 18px;
            border-radius: 12px;
            border: 2px solid {COLOR_BORDER};
        """)
        layout.addWidget(self.status_label)
        
        # Players info
        self.players_label = QLabel("Players:")
        self.players_label.setAlignment(Qt.AlignCenter)
        self.players_label.setStyleSheet(f"""
            font-size: 11pt;
            color: {COLOR_TEXT_LIGHT};
            font-weight: 500;
            padding: 10px;
            background-color: {COLOR_BG};
            border-radius: 8px;
        """)
        layout.addWidget(self.players_label)
        
        # Board container
        self.board_container = QWidget()
        self.board_layout = QVBoxLayout()
        self.board_layout.setAlignment(Qt.AlignCenter)
        self.board_container.setLayout(self.board_layout)
        layout.addWidget(self.board_container, 1)
        
        self.setLayout(layout)
    
    def set_board_size(self, size: int):
        """Create board with specified size."""
        if self.board_widget:
            self.board_layout.removeWidget(self.board_widget)
            self.board_widget.deleteLater()
        
        self.board_widget = BoardWidget(size)
        self.board_layout.addWidget(self.board_widget)


class MainWindow(QMainWindow):
    """Main application window."""
    
    PROFILE_FILE = "user_profile.json"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-Tac-Toe")
        #logo
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'Logo.png')))
        self.setMinimumSize(800, 600)
        
        # Apply main window styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BG_SECONDARY};
            }}
        """)
        
        # Load user profile
        self.user_profile = self._load_profile()
        
        # Network client (disable logging)
        import logging
        logging.basicConfig(level=logging.CRITICAL)
        
        self.client = NetworkClient()
        self.client.message_received.connect(self._on_message_received)
        self.client.connection_lost.connect(self._on_connection_lost)
        self.client.connected.connect(self._on_connected)
        
        # Game state
        self.current_game_id: Optional[str] = None
        self.my_player_id: Optional[str] = None
        self.my_symbol: Optional[str] = None
        self.game_state: Optional[Dict] = None
        
        self._init_ui()
        self._show_connect_dialog()
    
    def _load_profile(self) -> Dict:
        """Load user profile from file."""
        try:
            if os.path.exists(self.PROFILE_FILE):
                with open(self.PROFILE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'name': 'Player', 'email': ''}
    
    def _save_profile(self):
        """Save user profile to file."""
        try:
            with open(self.PROFILE_FILE, 'w') as f:
                json.dump(self.user_profile, f)
        except Exception as e:
            print(f"Error saving profile: {e}")
    
    def _init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(layout)
        
        # Connection status
        self.connection_label = QLabel("● Not Connected")
        self.connection_label.setAlignment(Qt.AlignCenter)
        self.connection_label.setStyleSheet(f"""
            background-color: {COLOR_DANGER};
            color: white;
            font-weight: 600;
            font-size: 10pt;
            padding: 8px;
        """)
        layout.addWidget(self.connection_label)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Home page
        self.home_widget = HomePageWidget()
        self.home_widget.create_card.clicked.connect(self._show_create_game)
        self.home_widget.join_card.clicked.connect(self._show_join_game)
        self.home_widget.profile_card.clicked.connect(self._show_profile)
        self.home_widget.exit_card.clicked.connect(self.close)
        self.stacked_widget.addWidget(self.home_widget)
        
        # Create game view
        self.create_widget = CreateGameWidget()
        self.create_widget.back_btn.clicked.connect(self._show_home)
        self.create_widget.create_btn.clicked.connect(self._on_create_game)
        self.stacked_widget.addWidget(self.create_widget)
        
        # Join game view
        self.join_widget = JoinGameWidget()
        self.join_widget.back_btn.clicked.connect(self._show_home)
        self.join_widget.refresh_btn.clicked.connect(self._on_refresh_games)
        self.join_widget.join_btn.clicked.connect(self._on_join_game)
        self.stacked_widget.addWidget(self.join_widget)
        
        # Profile view
        self.profile_widget = ProfileWidget()
        self.profile_widget.back_btn.clicked.connect(self._show_home)
        self.profile_widget.save_btn.clicked.connect(self._on_save_profile)
        self.profile_widget.name_input.setText(self.user_profile['name'])
        self.profile_widget.email_input.setText(self.user_profile['email'])
        self.stacked_widget.addWidget(self.profile_widget)
        
        # Gameplay view
        self.gameplay_widget = GamePlayWidget()
        self.gameplay_widget.quit_btn.clicked.connect(self._on_quit_game)
        self.stacked_widget.addWidget(self.gameplay_widget)
        
        layout.addWidget(self.stacked_widget)
        
        # Show home page
        self.stacked_widget.setCurrentWidget(self.home_widget)
    
    def _show_home(self):
        """Show home page."""
        self.stacked_widget.setCurrentWidget(self.home_widget)
    
    def _show_create_game(self):
        """Show create game screen."""
        self.stacked_widget.setCurrentWidget(self.create_widget)
    
    def _show_join_game(self):
        """Show join game screen."""
        self.stacked_widget.setCurrentWidget(self.join_widget)
        self._on_refresh_games()
    
    def _show_profile(self):
        """Show profile screen."""
        self.stacked_widget.setCurrentWidget(self.profile_widget)
    
    def _show_connect_dialog(self):
        """Show connection dialog."""
        dialog = ConnectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            host, port = dialog.get_connection_info()
            self._connect_to_server(host, port)
        else:
            self.close()
    
    def _connect_to_server(self, host: str, port: int):
        """Connect to the server."""
        success, error = self.client.connect(host, port)
        if not success:
            QMessageBox.critical(self, "Connection Error", error)
            self._show_connect_dialog()
    
    @pyqtSlot()
    def _on_connected(self):
        """Handle successful connection."""
        self.connection_label.setText(f"● Connected to Server")
        self.connection_label.setStyleSheet(f"""
            background-color: {COLOR_SUCCESS};
            color: white;
            font-weight: 600;
            font-size: 10pt;
            padding: 8px;
        """)
    
    @pyqtSlot()
    def _on_connection_lost(self):
        """Handle connection loss."""
        self.connection_label.setText("● Connection Lost")
        self.connection_label.setStyleSheet(f"""
            background-color: {COLOR_DANGER};
            color: white;
            font-weight: 600;
            font-size: 10pt;
            padding: 8px;
        """)
        QMessageBox.warning(self, "Connection Lost", "Connection to server was lost")
        self._show_home()
    
    @pyqtSlot(str, dict)
    def _on_message_received(self, msg_type: str, data: Dict):
        """Handle received message from server."""
        if msg_type == MessageType.GAME_CREATED.value:
            self._handle_game_created(data)
        elif msg_type == MessageType.GAME_JOINED.value:
            self._handle_game_joined(data)
        elif msg_type == MessageType.GAME_LIST.value:
            self._handle_game_list(data)
        elif msg_type == MessageType.GAME_STATE.value:
            self._handle_game_state(data)
        elif msg_type == MessageType.GAME_OVER.value:
            self._handle_game_over(data)
        elif msg_type == MessageType.ERROR.value:
            self._handle_error(data)
    
    def _handle_game_created(self, data: Dict):
        """Handle GAME_CREATED message."""
        game_id = data.get('game_id')
        QMessageBox.information(self, " Game Created", 
                               f"Game created successfully!\nGame ID: {game_id}")
    
    def _handle_game_joined(self, data: Dict):
        """Handle GAME_JOINED message."""
        self.current_game_id = data.get('game_id')
        self.my_player_id = data.get('player_id')
        self.my_symbol = data.get('symbol')
        
        self.stacked_widget.setCurrentWidget(self.gameplay_widget)
        self.gameplay_widget.game_id_label.setText(f" Game: {self.current_game_id}")
    
    def _handle_game_list(self, data: Dict):
        """Handle GAME_LIST message."""
        games = data.get('games', [])
        self.join_widget.games_list.clear()
        
        if not games:
            item = QListWidgetItem("No games available. Create one!")
            item.setFlags(Qt.NoItemFlags)
            self.join_widget.games_list.addItem(item)
            return
        
        for game in games:
            game_id = game.get('game_id')
            num_players = game.get('num_players')
            current_count = game.get('current_player_count')
            
            item_text = f" {game_id}  •  {current_count}/{num_players} players"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, game_id)
            self.join_widget.games_list.addItem(item)
    
    def _handle_game_state(self, data: Dict):
        """Handle GAME_STATE message."""
        self.game_state = data
        
        board_data = data.get('board', {})
        board_size = board_data.get('size', 3)
        
        if not self.gameplay_widget.board_widget or \
           self.gameplay_widget.board_widget.size != board_size:
            self.gameplay_widget.set_board_size(board_size)
            self.gameplay_widget.board_widget.cell_clicked.connect(self._on_cell_clicked)
        
        grid = board_data.get('grid', [])
        self.gameplay_widget.board_widget.set_board_state(grid)
        
        players = data.get('players', [])
        players_text = "  •  ".join([
            f"{p['symbol']} {p['name']}" + (" (left)" if not p['is_active'] else "")
            for p in players
        ])
        self.gameplay_widget.players_label.setText(players_text)
        
        state = data.get('state')
        if state == GameState.WAITING.value:
            self.gameplay_widget.status_label.setText(" Waiting for players to join...")
            self.gameplay_widget.status_label.setStyleSheet(f"""
                background-color: {COLOR_WARNING};
                color: white;
                font-size: 15pt;
                font-weight: 600;
                padding: 18px;
                border-radius: 12px;
                border: 2px solid {COLOR_WARNING};
            """)
            self.gameplay_widget.board_widget.set_enabled(False)
        
        elif state == GameState.PLAYING.value:
            current_player_id = data.get('current_player_id')
            current_player = next((p for p in players if p['player_id'] == current_player_id), None)
            
            if current_player:
                if current_player_id == self.my_player_id:
                    self.gameplay_widget.status_label.setText(f" Your Turn! ({self.my_symbol})")
                    self.gameplay_widget.status_label.setStyleSheet(f"""
                        background-color: {COLOR_SUCCESS};
                        color: white;
                        font-size: 16pt;
                        font-weight: 700;
                        padding: 18px;
                        border-radius: 12px;
                        border: 3px solid {COLOR_SUCCESS};
                    """)
                    self.gameplay_widget.board_widget.set_enabled(True)
                else:
                    self.gameplay_widget.status_label.setText(
                        f"Waiting for {current_player['name']} ({current_player['symbol']})"
                    )
                    self.gameplay_widget.status_label.setStyleSheet(f"""
                        background-color: {COLOR_BG_SECONDARY};
                        color: {COLOR_TEXT};
                        font-size: 15pt;
                        font-weight: 600;
                        padding: 18px;
                        border-radius: 12px;
                        border: 2px solid {COLOR_PRIMARY};
                    """)
                    self.gameplay_widget.board_widget.set_enabled(False)
    
    def _handle_game_over(self, data: Dict):
        """Handle GAME_OVER message and automatically exit."""
        self.gameplay_widget.board_widget.set_enabled(False)
        
        abandoned = data.get('abandoned', False)
        is_draw = data.get('is_draw', False)
        
        if abandoned:
            reason = data.get('reason', 'Game abandoned')
            self.gameplay_widget.status_label.setText(" Game Ended")
            self.gameplay_widget.status_label.setStyleSheet(f"""
                background-color: {COLOR_WARNING};
                color: white;
                font-size: 16pt;
                font-weight: 700;
                padding: 18px;
                border-radius: 12px;
                border: 3px solid {COLOR_WARNING};
            """)
            QMessageBox.information(self, "Game Ended", f"{reason}")
        elif is_draw:
            self.gameplay_widget.status_label.setText(" It's a Draw!")
            self.gameplay_widget.status_label.setStyleSheet(f"""
                background-color: {COLOR_WARNING};
                color: white;
                font-size: 16pt;
                font-weight: 700;
                padding: 18px;
                border-radius: 12px;
                border: 3px solid {COLOR_WARNING};
            """)
            QMessageBox.information(self, "Game Over", "The game ended in a draw! ")
        else:
            winner = data.get('winner', {})
            winner_name = winner.get('name', 'Unknown')
            winner_symbol = winner.get('symbol', '?')
            
            if winner.get('player_id') == self.my_player_id:
                self.gameplay_widget.status_label.setText("🏆 You Won!")
                self.gameplay_widget.status_label.setStyleSheet(f"""
                    background-color: {COLOR_SUCCESS};
                    color: white;
                    font-size: 18pt;
                    font-weight: 700;
                    padding: 18px;
                    border-radius: 12px;
                    border: 4px solid {COLOR_SUCCESS};
                """)
                QMessageBox.information(self, "🏆 Victory!", f"Congratulations! You won! ")
            else:
                self.gameplay_widget.status_label.setText(f"{winner_name} Won!")
                self.gameplay_widget.status_label.setStyleSheet(f"""
                    background-color: {COLOR_DANGER};
                    color: white;
                    font-size: 16pt;
                    font-weight: 700;
                    padding: 18px;
                    border-radius: 12px;
                    border: 3px solid {COLOR_DANGER};
                """)
                QMessageBox.information(self, "Game Over", f"{winner_name} ({winner_symbol}) won the game!")
        
        QTimer.singleShot(2000, self._auto_return_to_home)
    
    def _auto_return_to_home(self):
        """Automatically return to home after game over."""
        if self.current_game_id:
            self.client.quit_game()
        
        self.current_game_id = None
        self.my_player_id = None
        self.my_symbol = None
        
        self._show_home()
    
    def _handle_error(self, data: Dict):
        """Handle ERROR message."""
        error_msg = data.get('message', 'Unknown error')
        QMessageBox.warning(self, "Error", error_msg)
    
    @pyqtSlot()
    def _on_create_game(self):
        """Handle create game button click."""
        num_players = self.create_widget.num_players_spin.value()
        self.client.create_game(num_players)
    
    @pyqtSlot()
    def _on_join_game(self):
        """Handle join game button click."""
        selected_items = self.join_widget.games_list.selectedItems()
        if not selected_items:
            return
        
        game_id = selected_items[0].data(Qt.UserRole)
        if not game_id:
            return
            
        player_name = self.user_profile.get('name', 'Player')
        self.client.join_game(game_id, player_name)
    
    @pyqtSlot()
    def _on_refresh_games(self):
        """Handle refresh games button click."""
        self.client.list_games()
    
    @pyqtSlot()
    def _on_save_profile(self):
        """Handle save profile button click."""
        self.user_profile['name'] = self.profile_widget.name_input.text() or 'Player'
        self.user_profile['email'] = self.profile_widget.email_input.text()
        self._save_profile()
        QMessageBox.information(self, " Saved", "Your profile has been saved!")
    
    @pyqtSlot()
    def _on_quit_game(self):
        """Handle quit game button click."""
        reply = QMessageBox.question(self, "Leave Game", 
                                    "Are you sure you want to leave this game?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.client.quit_game()
            self.current_game_id = None
            self.my_player_id = None
            self.my_symbol = None
            self._show_home()
    
    @pyqtSlot(int, int)
    def _on_cell_clicked(self, row: int, col: int):
        """Handle board cell click."""
        if self.current_game_id:
            self.client.make_move(row, col)
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.client.is_connected():
            self.client.disconnect()
        event.accept()