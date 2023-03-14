#-------------------------------------------------------------------------------
# Name:        Print Kicad footprint modules in to pdf document
# Purpose:
#
# Author:      Felix Quintana
#
# Created:     30/03/2016
#-------------------------------------------------------------------------------

from os import path, walk, chdir, listdir, devnull
import sys
sys.path.append(path.dirname(__file__))

direct = sys.argv[1:]
if direct:
    mypath = direct[0]
else:
    sys.exit("You must provide one directory")

#From https://github.com/KiCad/kicad-library-utils/tree/master/pcb
import kicad_mod

import subprocess
import time
import math
import reportlab.pdfbase.pdfmetrics as pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
import reportlab.lib.colors as colors

from reportlab.platypus.flowables import Flowable
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, NextPageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus.tableofcontents import TableOfContents

class FootPrintComp():
    xmax = 0
    ymax = 0
    xmin = 0
    ymin = 0

    def __init__(self, f):
        self.module = kicad_mod.KicadMod(f)
        self.calcSize()

    def setCanvas(self, c):
        self.c = c

    def drawText(self, x, y, text, scale, orientation, color, font_size, font):
        c = self.c
        c.saveState()
        padFontSize = (font_size + 0.5) * scale
        yas = pdfmetrics.getAscent(font, padFontSize)
        yds = pdfmetrics.getDescent(font, padFontSize)
        yaj = -(yas + yds) / 3 + padFontSize / 2
        textWidth = stringWidth(str(text), font, padFontSize)
        xpadn = x * scale - textWidth / 2
        ypadn = -y * scale - yaj
        r = 0
        if not ((orientation==0) or (orientation==180)):
            r = 90
            tmp = xpadn
            xpadn = -xpadn * math.cos(math.radians(r)) + ypadn * math.sin(math.radians(r))
            ypadn = -ypadn * math.cos(math.radians(r)) + tmp * math.sin(math.radians(r))
            
        c.rotate(r)
        c.translate(xpadn, ypadn)
        c.setFillColor(color)
        c.setFontSize(padFontSize)
        c.drawString(0, 0, str(text))
        c.restoreState()

    def drawPadShape(self, xsize, ysize, shape, rect_delta_0, rect_delta_1, fill_pad, scale):
        c = self.c
        #pad
        if shape=="rect":
            c.rect(0, 0, xsize, -ysize, fill = fill_pad)
        elif shape=="circle" or shape=="circular":
            #c.translate(xsize/2, -xsize/2)
            c.ellipse(0, 0, xsize, -ysize, fill = fill_pad)
            #c.circle(0, 0, xsize/2, fill = fill_pad)
        elif shape=="trapezoid":
            pth = c.beginPath()
            if rect_delta_0==0:
                delta = rect_delta_1 * scale
                pth.moveTo(delta / 2, 0)
                pth.lineTo(xsize - delta / 2, 0)
                pth.lineTo(xsize + delta / 2, -ysize)
                pth.lineTo(-delta / 2, -ysize)
            else:
                delta = rect_delta_0 * scale
                pth.moveTo(xsize, - delta / 2)
                pth.lineTo(xsize , -ysize + delta / 2)
                pth.lineTo(0, -ysize - delta / 2)
                pth.lineTo(0, delta / 2)
            pth.close()
            c.drawPath(pth, fill = fill_pad)
        elif shape=="oval":
            if xsize<ysize:
                xsize, ysize = ysize, xsize
                c.rotate(90)
                c.translate(-xsize, 0)
            pth = c.beginPath()
            pth.arc(0, 0, xsize, -xsize, 180, 180)
            pth.lineTo(0, -ysize + xsize / 2)
            pth.arc(0, -ysize, xsize, -ysize + xsize, 0, 180)
            pth.lineTo(xsize, - xsize / 2)
            c.drawPath(pth, fill = fill_pad)

    def drawComp(self, x = 0, y = 0):
        c = self.c
        module = self.module
        scale = mm
        font = "Helvetica"
        font_pad_size = 0.3
        col = {}
        col['*.Cu'] = colors.HexColor("#7E7800")
        #Front copper layer
        col['F.Cu'] = colors.darkred
        #Back copper layer
        col['B.Cu'] = colors.darkgreen
        #Inner copper layer
        #Adhesive on board's front
        col['F.Adhes'] = colors.darkmagenta
        #Adhesive on board's back
        col['B.CAdhes'] = colors.darkblue
        #Solder paste on board's front
        col['F.Paste'] = colors.darkred
        #Solder paste on board's back
        col['B.Paste'] = colors.cyan
        #Silkscreen on board's front
        col['F.SilkS'] = colors.darkcyan
        #Silkscreen on board's back
        col['B.SilkS'] = colors.darkmagenta
        #Solder mask on board's front
        col['F.Mask'] = colors.darkmagenta
        #Solder mask on board's back
        col['B.Mask'] = colors.brown
        #Explanatory drawings
        #Explanatory comments
        #User defined meaning
        col['Dwgs.User'] = colors.gray
        col['Cmts.User'] = colors.darkblue
        #Board's perimeter definition

        #Board's edge setback outline
        col['Edge.Cuts'] = colors.darkgoldenrod
        #Footprint courtyards on board's front
        col['F.CrtYd'] = colors.gray
        #Footprint courtyards on board's back
        col['B.CrtYd'] = colors.yellow
        #Footprint assembly on board's front
        col['F.Fab'] = colors.darkgoldenrod
        #Footprint assembly on board's back
        col['B.Fab'] = colors.darkred

        xoff = 0
        yoff = 0

        c.saveState()
        c.translate(x + xoff, y + yoff)

        self.drawText(module.reference['pos']['x'], module.reference['pos']['y'], module.reference['reference'], scale, module.reference['pos']['orientation'], col[module.reference['layer']], module.reference['font']['height'], font)
        self.drawText(module.value['pos']['x'], module.value['pos']['y'], module.value['value'], scale, module.value['pos']['orientation'], col[module.value['layer']], module.value['font']['height'], font)
        if len(module.userText)>0:
            for u in module.userText:
                self.drawText(u['pos']['x'], u['pos']['y'], u['user'], scale, u['pos']['orientation'], col[u['layer']], u['font']['height'], font)

        c.setLineCap(1)

        for l in module.polys:
            c.setStrokeColor(col[l['layer']])
            c.setFillColor(col[l['layer']])
            c.setLineWidth(l['width'] * scale)
            p = c.beginPath()
            p.moveTo(l['pts'][0]['x'] * scale, -l['pts'][0]['y'] * scale)
            for v in l['pts'][1:]:
                p.lineTo(v['x'] * scale, -v['y'] * scale)
            if (l['pts'][0]['x'] == l['pts'][len(l['pts'])-1]['x']) and (l['pts'][0]['y'] == l['pts'][len(l['pts'])-1]['y']):
                fill = 1
            else:
                fill = 0
            c.drawPath(p, fill = fill)

        for l in module.lines:
            c.setStrokeColor(col[l['layer']])
            c.setLineWidth(l['width'] * scale)
            c.line(l['start']['x'] * scale, -l['start']['y'] * scale, l['end']['x'] * scale, -l['end']['y'] * scale)

        for l in module.circles:
            c.setStrokeColor(col[l['layer']])
            c.setLineWidth(l['width'] * scale)
            r = (l['end']['x']-l['center']['x'])**2 + (l['end']['y']-l['center']['y'])**2
            r = r**0.5
            r = r * scale
            c.circle(l['center']['x'] * scale, -l['center']['y'] * scale, r)

        for l in module.arcs:
            c.setStrokeColor(col[l['layer']])
            c.setLineWidth(l['width'] * scale)

            ax0 = l['end']['x'] - l['start']['x']
            ay0 = l['end']['y'] - l['start']['y']
            ax = ax0
            ay = -ay0
            if l['start']['x']<l['end']['x']:
                ax = abs(ax)
            if l['start']['y']>l['end']['y']:
                ay = abs(ay)

            #A = sqr(Ax^2 + Ay^2)
            r = (ax)**2 + (ay)**2
            r = r**0.5
            #arc = tan^-1 (Ay/Ax)
            if ax==0:
                if ay<0:
                    zarc = 270
                else:
                    zarc = 90
            elif ay==0:
                if ax>0:
                    zarc = 0
                else:
                    zarc = 180
            else:
                zarc = math.atan2(ay, ax)
                zarc = math.degrees(zarc)

            r = r * scale
            x0 = l['start']['x'] * scale - r
            y0 = l['start']['y'] * scale + r
            x1 = x0 + r * 2
            y1 = y0 - r * 2

            c.arc(x0, -y0, x1, -y1, zarc , -l['angle'])

        c.restoreState()

        fill_pad = 1
        c.setLineWidth(0.01 * scale)

        for p in module.pads:
            c.saveState()

            c.setStrokeColor(colors.red)
            c.setFillColor(colors.red)
            if '*.Cu' in p['layers']:
                #c.setFillColor(colors.linearlyInterpolatedColor(col['F.Cu'], col['B.Cu'], 1, 0, 0.5))
                c.setFillColor(col['*.Cu'])
            elif 'B.Cu' in p['layers']:
                c.setFillColor(col['B.Cu'])
            elif 'F.Cu' in p['layers']:
                c.setFillColor(col['F.Cu'])

            c.translate(x + xoff, y + yoff)

            c.translate(p['pos']['x'] * scale, -p['pos']['y'] * scale)

            xrz = (p['size']['x'] / 2) * scale
            xsize = - p['size']['x'] * scale
            
            if p['shape']=="circle" or p['shape']=="circular":
                yrz = xrz
                ysize = xsize
            else:
                yrz = (p['size']['y'] / 2) * scale
                ysize = - p['size']['y'] * scale

            tmp = xrz
            xrz = xrz * math.cos(math.radians(p['pos']['orientation'])) + yrz * math.sin(math.radians(p['pos']['orientation']))
            yrz = yrz * math.cos(math.radians(p['pos']['orientation'])) - tmp * math.sin(math.radians(p['pos']['orientation']))

            c.translate(xrz, -yrz)

            c.rotate(p['pos']['orientation'])
            #pad
            if len(p['rect_delta'])>0:
                rect_delta_0 = p['rect_delta'][0]
                rect_delta_1 = p['rect_delta'][1]
            else:
                rect_delta_0 = 0
                rect_delta_1 = 0

            self.drawPadShape(xsize, ysize, p['shape'], rect_delta_0, rect_delta_1, fill_pad, scale)

            #drill
            if len(p['drill'])>0:
                c.restoreState()
                c.saveState()
                try:
                    xsize = - p['drill']['size']['x'] * scale
                except (IndexError, KeyError) as e:
                    xsize = 1 * scale
                    print(self.module.name + ": Drill size x not defined. Assuming " + str(xsize))                    
                
                try:
                    ysize = - p['drill']['size']['y'] * scale
                except (IndexError, KeyError) as e:
                    ysize = 1 * scale
                    print(self.module.name + ": Drill size y not defined. Assuming " + str(ysize))
                
                if xsize<ysize:
                    xsize, ysize = ysize, xsize

                xrz = -xsize / 2
                yrz = -ysize / 2

                tmp = xrz
                xrz = xrz * math.cos(math.radians(p['pos']['orientation'])) + yrz * math.sin(math.radians(p['pos']['orientation']))
                yrz = yrz * math.cos(math.radians(p['pos']['orientation'])) - tmp * math.sin(math.radians(p['pos']['orientation']))

                c.translate(x + xoff, y + yoff)
                c.translate(p['pos']['x'] * scale, -p['pos']['y'] * scale)
                c.translate(xrz, -yrz)

                c.rotate(p['pos']['orientation'])

                c.setStrokeColor(colors.white)
                c.setFillColor(colors.white)

                self.drawPadShape(xsize, ysize, p['drill']['shape'], 0, 0, fill_pad, scale)

            c.restoreState()

            #pad #
            c.saveState()
            c.translate(x + xoff, y + yoff)
            c.translate(p['pos']['x'] * scale, -p['pos']['y'] * scale)
            #c.translate(xrz, -yrz)
            #c.rotate(p['pos']['orientation'])
            
            rot_text = 0
            #if (p['size']['x']<p['size']['y']):
            #    rot_text = 90
                
            self.drawText(0, 0, str(p['number']), scale, rot_text, colors.black, font_pad_size, font)
            c.restoreState()

    def calcSize(self):
        module = self.module
        for l in module.lines:
            self.setSize(l['start']['x'], l['start']['y'])
            self.setSize(l['end']['x'], l['end']['y'])

        for l in module.circles:
            r = (l['end']['x']-l['center']['x'])**2 + (l['end']['y']-l['center']['y'])**2
            r = r**0.5
            self.setSize(l['center']['x'] + r, l['center']['y'] + r)
            self.setSize(l['center']['x'] - r, l['center']['y'] - r)

        for l in module.arcs:
            self.setSize(l['start']['x'], l['start']['y'])
            self.setSize(l['end']['x'], l['end']['y'])

        for p in module.pads:
            self.setSize(p['pos']['x'], p['pos']['y'])
            self.setSize(p['pos']['x'] + p['size']['x']/2, p['pos']['y'] + p['size']['y']/2)
            self.setSize(p['pos']['x'] - p['size']['x']/2, p['pos']['y'] - p['size']['y']/2)

        for l in module.polys:
            for v in l['pts']:
                self.setSize(v['x'], -v['y'])

        self.setSize(module.reference['pos']['x'], module.reference['pos']['y'])
        self.setSize(module.value['pos']['x'], module.value['pos']['y'])

    def setSize(self, x ,y):
        if x>self.xmax:
            self.xmax = x
        if x<self.xmin:
            self.xmin = x
        if y>self.ymax:
            self.ymax = y
        if y<self.ymin:
            self.ymin = y

    def getSize(self):
        xoff = round((self.xmin) * mm, 0)
        yoff = round((self.ymax) * mm, 0)
        xsize = abs(round((abs(self.xmax) + abs(self.xmin)) * mm, 0))
        ysize = abs(round((abs(self.ymax) + abs(self.ymin)) * mm, 0))
        #print(xsize, ysize)
        return xoff, yoff, xsize, ysize

    def getName(self):
        return str(self.module.name)

