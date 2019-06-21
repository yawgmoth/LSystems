import http.server
import socketserver
import threading
import time
import shutil
import os
import random
import hashlib
import sys
import traceback
import threading
import lsystems
import math
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from serverconf import HOST_NAME, PORT_NUMBER



debug = True

errlog = sys.stdout
if not debug:
    errlog = file("lsystems.log", "w")

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def respond(s, str):
        s.wfile.write(str.encode("utf8"))
    def do_GET(s):
        s.process_request()
        
    def add_example(s, rule, angle, pieces, desc=""):
        s.respond('<li><a href="/%s/%.2f/%.2f">%s, angle: %.2f, pieces: %.2f</a>: %s'%(rule, angle, pieces, rule, angle, pieces, desc))
    
    def process_request(s, rule="", angle="", pieces=""):
        s.send_response(200)
        path = s.path.strip("/")
        if not path:
            path = "F+[[X]-X]-F[-FX]+X"
        
        s.end_headers()
        s.wfile.write("<html><head><title>L-Systems</title></head><body><h1>L-Systems</h1>".encode("utf8"))
        if rule:
            path = rule + "/" + angle + "/" + pieces
        (rule,angle,pieces) = lsystems.parse(path)
            
        s.respond('<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" height="480" width="640">') 
        s.respond(lsystems.L(rule, angle,pieces)['X'](320,480,math.radians(270),[],160,"",0)[5])
        s.respond('</svg>')
        s.respond('<form action="/" method="POST">')
        s.respond("<table>")
        s.respond('<tr><td>Rule:</td><td> <input name="rule" value="%s"/></td></td>'%rule)
        s.respond('<tr><td>Angle:</td><td> <input name="angle" value="%.2f"/></td></td>'%math.degrees(angle))
        s.respond('<tr><td>Pieces:</td><td> <input name="pieces" value="%.2f"/></td></td>'%pieces)
        s.respond('</table>')
        s.respond('<input type="submit" value="Generate"/><br/>')
        s.respond('</form>')
        s.respond("""This is a pretty minimalistic implementation of <a href="https://en.wikipedia.org/wiki/L-system">L-Systems</a>, which allows for only one rule, and automatically reduces the line length 
        (by dividing it by the value of "pieces") in each recursive invocation. Once the length is below a certain (semi-random) threshold (or a maximum recursion depth has been reached, whichever happens first), 
        no more recursive invocations will be done. Source code available <a href="https://github.com/yawgmoth/LSystems">here</a>. <hr/>Available symbols:
""")
        s.respond('<table>')
        s.respond('<tr><td>X</td><td>The name of the rule, for recursive invocation.</td></tr>')
        s.respond('<tr><td>F</td><td>Move forward.</td></tr>')
        s.respond('<tr><td>B</td><td>Move backward.</td></tr>')
        s.respond('<tr><td>R</td><td>Reset to starting location.</td></tr>')
        s.respond('<tr><td>+</td><td>Turn right.</td></tr>')
        s.respond('<tr><td>-</td><td>Turn left.</td></tr>')
        s.respond('<tr><td>[</td><td>Store position, rotation and line length.</td></tr>')
        s.respond('<tr><td>]</td><td>Restore position, rotation and line length.</td></tr>')
        s.respond('<tr><td>^</td><td>Increase line length.</td></tr>')
        s.respond('<tr><td>v</td><td>Decrease line length.</td></tr>')
        s.respond('</table>')
        s.respond("<hr/>Some examples: <br/>")
        s.respond("<ul>")
        s.add_example('F+[[X]-X]-F[-FX]+X', 30, 2, "The classic fern")
        s.add_example('F[+X][-X]', 45, 1.66, "A nice tree")
        s.add_example('F[+X][-X]vF', 90, 1.4, "An incomplete grid")
        s.add_example('FF[+X]', 120, 1.04, "A spiral")
        s.respond("</ul>")
        s.respond("Feel free to submit a pull request on github if you come up with other nice examples.")
        s.wfile.write("</body></html>".encode("utf8"))

    def do_POST(s):
        ctype, pdict = parse_header(s.headers['content-type'])
        postvars = {}
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(s.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(s.headers['content-length'])
            postvars = parse_qs(
                    s.rfile.read(length), keep_blank_values=1)
        s.process_request(postvars.get(b'rule', [b''])[0].decode("utf8"), postvars.get(b'angle', [b''])[0].decode("utf8"), postvars.get(b'pieces', [b''])[0].decode("utf8"))


 
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    def finish_request(self, request, client_address):
        request.settimeout(30)
        # "super" can not be used because BaseServer is not created from object
        http.server.HTTPServer.finish_request(self, request, client_address) 
 
if __name__ == '__main__':
    server_class = ThreadingHTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    errlog.write(time.asctime() + " Server Starts - %s:%s\n" % (HOST_NAME, PORT_NUMBER))
    errlog.flush()
    try:
       httpd.serve_forever()
    except KeyboardInterrupt:
       pass
    httpd.server_close()
    errlog.write(time.asctime() +  " Server Stops - %s:%s\n" % (HOST_NAME, PORT_NUMBER))
    errlog.flush()