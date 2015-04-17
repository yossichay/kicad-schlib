#!/usr/bin/python3

import cairo
import math
import shlex
from decimal import Decimal
import sys
import os
import copy

COLOR_FG = (0.51765, 0.0, 0.0)
COLOR_BG = (1.0, 1.0, 0.76078)
COLOR_PN = (0.0, 0.51765, 0.51765)
MIN_WIDTH = 5
TEXT_OFFS = 10
MILS_PER_PIXEL = 5

def draw_text(ctx, text, posx, posy, size, hjust, vjust, theta=0):
    ctx.save()

    ctx.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size*1.5)

    fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()
    (x, y, width, height, dx, dy) = ctx.text_extents(text)

    ctx.translate(posx, posy)
    ctx.rotate(theta)
    ctx.translate(-width/2, fheight/2)

    if hjust == "L":
        sx = -width/2
    elif hjust == "C":
        sx = 0
    elif hjust == "R":
        sx = width/2

    if vjust == "T":
        sy = -height/2
    elif vjust == "C":
        sy = 0
    elif vjust == "B":
        sy = height/2

    ctx.move_to(sx, sy - height/2)
    ctx.show_text(text)
    ctx.restore()

def bounding_box(items):
    boxes = [i.bounding_box() for i in items]
    minx = min(i[0] for i in boxes)
    maxx = max(i[1] for i in boxes)
    miny = min(i[2] for i in boxes)
    maxy = max(i[3] for i in boxes)

    return minx, maxx, miny, maxy

class SchSymbol(object):
    def __init__(self, stack=None):
        self.text_offset = 40
        self.draw_pinnums = True
        self.draw_pinnames = True
        self.n_units = 1
        self.units_locked = False
        self.flag = "N"
        self.fields = []
        self.fplist = []
        self.objects = []

        if stack is not None:
             self.parse_kicad(stack)

    @property
    def name(self):
        return self.fields[1].value

    @property
    def ref(self):
        return self.fields[0].value

    def parse_kicad(self, stack):
        """Parse a KiCad library file into this object.

        @param stack - a stack of lines, with the first line at the end
            (so we can pop() them)
        """

        states = ["root", "fplist", "draw"]
        state = "root"

        while stack:
            assert state in states
            raw_line = stack.pop()
            line = raw_line.strip()
            parts = shlex.split(line)

            if not line:
                continue
            if line.startswith("#"):
                continue

            if state == "root":
                if parts[0] == "EESchema-LIBRARY":
                    assert parts[1] == "Version"
                    assert Decimal(parts[2]) <= Decimal("2.3")

                elif parts[0] == "DEF":
                    head, name, ref, unused, text_offset, draw_pinnums, draw_pinnames, n_units, units_locked, flag = parts
                    self.text_offset = int(text_offset)
                    self.draw_pinnums = (draw_pinnums == "Y")
                    self.draw_pinnames = (draw_pinnames == "Y")
                    self.n_units = int(n_units)
                    self.units_locked = (units_locked == "L")
                    self.flag = flag

                elif parts[0].startswith("F"):
                    fieldnum = int(parts[0][1:])
                    assert fieldnum == len(self.fields)
                    stack.append(raw_line)
                    self.fields.append(Field(self, stack))

                elif parts[0] == "$FPLIST":
                    state = "fplist"

                elif parts[0] == "DRAW":
                    state = "draw"

                elif parts[0] == "ENDDEF":
                    return

                else:
                    print("Unrecognized line %s" % parts[0])

            elif state == "fplist":
                if parts[0] == "$ENDFPLIST":
                    state = "root"
                else:
                    self.fplist.append (line)

            elif state == "draw":
                if parts[0] == "X":
                    stack.append(raw_line)
                    self.objects.append(Pin(self, stack))
                elif parts[0] == "A":
                    stack.append(raw_line)
                    self.objects.append(Arc(self, stack))
                elif parts[0] == "C":
                    stack.append(raw_line)
                    self.objects.append(Circle(self, stack))
                elif parts[0] == "P":
                    stack.append(raw_line)
                    self.objects.append(Polyline(self, stack))
                elif parts[0] == "S":
                    stack.append(raw_line)
                    self.objects.append(Rectangle(self, stack))
                elif parts[0] == "T":
                    stack.append(raw_line)
                    self.objects.append(Text(self, stack))
                elif parts[0] == "ENDDRAW":
                    state = "root"
                else:
                    raise Exception("Unrecognized graphic item %s" % parts[0])

    def __str__(self):
        lines = []
        lines.append(self.name + " : " + self.ref + "?")
        lines.extend(str(i) for i in self.objects)
        return '\n'.join(lines)

    def render_cairo(self, ctx, origx, origy):
        for i in self.objects:
            i.render_cairo(ctx, origx, origy)

    def filter_unit(self, unit):
        self.objects = [i for i in self.objects if (i.unit == unit or i.unit == 0)]

    def sort_objects(self):
        """Sort the objects into a good drawing order"""

        def sortkey(x):
            if isinstance(x, Pin):
                return 4
            elif isinstance(x, Text):
                return 5
            elif hasattr(x, "fill") and x.fill == "F":
                return 2
            elif hasattr(x, "fill") and x.fill == "f":
                return 0
            else:
                return 1

        self.objects.sort(key=sortkey)

    def bounding_box(self):
        """Returns minx, maxx, miny, maxy"""

        boxes = [i.bounding_box() for i in self.objects]
        minx = min(i[0] for i in boxes)
        maxx = max(i[1] for i in boxes)
        miny = min(i[2] for i in boxes)
        maxy = max(i[3] for i in boxes)

        return minx, maxx, miny, maxy

