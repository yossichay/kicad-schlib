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

class BoundingBox(object):
    def __init__(self, minx, maxx, miny, maxy):
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

    def __add__(self, other):
        if other == 0:
            return BoundingBox(self.minx, self.maxx, self.miny, self.maxy)
        return BoundingBox(
                min(self.minx, other.minx),
                max(self.maxx, other.maxx),
                min(self.miny, other.miny),
                max(self.maxy, other.maxy))
    __radd__ = __add__

    def __repr__(self):
        return "BoundingBox(%r, %r, %r, %r)" % (
                self.minx, self.maxx, self.miny, self.maxy)

    __str__ = __repr__

    @property
    def width(self):
        return self.maxx - self.minx
    @property
    def height(self):
        return self.maxy - self.miny
    @property
    def centerx(self):
        return (self.maxx + self.minx) / 2
    @property
    def centery(self):
        return (self.maxy + self.miny) / 2

def rotate_point(x, y, theta):
    x2 = x * math.cos(theta) + y * math.sin(theta)
    y2 = x * math.sin(theta) + y * math.cos(theta)
    return x2, y2

def decideg2rad(d):
    return (d/3600) * 2*math.pi

def rad2decideg(r):
    return r / 2*math.pi * 3600

def draw_text(ctx, text, posx, posy, size, hjust, vjust, theta=0):
    """Draw text onto a Cairo context.
    @param ctx - Cairo context
    @param text - string containing text to write
    @param posx - x coordinate of text origin
    @param posy - y coordinate of text origin
    @param hjust - horizontal justification relative to origin: R, C, L
    @param vjust - vertical justification relative to origin: T, C, B
    @param theta - rotation around origin
    @return BoundingBox of text
    """

    ctx.save()

    ctx.select_font_face("Inconsolata", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size*1.5)

    fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()
    (x, y, width, height, dx, dy) = ctx.text_extents(text)

    ctx.translate(posx, posy)
    ctx.rotate(theta)
    ctx.translate(-width/2, fheight/2)

    if hjust == "R":
        sx = -width/2
        minx = -width - size
        maxx = size
    elif hjust == "C":
        sx = 0
        minx = -width/2 - size
        maxx = width/2 + size
    elif hjust == "L":
        sx = width/2
        minx = -size
        maxx = width + size
    else:
        raise ValueError("Expected R, C, or L for hjust; got %r" % hjust)

    if vjust == "T":
        sy = -height/2
        miny = -height/2
        maxy = 0
    elif vjust == "C":
        sy = 0
        miny = -height/2
        maxy = height/2
    elif vjust == "B":
        sy = height/2
        miny = 0
        maxy = height/2
    else:
        raise ValueError("Expected T, C, or B for vjust; got %r" % vjust)

    ctx.move_to(sx, sy - height/2)
    ctx.show_text(text)
    ctx.restore()

    # Rotate the bounding box
    c1 = rotate_point (minx, miny, theta)
    c2 = rotate_point (minx, maxy, theta)
    c3 = rotate_point (maxx, miny, theta)
    c4 = rotate_point (maxx, maxy, theta)
    cs = [c1, c2, c3, c4]

    minx = min(i[0] for i in cs) + posx
    maxx = max(i[0] for i in cs) + posx
    miny = min(i[1] for i in cs) + posy
    maxy = max(i[1] for i in cs) + posy

    return BoundingBox(minx, maxx, miny, maxy)

