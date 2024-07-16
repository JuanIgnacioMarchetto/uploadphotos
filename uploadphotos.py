import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import cgi

UPLOAD_FOLDER = 'uploads'
PORT = 8080

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def _send_response(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
    
    def do_GET(self):
        if self.path == '/':
            self.list_photos()
        elif self.path.startswith('/uploads/'):
            self.serve_file()
        else:
            self.send_error(404, "File Not Found")
    
    def list_photos(self):
        photos = os.listdir(UPLOAD_FOLDER)
        photo_list_html = '\n'.join([f'<li><a href="/uploads/{photo}">{photo}</a></li>' for photo in photos])
        html = f'''
            <html>
                <body>
                    <h1>Subida de Fotos</h1>
                    <form action="/" method="post" enctype="multipart/form-data">
                        <input type="file" name="file">
                        <input type="submit" value="Subir">
                    </form>
                    <h2>Fotos Subidas</h2>
                    <ul>
                        {photo_list_html}
                    </ul>
                </body>
            </html>
        '''
        self._send_response(html)
    
    def serve_file(self):
        file_path = self.path.lstrip('/')
        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, "File Not Found")
    
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            file_data = fields.get('file')[0]
            filename = os.path.join(UPLOAD_FOLDER, fields['file'][0].filename)
            with open(filename, 'wb') as file:
                file.write(file_data)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(400, "Bad Request")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Server running on port {PORT}")
    httpd.serve_forever()
