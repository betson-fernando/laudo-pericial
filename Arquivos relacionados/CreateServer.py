from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "localhost"
serverPort = 8000


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):

        text = f"""
            <html><head><title>https://pythonbasics.org</title></head>
            <p>Request: {self.client_address}</p>

            <body>
            <p>This is an example web server. </p>
            </body></html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(text, "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped")