class SchSymbol(object):
    def __init__(self, stack=None):
        self.fields = []
        self.fplist = []
        self.objects = []
        self.description = ""
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

        state = "root"

        while stack:
            raw_line = stack.pop()
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            try:
                parts = shlex.split(line)
            except ValueError:
                print(line, file=sys.stderr)
                raise

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
                    pass
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
            else:
                assert False, "invalid state %r" % state

    def __str__(self):
        lines = []
        lines.append(self.name + " : " + self.ref + "?")
        lines.extend(str(i) for i in self.objects)
        return '\n'.join(lines)

    def render_cairo(self, ctx, origx, origy):
        bbs = []
        for i in self.objects:
            bb = i.render_cairo(ctx, origx, origy)
            bbs.append (bb)
        return sum(bbs)

    def filter_unit(self, unit):
        self.objects = [i for i in self.objects if (i.unit == unit or i.unit == 0)]

    def filter_convert(self, convert):
        self.objects = [i for i in self.objects if (i.convert == convert or i.convert == 0)]

    def has_convert(self):
        for i in self.objects:
            if i.convert > 1:
                return True
        return False

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
            altnumx = (sx + ex) / 2
            altnumy = sy + self.num_size/2 + TEXT_OFFS
            numth = 0
            namex = ex + TEXT_OFFS + self.parent.text_offset
            namey = sy
            namej = ("L", "C")
            nameth = 0
        elif self.dir == "L":
            ex = sx - self.length
            ey = sy
            numx = (sx + ex) / 2
            numy = sy - self.num_size/2 - TEXT_OFFS
            altnumx = (sx + ex) / 2
            altnumy = sy + self.num_size/2 + TEXT_OFFS
            numth = 0
            namex = ex - TEXT_OFFS - self.parent.text_offset
            namey = sy
            namej = ("R", "C")
            nameth = 0
        elif self.dir == "D":
            ex = sx
            ey = sy + self.length
            numx = sx - self.num_size/2 - TEXT_OFFS
            numy = (sy + ey) / 2
            altnumx = sx + self.num_size/2 + TEXT_OFFS
            altnumy = (sy + ey) / 2
            numth = -math.pi/2
            namex = sx
            namey = ey + TEXT_OFFS + self.parent.text_offset
            namej = ("R", "C")
            nameth = -math.pi/2
        elif self.dir == "U":
            ex = sx
            ey = sy - self.length
            numx = sx - self.num_size/2 - TEXT_OFFS
            numy = (sy + ey) / 2
            altnumx = sx + self.num_size/2 + TEXT_OFFS
            altnumy = (sy + ey) / 2
            numth = -math.pi/2
            namex = sx
            namey = ey - TEXT_OFFS - self.parent.text_offset
            namej = ("L", "C")
            nameth = -math.pi/2

        if self.parent.text_offset == 0:
            # Pin names are on pins, not inside
            numx, altnumx = altnumx, numx
            numy, altnumy = altnumy, numy
            namex = altnumx
            namey = altnumy
            namej = ("C", "C")

        ctx.move_to(sx, sy)
        ctx.line_to(ex, ey)
        ctx.set_source_rgb(*COLOR_FG)
        ctx.stroke()

        # "Inverted" bubble?
        if self.pin_type == "I":
            ctx.arc(ex, ey, 12.5, 0, 2*math.pi)

        # Endpoint
        if self.elec_type != "N":
            ctx.arc(sx, sy, 10, 0, 2*math.pi)
            ctx.stroke()

        bbs = []

        if self.num_size and self.parent.draw_pinnums:
            bbs.append(draw_text(ctx, self.num, numx, numy, self.num_size, "C", "C", numth))

        if self.name_size and self.name != "~" and self.parent.draw_pinnames:
            ctx.set_source_rgb(*COLOR_PN)
            bbs.append(draw_text(ctx, self.name, namex, namey, self.name_size, namej[0], namej[1], nameth))

        # Bounding box
        bbs.append(BoundingBox(min(sx,ex), max(sx,ex), min(sy, ey), max(sy,ey))) # Pin stick bounding box
        return sum(bbs)