class Field(object):
    def __init__(self, parent, stack=None):
        self.parent = parent
        self.value = ""
        self.posx = 0
        self.posy = 0
        self.size = 0
        self.orient = "H"
        self.visible = True
        self.hjust = "C"
        self.vjust = "C"
        self.fieldname = ""

        if stack is not None:
            self.parse_kicad(stack)

    def parse_kicad(self, stack):
        raw_line = stack.pop()
        line = raw_line.strip()
        parts = shlex.split(line)

        head, value, posx, posy, size, orient, visible, hjust, vjust, *rest = parts
        assert head.startswith("F")
        self.value = value
        self.posx = int(posx)
        self.posy = int(posy)
        self.size = int(size)
        self.orient = orient
        self.visible = (visible == "V")
        self.hjust = hjust
        self.vjust = vjust[0]  # CNN -> C
        assert vjust[1:] == "NN"
        if rest:
            self.fieldname = rest[0]
        else:
            self.fieldname = ""

    def __str__(self):
        return self.fieldname + ": " + self.value

    def render_cairo(self, ctx, origx, origy):
        pass

class Pin(object):
    def __init__(self, parent, stack=None):
        self.parent = parent
        self.name = ""
        self.num = ""
        self.posx = 0
        self.posy = 0
        self.length = 0
        self.dir = "L"
        self.name_size = 0
        self.num_size = 0
        self.elec_type = "U"
        self.pin_type = ""
        self.unit = 1
        self.convert = 1

        if stack is not None:
            self.parse_kicad(stack)

    def parse_kicad(self, stack):
        raw_line = stack.pop()
        line = raw_line.strip()
        parts = shlex.split(line)

        head, name, num, posx, posy, length, direction, num_size, name_size, unit, convert, elec_type, *rest = parts
        self.name = name
        self.num = num
        self.posx = int(posx)
        self.posy = int(posy)
        self.length = int(length)
        self.dir = direction
        self.name_size = int(name_size)
        self.num_size = int(num_size)
        self.unit = int(unit)
        self.convert = int(convert)
        self.elec_type = elec_type
        if rest:
            self.pin_type = rest[0]
        else:
            self.pin_type = ""

    def __str__(self):
        return "PIN: %s (%s)" % (self.name, self.num)

    def render_cairo(self, ctx, origx, origy):
        ctx.set_line_width(MIN_WIDTH)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)

        sx = self.posx + origx
        sy = -self.posy + origy

        if self.dir == "R":
            ex = sx + self.length
            ey = sy
            numx = (sx + ex) / 2
            numy = sy - self.num_size/2 - TEXT_OFFS
            numth = 0
            namex = ex + TEXT_OFFS
            namey = sy
            namej = ("R", "C")
            nameth = 0
        elif self.dir == "L":
            ex = sx - self.length
            ey = sy
            numx = (sx + ex) / 2
            numy = sy - self.num_size/2 - TEXT_OFFS
            numth = 0
            namex = ex - TEXT_OFFS
            namey = sy
            namej = ("L", "C")
            nameth = 0
        elif self.dir == "D":
            ex = sx
            ey = sy + self.length
            numx = sx - self.num_size/2 - TEXT_OFFS
            numy = (sy + ey) / 2
            numth = math.pi/2
            namex = sx
            namey = ey + TEXT_OFFS
            namej = ("R", "C")
            nameth = math.pi/2
        elif self.dir == "U":
            ex = sx
            ey = sy - self.length
            numx = sx - self.num_size/2 - TEXT_OFFS
            numy = (sy + ey) / 2
            numth = math.pi/2
            namex = sx
            namey = ey - TEXT_OFFS
            namej = ("L", "C")
            nameth = math.pi/2

        ctx.move_to(sx, sy)
        ctx.line_to(ex, ey)
        ctx.set_source_rgb(*COLOR_FG)
        ctx.stroke()

        ctx.arc(sx, sy, 10, 0, 2*math.pi)
        ctx.stroke()

        if self.num_size:
            draw_text(ctx, self.num, numx, numy, self.num_size, "C", "C", numth)

        if self.name_size and self.name != "~":
            ctx.set_source_rgb(*COLOR_PN)
            draw_text(ctx, self.name, namex, namey, self.name_size, namej[0], namej[1], nameth)

    def bounding_box(self):
        """Returns minx, maxx, miny, maxy"""

        sx = self.posx
        sy = -self.posy

        if self.dir == "L":
            ex = sx - self.length
            ey = sy
        elif self.dir == "R":
            ex = sx + self.length
            ey = sy
        elif self.dir == "D":
            ex = sx
            ey = sy + self.length
        elif self.dir == "U":
            ex = sx
            ey = sy - self.length

        return min(sx,ex), max(sx,ex), min(sy,ey), max(sy,ey)

