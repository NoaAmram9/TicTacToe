# TicTacToe
Tic-Tac-Toe Game
=======
Tic-Tac-Toe Game for Computer Networks and Internet
# 🎮 Tic-Tac-Toe Online



[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Qt5](https://img.shields.io/badge/Qt5-5.15+-green.svg)](https://www.qt.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🎨 **Beautiful Modern UI** - Clean, light design with smooth interactions
- 👥 **2-10 Players** - Scale from classic 2-player to massive 10-player games
- 📐 **Dynamic Boards** - Board size automatically adjusts: (players + 1)²
- ⚡ **Real-Time Updates** - See moves instantly across all clients
- 🌐 **Network Play** - TCP socket-based reliable communication
- 🏆 **Auto-Exit** - Game automatically returns to lobby after completion

## 🎨 Design

Modern, clean, light design with:
- Soft color palette (#4A90E2, #50C878, #F8F9FA)
- Smooth hover effects
- Clear visual feedback
- Responsive layout
- Professional typography

## 📦 Installation

```bash
# Install dependencies
pip install PyQt5

# Or use requirements file
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Start the Server

```bash
cd server
python -m server.main
```

The server will start on port 5555 (default).

### 2. Launch Clients

```bash
cd client
python -m client.main
```


### 3. Play!

1. **Create a Game** - Click "Create Game" and choose player count
2. **Join a Game** - Select from available games and click "Join"
3. **Make Your Move** - Click empty cells when it's your turn
4. **Win!** - Get 3 symbols in a row (horizontal, vertical, or diagonal)

## 🎯 Game Rules

### Board Size
- 2 players → 3×3 board
- 3 players → 4×4 board
- 4 players → 5×5 board
- Formula: **(players + 1)² cells**

### Win Condition
Get **exactly as many symbols in a row as the number of players**:
- **2 players** → Need **2 in a row** to win
- **3 players** → Need **3 in a row** to win
- **4 players** → Need **4 in a row** to win
- **X players** → Need **X in a row** to win

Win directions: ➡️ Horizontal, ⬇️ Vertical, ↘️ Diagonal, ↙️ Anti-diagonal

### Player Symbols
Each player gets a unique symbol: **X, O, Δ, □, ◇, ★, ♠, ♣, ♥, ♦**

## 🏗️ Architecture

### Project Structure

```
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
<<<<<<< HEAD
    └── network_client.py # Server communication
=======
    └── network_client.py # Server communication
```

### Network Protocol

- **Transport**: TCP for reliability
- **Format**: JSON messages with newline delimiters
- **Pattern**: Request-response + server broadcasts

## 🛠️ Technical Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.8+** | Core language |
| **PyQt5** | Modern GUI framework |
| **TCP Sockets** | Network communication |
| **JSON** | Data serialization |
| **Threading** | Concurrent operations |

## 🎮 Features in Detail

### For Players
- ✅ Simple, intuitive interface
- ✅ Real-time game updates
- ✅ Clear turn indicators
- ✅ Winner celebration
- ✅ Auto-return to lobby after game

### For Developers
- ✅ Modular, clean code
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Thread-safe operations
- ✅ Error handling
- ✅ Easy to extend


### Multiple Games

The server supports multiple concurrent games:
- Each game is independent
- Players can create or join any available game
- No limit on number of simultaneous games


## 💡 Tips

- 🔄 **Refresh often** - Click "Refresh List" to see new games
- 👥 **Play with friends** - Share the game ID
- ⚡ **Fast responses** - The game updates in real-time
- 🎨 **Enjoy the design** - Modern, clean, and pleasant
- 
All rights reserved to Noa Amram and Sima Priluk





---

**Enjoy the game!** 🎉

Made with ❤️ for learning network programming
>>>>>>> 129b429d4253b21ec37a2b906fa17da5e649a897