class FootPrint(Flowable):
    def __init__(self, footprint, showBoundary = 0):
        self.footprint = footprint
        self.drc = FootPrintComp(self.footprint)
        self.xoff, self.yoff, self.width, self.height = self.drc.getSize()
        self.spaceAfter = 10 * mm
        self._showBoundary = showBoundary
        self.hAlign = 'CENTER'
        self.vAlign = "CENTER"
    def wrap(self, *args):
        return (self.width, self.height)
    def draw(self):
        self.drc.setCanvas(self.canv)
        self.drc.drawComp(-self.xoff, self.yoff)
    def getName(self):
        return self.drc.getName()

def footPage(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica',10)
    canvas.setFillColor(colors.black)
    canvas.setFontSize(10)
    canvas.drawString(doc.width/2, 10 * mm, "Page %d" % doc.page)
    h = doc.height + doc.bottomMargin + doc.topMargin
    w = doc.width + doc.leftMargin + doc.rightMargin

    canvas.grid([10*mm, 20*mm, 30*mm, 40*mm], [mm, 10*mm])
    canvas.grid([mm, 10*mm], [mm, 10*mm, 20*mm, 30*mm,40*mm])

    canvas.grid([w-10*mm, w-20*mm, w-30*mm, w-40*mm], [mm, 10*mm])
    canvas.grid([w-mm, w-10*mm], [mm, 10*mm, 20*mm, 30*mm,40*mm])

    canvas.grid([10*mm, 20*mm, 30*mm, 40*mm], [h - mm, h - 10*mm])
    canvas.grid([mm, 10*mm], [h - mm, h - 10*mm, h - 20*mm, h - 30*mm, h - 40*mm])

    canvas.grid([w-10*mm, w-20*mm, w-30*mm, w-40*mm], [h - mm, h - 10*mm])
    canvas.grid([w-mm, w-10*mm], [h - mm, h - 10*mm, h - 20*mm, h - 30*mm, h - 40*mm])
    
    canvas.restoreState()

def addTemplate(doc, frameCount, onPageEnd):
    frameWidth = doc.width/frameCount
    frameHeight = doc.height
    frames = []
    #construct a frame for each column
    for frame in range(frameCount):
        leftMargin = doc.leftMargin + frame*frameWidth
        column = Frame(leftMargin, doc.bottomMargin, frameWidth, frameHeight, id="col_" + str(frame), leftPadding=0, rightPadding=0, bottomPadding=0, topPadding=0)
        frames.append(column)

    template = PageTemplate(frames=frames, onPageEnd=footPage, id="idt_" + str(frameCount))
    doc.addPageTemplates(template)
    return frameWidth

class MyDocTemplate(BaseDocTemplate):
    def __init__(self, *args, **kwargs):
        BaseDocTemplate.__init__(self, *args, **kwargs)
        # BaseDocTemplate keeps a "progress" dictionary for its own
        # internal use, which is updated as various drawings are done.
        # This directs reportlab to use your own custom method
        # as the "callback" function when updates are made.
        # Notice the use of the __ prefix for the method, which ensures
        # that it calls *your* custom class's method, and not the default.
        # Should match the signature of the original callback: (self, type, value)
        self.setProgressCallBack(self.__onProgress)
    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'nombre':
                key = 'f-%s' % self.seq.nextf('nombre')
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (0, text, self.page, key))
    def __onProgress(self, prog_type, value):
        """Progress monitoring"""
        #print('PROGRESS MONITOR:  %-10s   %d' % (prog_type, value))
        if prog_type == "PAGE":
            print("Drawing page: %s" % value)
        elif prog_type == "PASS":
            print("PASS: %s" % value)
        elif prog_type == "FINISHED":
            print("Drawing complete!")

