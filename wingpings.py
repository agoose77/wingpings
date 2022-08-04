import http.server
import urllib.parse
import uuid
import datetime
import argparse


messages = []


class ChatHandler(http.server.BaseHTTPRequestHandler):
    def view(self):
        data = [{**f, "received": t} for f, t in messages]
        return "\n".join(
            [
                "HTTP/1.1 200 OK",
                "Content-type: text/html",
                "",
                "<style>.message > * {padding: 1em;} </style>",
                "<div>",
                *[
                    '<div class="message"><span class="received">{received}</span><span class="name">{name}</span><span class="message">{message}</span></div>'.format_map(
                        m
                    )
                    for m in data
                ],
                "</div>",
                '<form method="POST" action=""><input name="name" type="text"><input name="message" type=text><input type=submit></form>',
            ]
        )

    def parse_form(self, content):
        raw_items = [l.split("=", 1) for l in content.split("&")]
        items = [
            (urllib.parse.unquote_plus(k), urllib.parse.unquote_plus(v))
            for (k, v) in raw_items
        ]
        return dict(items)

    def do_GET(self):
        self.wfile.write(self.view().encode())

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"])).decode()
        form = self.parse_form(data)
        print(form)
        if not messages or form != messages[-1][0]:
            messages.append((form, datetime.datetime.now().time()))
        self.wfile.write(self.view().encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", default="0.0.0.0")
    parser.add_argument("port", default=8000, type=int)
    args = parser.parse_args()

    server = http.server.HTTPServer((args.host, args.port), ChatHandler)
    print(f"Serving on http://{args.host}:{args.port}")
    server.serve_forever()
