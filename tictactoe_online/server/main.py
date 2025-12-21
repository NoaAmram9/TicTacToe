#!/usr/bin/env python3
"""
Server main entry point.
"""

import sys
import signal
from .server import Server


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nShutting down server...")
    sys.exit(0)


def main():
    """Main function to run the server."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get port from command line or use default
    port = 5555
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Create and start server
    server = Server(host='0.0.0.0', port=port)
    
    if not server.start():
        print("Failed to start server")
        sys.exit(1)
    
    print(f"Tic-Tac-Toe Server running on port {port}")
    print("Press Ctrl+C to stop")
    
    # Keep main thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == '__main__':
    main()