#!/usr/bin/env python
from pyPdf import PdfFileReader, PdfFileWriter
import sys, os

def mm(mm):
  return mm / 25.4 * 72

def fitPage (p, tw, th, xo, yo, flip, cx = 0, cy = 0):
  w, h = p.cropBox.getWidth() - cx, p.cropBox.getHeight() - cy
  sx, sy = tw / float(w), th / float(h)
  s = min (sx, sy)
  nw, nh = w * s, h * s
  om = 1
  if flip:
    om = -1
    s = -s
    xo += tw
    yo += th
  xo += (tw - nw) / 2 * om; yo += (th - nh) / 2 * om
  xo -= cx/2. * s; yo -= cy/2. * s
  p.addTransformation([s,  0,
                       0,  s,
                       xo, yo])
  return p

def roundTo (n, d):
  return (n / d) * d

def oneBooklet (s, e):
  flip = False
  while s < e:
    yield e, s, flip
    s+=1; e-=1; flip = not flip

def bookletPageNumbers (n):
  n = roundTo (n + 3, 4)
  full = n // 16
  for c in range(full):
    c *= 16
    for p1, p2, flip in oneBooklet(c, c+15):
      yield p1, p2, flip
  c = full * 16
  rest = n - c
  for p1, p2, flip in oneBooklet(c, c+rest-1):
    yield p1, p2, flip

def bookletPages (pdf):
  n = pdf.numPages
  for pn1, pn2, flip in bookletPageNumbers (n):
    p1, p2 = None, None
    if pn1 < n: p1 = pdf.getPage (pn1)
    if pn2 < n: p2 = pdf.getPage (pn2)
    yield p1, p2, flip

def mergePage (d, s):
  d.mergePage (s)

def getIntOpt (i, d = 0):
  if i >= len(sys.argv):
    return d
  return int (sys.argv[i])

cx = mm (getIntOpt (2))
cy = mm (getIntOpt (3))
fin = sys.argv[1]

out = PdfFileWriter()
inp = PdfFileReader (file (fin, "rb"))

w, h = mm(297), mm(210)
for p1, p2, flip in bookletPages(inp):
  p = out.addBlankPage (w, h)
  if (p1):
    mergePage (p, fitPage (p1, w/2, h, 0, 0, flip, cx, cy))
  if (p2):
    mergePage (p, fitPage (p2, w/2, h, w/2, 0, flip, cx, cy))

outf = file (os.path.splitext (fin)[0] + ".booklet.pdf", "wb")
out.write (outf)
outf.close()
