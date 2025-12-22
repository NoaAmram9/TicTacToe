"""
Board Widget - Qt5 widget for displaying and interacting with the game board.
Modern, clean, light design.
"""

from typing import Optional, Callable, List
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class BoardWidget(QWidget):
    """
    Widget for displaying the Tic-Tac-Toe board.
    
    Signals:
        cell_clicked: Emitted when a cell is clicked (row, col)
    """
    
    cell_clicked = pyqtSignal(int, int)
    
    # Modern light color palette
    COLOR_BG = "#FCF9EA"
    COLOR_PRIMARY = "#BADFDB"
    COLOR_SECONDARY = "#E8F4FD"
    COLOR_SUCCESS = "#B4DEB8"
    COLOR_CELL_BG = "#FFFFFF"
    COLOR_CELL_BORDER = "#E0E0E0"
    COLOR_TEXT = "#234C6A"
   
    
    def __init__(self, size: int = 3, parent=None):
        """
        Initialize the board widget.
        
        Args:
            size: Size of the board (size x size)
            parent: Parent widget
        """
        super().__init__(parent)
        self.size = size
        self.cells: List[List[QPushButton]] = []
        self.enabled = False
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Clean background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.COLOR_BG};
                border-radius: 20px;
            }}
        """)
        
        # Create grid of buttons
        for row in range(self.size):
            row_cells = []
            for col in range(self.size):
                cell = QPushButton()
                cell.setMinimumSize(100, 100)
                cell.setMaximumSize(140, 140)
                cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                
                # Beautiful modern styling
                cell.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.COLOR_CELL_BG};
                        border: 2px solid {self.COLOR_CELL_BORDER};
                        border-radius: 16px;
                        font-size: 36pt;
                        font-weight: 600;
                        color: {self.COLOR_PRIMARY};
                    }}
                    QPushButton:hover:enabled {{
                        background-color: {self.COLOR_SECONDARY};
                        border: 2px solid {self.COLOR_PRIMARY};
                    }}
                    QPushButton:pressed:enabled {{
                        background-color: {self.COLOR_PRIMARY};
                        color: white;
                    }}
                    QPushButton:disabled {{
                        background-color: {self.COLOR_CELL_BG};
                        color: {self.COLOR_TEXT};
                        border: 2px solid {self.COLOR_CELL_BORDER};
                    }}
                """)
                
                # Connect click handler
                cell.clicked.connect(lambda checked, r=row, c=col: self._on_cell_clicked(r, c))
                
                layout.addWidget(cell, row, col)
                row_cells.append(cell)
                cell.setEnabled(False)
            
            self.cells.append(row_cells)
    
    def _on_cell_clicked(self, row: int, col: int):
        """
        Handle cell click.
        
        Args:
            row: Row index
            col: Column index
        """
        if self.enabled and not self.cells[row][col].text():
            self.cell_clicked.emit(row, col)
    
    def set_cell(self, row: int, col: int, symbol: str):
        """
        Set the symbol in a cell.
        
        Args:
            row: Row index
            col: Column index
            symbol: Symbol to display
        """
        if 0 <= row < self.size and 0 <= col < self.size:
            self.cells[row][col].setText(symbol)
            self.cells[row][col].setEnabled(False)
    
    def clear_cell(self, row: int, col: int):
        """
        Clear a cell.
        
        Args:
            row: Row index
            col: Column index
        """
        if 0 <= row < self.size and 0 <= col < self.size:
            self.cells[row][col].setText("")
            if self.enabled:
                self.cells[row][col].setEnabled(True)
    
    def set_board_state(self, grid: List[List[Optional[str]]]):
        """
        Set the entire board state.
        
        Args:
            grid: 2D list of symbols
        """
        for row in range(self.size):
            for col in range(self.size):
                if row < len(grid) and col < len(grid[row]):
                    symbol = grid[row][col]
                    if symbol:
                        self.set_cell(row, col, symbol)
                    else:
                        self.clear_cell(row, col)
    
    def clear_board(self):
        """Clear all cells."""
        for row in range(self.size):
            for col in range(self.size):
                self.clear_cell(row, col)
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable the board for interaction.
        
        Args:
            enabled: Whether to enable the board
        """
        self.enabled = enabled
        for row in range(self.size):
            for col in range(self.size):
                # Only enable empty cells
                if not self.cells[row][col].text():
                    self.cells[row][col].setEnabled(enabled)
    
    def highlight_winning_cells(self, cells: List[tuple]):
        """
        Highlight winning cells.
        
        Args:
            cells: List of (row, col) tuples
        """
        for row, col in cells:
            if 0 <= row < self.size and 0 <= col < self.size:
                self.cells[row][col].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.COLOR_SUCCESS};
                        border: 3px solid {self.COLOR_SUCCESS};
                        border-radius: 16px;
                        font-size: 40pt;
                        font-weight: bold;
                        color: white;
                    }}
                """)
    
    def resize_board(self, new_size: int):
        """
        Resize the board to a new size.
        
        Args:
            new_size: New board size
        """
        # Clear existing cells
        for row in self.cells:
            for cell in row:
                cell.deleteLater()
        self.cells.clear()
        
        # Remove old layout
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        
        # Update size and recreate UI
        self.size = new_size
        self._init_ui()
