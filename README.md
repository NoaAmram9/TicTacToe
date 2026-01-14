# TicTacToe
Tic-Tac-Toe Game for Computer Networks and Internet 1
tictactoe_online/
├── common/              # Shared modules
│   ├── protocol.py      # Network protocol (JSON over TCP)
│   ├── player.py        # Player representation
│   ├── board.py         # Game board logic
│   └── game.py          # Game session management
├── server/              # Server components
│   ├── server.py        # Main multi-threaded server
│   ├── client_handler.py # Per-client connection handler
│   └── game_manager.py   # Multiple game coordinator
└── client/              # Client components
    ├── main_window.py   # Main GUI application
    ├── board_widget.py  # Interactive game board
    └── network_client.py # Server communication