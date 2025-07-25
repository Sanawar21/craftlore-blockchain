#!/usr/bin/env python3

import time
import subprocess
import sys
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            print("🔄 Restarting transaction processor...")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        
        print(f"🚀 Starting: {' '.join(self.command)}")
        self.process = subprocess.Popen(self.command)

    def on_modified(self, event):
        if event.src_path.endswith('.py') and not event.src_path.endswith('watch.py'):
            print(f"📝 File changed: {event.src_path}")
            self.restart()

    def cleanup(self):
        if self.process:
            print("🛑 Stopping transaction processor...")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

def signal_handler(sig, frame):
    print("\n👋 Received shutdown signal")
    global event_handler
    if event_handler:
        event_handler.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 watch.py <command> [args...]")
        sys.exit(1)
    
    command = sys.argv[1:]
    event_handler = RestartHandler(command)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    print("👀 Watching for file changes...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down watcher...")
    finally:
        observer.stop()
        event_handler.cleanup()
        observer.join()