def getUrlGit(dir):
    sys.stdout.flush()
    chdir(dir)
    if '.git' in listdir('.'):
        p = subprocess.Popen("git config --get remote.origin.url", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data = p.communicate(timeout=10)        
        return stdout_data[0].decode().strip()
    else:
        return ""
        
def getTimeGit(dir):
    sys.stdout.flush()
    chdir(dir)
    if '.git' in listdir('.'):
        p = subprocess.Popen("git log -1 --date=short --pretty=format:%cd", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data = p.communicate(timeout=10)
        #h, t = data.split('|')
        #dfmt = '%Y-%m-%d %H:%M'
        #return '{}'.format(time.strftime(dfmt, time.gmtime(float(t))))
        return stdout_data[0].decode().strip()
    else:
        return ""

def testGit():
    try:
        with open(devnull, 'w') as bb:
            rc = subprocess.call("git --version", stdout=bb, stderr=bb)
        if rc != 0:
            raise OSError
    except OSError as oops:
        return 0
    return 1
        
title = "Footprint"
author = path.basename(__file__)
showBoundary = 0
leftMargin = 10*mm
rightMargin = 10*mm
bottomMargin = 20*mm
topMargin = 10*mm
pageCompression = 1
file_pdf = path.join(path.dirname(__file__),"footprint.pdf")

print(mypath, "-->", file_pdf)

doc = MyDocTemplate(file_pdf, pagesize=letter, showBoundary=showBoundary, allowSplitting=1, leftMargin = leftMargin, rightMargin = rightMargin, bottomMargin = bottomMargin, topMargin = topMargin, title = title, author = author, pageCompression = pageCompression)

frameWidth1 = addTemplate(doc, 1, footPage)
frameWidth2 = addTemplate(doc, 2, footPage)
frameWidth3 = addTemplate(doc, 3, footPage)
frameWidth4 = addTemplate(doc, 4, footPage)

style=getSampleStyleSheet()
style.add(ParagraphStyle(name = "nombre",  alignment=TA_CENTER, fontSize=8, fontName="Helvetica", spaceAfter=10*mm, spaceBefore=10*mm))
style.add(ParagraphStyle(name = "titulo",  alignment=TA_CENTER, fontSize=12, fontName="Helvetica", spaceAfter=5*mm, spaceBefore=5*mm))

fls = {}
cont_mod = 0
for (dirpath, dirnames, filenames) in walk(mypath):
    fls0 = []
    for file in filenames:
        if file.endswith(".kicad_mod"):
            fls0.append(path.join(dirpath, file))
    if len(fls0)>0:
        fls[dirpath] = fls0
        cont_mod = cont_mod + len(fls0)

git_ok = testGit()

print("dir: %s" % len(fls) + " mod: %s" % cont_mod)

toc = TableOfContents()

Story = []

dfmt = '%Y-%m-%d %H:%M'
Story.append(Paragraph("Kicad 4.0.+", style['titulo']))
Story.append(Paragraph("Build date: {0}.".format(time.strftime(dfmt, time.gmtime())), style['titulo']))
Story.append(Paragraph("Footprints in real scale.", style['titulo']))
Story.append(Paragraph(".pretty: %s" % len(fls) + " .mod: %s" % cont_mod, style['titulo']))
Story.append(Paragraph("Pretty name (mod counts) (last commit) (url)", style['titulo']))

arg = sys.argv[2:]
for a in arg:
    Story.append(Paragraph(a, style['titulo']))

Story.append(toc)

for direct in sorted(fls.keys()):
    Story4 = []
    Story3 = []
    Story2 = []
    Story1 = []
    direc_base = str(path.basename(direct))
    direc_base = direc_base.replace(".pretty", "")
    print(direc_base)
    fcount = 0
    gdate = ""
    gurl = ""
    
    for file in fls[direct]:
        fcount = fcount + 1
        if git_ok == 1:
            gdate = getTimeGit(direct)
            gurl = getUrlGit(direct)
    
    s = " (" + str(fcount) + ")"
    if len(gdate) > 0:
        s = s + " (" + gdate + ")"
    if len(gurl) > 0:
        gurl = '<link href="' + gurl + '">' + gurl + '</link>'
        s = s + " (" + gurl + ")"
    
    for file in fls[direct]:
        #try:
            f = FootPrint(file, showBoundary)
            w, h = f.wrap()
            if w<=frameWidth4:
                Story4.append(f)
            elif w<=frameWidth3:
                Story3.append(f)
            elif w<=frameWidth2:
                Story2.append(f)
            else:
                Story1.append(f)
                
        #except Exception as e:
            #print(file, "->", e)
            #import traceback
            #traceback.print_exc()
        
    if len(Story4)>0:
        Story.append(NextPageTemplate("idt_4"))
        Story.append(PageBreak())
        if len(direc_base)>0:
            Story.append(Paragraph(direc_base + s, style['nombre']))
            direc_base = ""
        Story.extend(Story4)

    if len(Story3)>0:
        Story.append(NextPageTemplate("idt_3"))
        Story.append(PageBreak())
        if len(direc_base)>0:
            Story.append(Paragraph(direc_base + s, style['nombre']))
            direc_base = ""
        Story.extend(Story3)

    if len(Story2)>0:
        Story.append(NextPageTemplate("idt_2"))
        Story.append(PageBreak())
        if len(direc_base)>0:
            Story.append(Paragraph(direc_base + s, style['nombre']))
            direc_base = ""
        Story.extend(Story2)

    if len(Story1)>0:
        Story.append(NextPageTemplate("idt_1"))
        Story.append(PageBreak())
        if len(direc_base)>0:
            Story.append(Paragraph(direc_base + s, style['nombre']))
            direc_base = ""
        Story.extend(Story1)

doc.multiBuild(Story)