def Arc(object):
    def __init__(self, parent, stack=None):
        self.parent = parent
        self.posx = 0
        self.posy = 0
        self.radius = 0
        self.start_angle = 0
        self.end_angle = 0
        self.startx = 0
        self.starty = 0
        self.endx = 0
        self.endy = 0
        self.fill = "N"
        self.unit = 1
        self.convert = 1

        if stack is not None:
            self.parse_kicad(stack)

    def parse_kicad(self, stack):
        raw_line = stack.pop()
        line = raw_line.strip()
        parts = shlex.split(line)

        head, posx, posy, radius, start_angle, end_engle, unit, convert, thickness, fill, startx, starty, endx, endy = parts

        self.posx = int(posx)
        self.posy = int(posy)
        self.radius = int(radius)
        self.start_angle = int(start_angle)
        self.end_angle = int(end_angle)
        self.startx = int(startx)
        self.starty = int(starty)
        self.endx = int(endx)
        self.endy = int(endy)
        self.unit = int(unit)
        self.convert = int(convert)
        self.fill = fill

    def __str__(self):
        return "ARC"

    def render_cairo(self, ctx, origx, origy):
        pass

    def bounding_box(self):
        """Returns minx, maxx, miny, maxy"""
        return 0, 0, 0, 0

class Circle(object):
    def __init__(self, parent, stack=None):
        self.parent = parent
        self.posx = 0
        self.posy = 0
        self.radius = 0
        self.unit = 1
        self.convert = 1
        self.thickness = 0
        self.fill = "N"

        if stack is not None:
            self.parse_kicad(stack)

    def parse_kicad(self, stack):
        raw_line = stack.pop()
        line = raw_line.strip()
        parts = shlex.split(line)

        head, posx, posy, radius, unit, convert, thickness, fill = parts

        self.posx = int(posx)
        self.posy = int(posy)
        self.radius = int(radius)
        self.unit = int(unit)
        self.convert = int(convert)
        self.thickness = int(thickness)
        self.fill = fill

    def __str__(self):
        return "CIRCLE"

    def render_cairo(self, ctx, origx, origy):
        ctx.set_line_width(max(self.thickness, MIN_WIDTH))

        ctx.arc(self.posx + origx, -self.posy + origy, self.radius, 0, 2*math.pi)

        if self.fill == "f":
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*COLOR_BG)
            ctx.fill()
        elif self.fill == "F":
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*COLOR_FG)
            ctx.fill()
        else:
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke()

    def bounding_box(self):
        """Returns minx, maxx, miny, maxy"""
        minx = self.posx - self.radius
        maxx = self.posx + self.radius
        miny = -self.posy - self.radius
        maxy = -self.posy + self.radius
        return minx, maxx, miny, maxy


