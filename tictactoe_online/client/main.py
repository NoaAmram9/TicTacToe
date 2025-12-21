#!/usr/bin/env python3
"""
Client main entry point.
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from .main_window import MainWindow


def main():
    """Main function to run the client application."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Tic-Tac-Toe Online")
    app.setOrganizationName("TicTacToe")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()