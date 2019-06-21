import random
import math
import functools 
import sys

def combine(g,f):
    def c(*args):
        return f(*g(*args))
    return c

def L(rule='F+[[X]-X]-F[-FX]+X',angle=0.4,pieces=2,depth=0):
    return {
        'X': lambda x,y,a,s,l,svg,ops: combine(functools.reduce(combine, map(lambda c: L(rule,angle,pieces,depth+1)[c], (rule if (l > random.randint(3,10) and depth < 16 and ops < 50000) else 'n'))), (lambda x,y,a,s,l,svg,ops: (x,y,a,s,l*pieces,svg,ops+1)))(x,y,a,s,l/pieces,svg,ops),
        'F': lambda x,y,a,s,l,svg,ops: (x + l*math.cos(a),y+l*math.sin(a),a,s,l,svg + '\n<line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:rgb(255,0,0);stroke-width:2" />'%(x,y,x + l*math.cos(a),y+l*math.sin(a)),ops+1),
        'n': lambda x,y,a,s,l,svg,ops: (x,y,a,s,l,svg,ops+1),
        '+': lambda x,y,a,s,l,svg,ops: (x,y,a+angle,s,l,svg,ops+1),
        '-': lambda x,y,a,s,l,svg,ops: (x,y,a-angle,s,l,svg,ops+1),
        '[': lambda x,y,a,s,l,svg,ops: (x,y,a,s + [(x,y,a,l)],l,svg,ops+1),
        ']': lambda x,y,a,s,l,svg,ops: (s[-1][0],s[-1][1],s[-1][2],s[:-1],s[-1][3],svg,ops+1),
        '^': lambda x,y,a,s,l,svg,ops: (x,y,a,s,l*pieces,svg,ops+1),
        'v': lambda x,y,a,s,l,svg,ops: (x,y,a,s,l/pieces,svg,ops+1),
        'B': lambda x,y,a,s,l,svg,ops: (x - l*math.cos(a),y-l*math.sin(a),a,s,l,svg + '\n<line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:rgb(255,0,0);stroke-width:2" />'%(x,y,x - l*math.cos(a),y-l*math.sin(a)),ops+1),
        'R': lambda x,y,a,s,l,svg,ops: (320,480,math.radians(270),s,l,svg,ops+1)
        }
        
def parse(s):
    rule = s
    pieces = 2
    aresult = math.radians(30)
    if "/" in s:
        items = s.split("/")
        try:
            aresult = math.radians(float(items[1]))
        except Exception:
            aresult = math.radians(30)
        if len(items) > 2:
            try:
                pieces = float(items[2])
            except Exception:
                pieces = 2
            #if pieces <= 1.1:
            #    pieces = 2
    result = ""
    open = 0
    for c in rule:
        if c in "XFBR^vn+-":
            result += c
        if c == "[":
            result += c 
            open += 1
        if c == "]" and open > 0:
            result += c
            open -= 1
    if not result:
        result = "F"
    return (result,aresult,pieces)

if __name__ == "__main__":
    rule = 'F+[[X]-X]-F[-FX]+X'
    angle = 0.4
    pieces=2
    if len(sys.argv) > 1:
        (rule,angle,pieces) = parse(sys.argv[1])
    print('<?xml version="1.0" encoding="UTF-8" ?>')
    print('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"   "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
    print('<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" height="480" width="640">') 
    print(L(rule, angle,pieces)['X'](320,480,math.radians(270),[],160,"",0))
    print('</svg>')