class Polyline(object):
    def __init__(self, parent, stack=None):
        self.unit = 1
        self.convert = 1
        self.thickness = 0
        self.points = []
        self.fill = "N"

        if stack is not None:
            self.parse_kicad(stack)

    def parse_kicad(self, stack):
        raw_line = stack.pop()
        line = raw_line.strip()
        parts = shlex.split(line)

        head, npoints, unit, convert, thickness, *points, fill = parts

        self.unit = int(unit)
        self.convert = int(convert)
        self.thickness = int(thickness)
        self.points = [(int(points[i]), int(points[i+1])) for i in range(0, len(points), 2)]
        self.fill = fill

    def __str__(self):
        return "POLYLINE"

    def render_cairo(self, ctx, origx, origy):
        ctx.set_line_width(max(self.thickness, MIN_WIDTH))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        p = self.points[0]
        ctx.move_to (origx + p[0], origy - p[1])
        for p in self.points[1:]:
            ctx.line_to (origx + p[0], origy - p[1])

        if self.fill == "f":
            ctx.close_path()
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*COLOR_BG)
            ctx.fill()
        elif self.fill == "F":
            ctx.close_path()
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*COLOR_FG)
            ctx.fill()
        else:
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke()

    def bounding_box(self):
        """Returns minx, maxx, miny, maxy"""
        minx = min(i[0] for i in self.points)
        maxx = max(i[0] for i in self.points)
        miny = min(-i[1] for i in self.points)
        maxy = max(-i[1] for i in self.points)
        return minx, maxx, miny, maxy