class Arc(object):
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

        head, posx, posy, radius, start_angle, end_angle, unit, convert, thickness, fill, startx, starty, endx, endy = parts

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
        self.thickness = int(thickness)
        self.fill = fill

    def __str__(self):
        return "ARC"

    def render_cairo(self, ctx, origx, origy):

        sth = -decideg2rad(self.start_angle)
        eth = -decideg2rad(self.end_angle)
        length = -eth + sth
        sth, eth = eth, sth
        if abs(length) > math.pi * 1.05:
            sth, eth = eth, sth

        posx = self.posx + origx
        posy = -self.posy + origy

        ctx.set_line_width(max(self.thickness, MIN_WIDTH))
        ctx.arc(posx, posy, self.radius, sth, eth)

        if self.fill == "F":
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.fill()
        elif self.fill == "f":
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*COLOR_BG)
            ctx.fill()
        else:
            ctx.set_source_rgb(*COLOR_FG)
            ctx.stroke()


        minx = posx - self.radius
        maxx = posx + self.radius
        miny = posy - self.radius
        maxy = posy + self.radius
        return BoundingBox(minx, maxx, miny, maxy)

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

        posx = self.posx + origx
        posy = -self.posy + origy

        ctx.arc(posx, posy, self.radius, 0, 2*math.pi)

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

        minx = posx - self.radius
        maxx = posx + self.radius
        miny = posy - self.radius
        maxy = posy + self.radius
        return BoundingBox(minx, maxx, miny, maxy)


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

        minx = min(i[0] for i in self.points) + origx
        maxx = max(i[0] for i in self.points) + origx
        miny = min(-i[1] for i in self.points) + origy
        maxy = max(-i[1] for i in self.points) + origy
        return BoundingBox(minx, maxx, miny, maxy)

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

        minx = min(self.startx, self.endx) + origx
        maxx = max(self.startx, self.endx) + origx
        miny = min(-self.starty, -self.endy) + origy
        maxy = max(-self.starty, -self.endy) + origy
        return BoundingBox(minx, maxx, miny, maxy)


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
        theta = (-self.direction / 10 / 360) * 2 * math.pi
        ctx.set_source_rgb(*COLOR_FG)
        return draw_text(ctx, self.text, self.posx + origx, -self.posy + origy, self.size,
                self.hjust, self.vjust, theta)

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

def get_item(items, name):
    for item in items:
        if item.name == name:
            return item

def load_dcm(items, f):
    item = None

    for line in f:
        if line.startswith("$CMP "):
            name = line.partition(" ")[2].strip()
            item = get_item(items, name)
        elif line.startswith("D ") and item is not None:
            item.description = line.partition(" ")[2].strip()
        elif line.startswith("$ENDCMP"):
            item = None

if __name__ == "__main__":

    # usage: schlib-render.py outdir abs_outdir libfile [dcmfile]

    outdir = sys.argv[1]
    abs_outdir = sys.argv[2]
    libfile = sys.argv[3]

    with open(libfile) as f:
        items = parse_file(f)

    # Load DCM file?
    if len(sys.argv) > 4:
        dcmfile = sys.argv[4]
        with open(dcmfile) as fdcm:
            load_dcm(items, fdcm)

    # Create a dummy Cairo context for determining bounding boxes
    dummy_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
    dummy_ctx = cairo.Context(dummy_surf)

    libname = os.path.basename(libfile)
    assert libname.endswith(".lib")
    libname = libname[:-4]
    print("# " + libname)
    print()

    for item in items:

        print("## " + item.name)
        if item.description:
            print(item.description)
            print()

        for unit in range(1, 1+item.n_units):
            for convert in range(1, 3 if item.has_convert() else 2):
                san_name = item.name.replace("/", "-")
                filename = "%s/%s__%s__%d__%d.png" % (outdir, libname, san_name, unit, convert)
                print("![%s](%s) " % (item.name + "__%d__%d" % (unit, convert), "%s/%s__%s__%d__%d.png?raw=true" % (abs_outdir, libname, item.name, unit, convert)), end='')

                itemcopy = copy.deepcopy(item)
                itemcopy.filter_unit(unit)
                itemcopy.filter_convert(convert)

                boundingbox = itemcopy.render_cairo(dummy_ctx, 0, 0)

                surf_width = boundingbox.width + 25
                surf_height = boundingbox.height + 25
                origx = surf_width/2 - boundingbox.centerx
                origy = surf_height/2 - boundingbox.centery

                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(surf_width//MILS_PER_PIXEL),
                        int(surf_height//MILS_PER_PIXEL))
                ctx = cairo.Context(surface)
                ctx.scale(1/MILS_PER_PIXEL, 1/MILS_PER_PIXEL)

                itemcopy.sort_objects()
                itemcopy.render_cairo(ctx, origx, origy)

                try:
                    surface.write_to_png(filename)
                except OSError:
                    print(filename, file=sys.stderr)
        print()
