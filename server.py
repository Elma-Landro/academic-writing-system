"""
Simple HTTP server to serve the landing page and redirect to Streamlit app.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import subprocess
import time
import os

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
        elif self.path == '/streamlit':
            # Redirect to Streamlit app
            self.send_response(302)
            self.send_header('Location', 'http://localhost:5000')
            self.end_headers()
            return

        return SimpleHTTPRequestHandler.do_GET(self)

def start_streamlit():
    """Start Streamlit app in background."""
    time.sleep(2)  # Wait for main server to start
    subprocess.run(['streamlit', 'run', 'app.py', '--server.port', '5000', '--server.address', '0.0.0.0'])

def main():
    """Start both servers."""
    print("🚀 Starting Academic Writing System...")

    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()

    # Start main HTTP server
    server = HTTPServer(('0.0.0.0', 8080), CustomHandler)
    print("📝 Landing page: http://localhost:8080")
    print("🎯 Streamlit app: http://localhost:5000")
    print("✅ System ready!")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        server.shutdown()

if __name__ == "__main__":
    main()