class Rectangle(object):
    def __init__(self, parent, stack=None):
        self.parent = parent
        self.startx = 0
        self.starty = 0
        self.endx = 0
        self.endy = 0
        self.unit = 0
        self.convert = 0
        self.thickness = 0
        self.fill = "N"

        if stack is not None:
            self.parse_kicad(stack)

    def parse_kicad(self, stack):
        raw_line = stack.pop()
        line = raw_line.strip()
        parts=shlex.split(line)

        head, startx, starty, endx, endy, unit, convert, thickness, fill = parts
        self.startx = int(startx)
        self.starty = int(starty)
        self.endx = int(endx)
        self.endy = int(endy)
        self.unit = int(unit)
        self.convert = int(convert)
        self.thickness = int(thickness)
        self.fill = fill

    def __str__(self):
        return "RECTANGLE"

    def render_cairo(self, ctx, origx, origy):
        ctx.set_line_width(max(self.thickness, MIN_WIDTH))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)

        sx = self.startx + origx
        sy = -self.starty + origy
        ex = self.endx + origx
        ey = -self.endy + origy

        ctx.move_to(sx, sy)
        ctx.line_to(sx, ey)
        ctx.line_to(ex, ey)
        ctx.line_to(ex, sy)
        ctx.close_path()

        if self.fill == "f":
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*COLOR_BG)
            ctx.fill()
        elif self.fill == "F":
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*COLOR_FG)
            ctx.fill()
        else:
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke()

    def bounding_box(self):
        """Returns minx, maxx, miny, maxy"""

        minx = min(self.startx, self.endx)
        maxx = max(self.startx, self.endx)
        miny = min(-self.starty, -self.endy)
        maxy = max(-self.starty, -self.endy)
        return minx, maxx, miny, maxy


class Text(object):
    def __init__(self, parent, stack=None):
        self.parent = parent
        self.direction = 0
        self.posx = 0
        self.posy = 0
        self.size = 0
        self.unit = 1
        self.convert = 1
        self.text = ""
        self.italic = False
        self.bold = False
        self.hjust = "C"
        self.vjust = "C"

        if stack is not None:
            self.parse_kicad(stack)

    def parse_kicad(self, stack):
        raw_line = stack.pop()
        line = raw_line.strip()
        parts=shlex.split(line)

        head, direction, posx, posy, size, unused, unit, convert, text, italic, bold, hjust, vjust = parts
        self.direction = int(direction)
        self.posx = int(posx)
        self.posy = int(posy)
        self.size = int(size)
        self.unit = int(unit)
        self.convert = int(convert)
        self.text = text.replace("~", " ")
        self.italic = (italic == "Italic")
        self.bold = bool(int(bold))
        self.hjust = hjust
        self.vjust = vjust

    def __str__(self):
        return "TEXT"

    def render_cairo(self, ctx, origx, origy):
        theta = (self.direction / 10 / 360) * 2 * math.pi
        ctx.set_source_rgb(*COLOR_FG)
        draw_text(ctx, self.text, self.posx + origx, -self.posy + origy, self.size,
                self.hjust, self.vjust, theta)

    def bounding_box(self):
        """Returns minx, maxx, miny, maxy"""
        return 0, 0, 0, 0

def parse_file(f):
    stack = []
    for line in f:
        stack.append (line)

    stack.reverse()
    items = []

    while stack:
        obj = SchSymbol(stack)
        try:
            obj.name
        except IndexError:
            pass
        else:
            items.append (obj)

    return items

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        items = parse_file(f)

    libname = os.path.basename(sys.argv[1])
    assert libname.endswith(".lib")
    libname = libname[:-4]
    print("# " + libname)
    print()

    for item in items:

        print("## " + item.name)
        for unit in range(1, 1+item.n_units):
            filename = "images/%s__%s__%d.png" % (libname, item.name, unit)
            print("![%s](%s) " % (item.name + "__%d" % unit, "/images/%s__%s__%d.png?raw=true" % (libname, item.name, unit)), end='')

            itemcopy = copy.deepcopy(item)
            itemcopy.filter_unit(unit)

            minx, maxx, miny, maxy = itemcopy.bounding_box()

            width = maxx - minx + 25
            height = maxy - miny + 25
            origx = width/2 - (maxx+minx)/2
            origy = height/2 - (maxy+miny)/2

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width//MILS_PER_PIXEL, height//MILS_PER_PIXEL)
            ctx = cairo.Context(surface)
            ctx.scale(1/MILS_PER_PIXEL, 1/MILS_PER_PIXEL)

            itemcopy.sort_objects()
            itemcopy.render_cairo(ctx, origx, origy)

            surface.write_to_png(filename)
        print()
