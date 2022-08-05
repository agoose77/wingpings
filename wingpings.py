import http.server
import urllib.parse
import uuid
import datetime
import argparse


class ChatHandler(http.server.BaseHTTPRequestHandler):
    messages = []

    def write_response(self):
        messages = [
            """
<div class="message">
    <span class="received">{received}</span>
    <span class="name">{name}</span>
    <span class="message">{message}</span>
</div>
            """.format_map(
                {**f, "received": t}
            )
            for f, t in self.messages
        ]
        message_log = "\n".join(messages)
        contents = f"""
<html>
<head>
<style>
    .message > * {{
        padding: 1em;
    }} 
</style>
</head>
<body>
    <div>
        { message_log }
    </div>

    <form method="POST" action="">
        <input name="name" type="text">
        <input name="message" type="text">
        <input type="submit">
    </form>
</body>
        """
        response = "\n".join(
            ["HTTP/1.1 200 OK", "Content-type: text/html", "", contents]
        )
        self.wfile.write(response.encode())

    def parse_form(self, content):
        raw_items = [l.split("=", 1) for l in content.split("&")]
        items = [
            (urllib.parse.unquote_plus(k), urllib.parse.unquote_plus(v))
            for (k, v) in raw_items
        ]
        return dict(items)

    def handle_message(self, message):
        if not self.messages or message != self.messages[-1][0]:
            self.messages.append((message, datetime.datetime.now().time()))

    def do_GET(self):
        self.write_response()

    def do_POST(self):
        n_bytes = int(self.headers["Content-Length"])
        form_data = self.rfile.read(n_bytes).decode()
        form = self.parse_form(form_data)

        self.handle_message(form)
        self.write_response()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", default="0.0.0.0")
    parser.add_argument("port", default=8000, type=int)
    args = parser.parse_args()

    server = http.server.HTTPServer((args.host, args.port), ChatHandler)
    print(f"Serving on http://{args.host}:{args.port}")
    server.serve_forever()
