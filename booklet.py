#!/usr/bin/env python
from PyPDF2 import PdfFileReader, PdfFileWriter
import sys, os

def mm(mm):
  return mm / 25.4 * 72

def fitPage (p, tw, th, xo, yo, flip, crop):
  iw, ih = float(p.cropBox.getWidth()), float(p.cropBox.getHeight())
  cbx, cby = p.cropBox.lowerLeft
  cbx, cby = cbx + crop.x * iw, cby + (1 - crop.y - crop.h) * ih
  w, h = float(iw * crop.w), float(ih * crop.h)
  sx, sy = tw / float(w), th / float(h)
  s = min (sx, sy)
  nw, nh = w * s, h * s
  om = 1
  if flip:
    om = -1
    s = -s
    xo += tw
    yo += th
  xo -= float(cbx) * s
  yo -= float(cby) * s
  xo += (tw - nw) / 2 * om; yo += (th - nh) / 2 * om
  p.trimBox.upperLeft = (cbx * s + xo, (cby + h) * s + yo)
  p.trimBox.lowerRight = ((cbx + w) * s + xo, cby * s + yo)
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
  remain = n
  for c in range(full):
    c *= 16
    s = 16
    remain -= s
    if remain <= 4:
      s += remain
      remain = 0
    for p1, p2, flip in oneBooklet(c, c+s-1):
      yield p1, p2, flip
  c = n - remain
  for p1, p2, flip in oneBooklet(c, c+remain-1):
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

def getFloatOpt (i, d = 0):
  if i >= len(sys.argv):
    return d
  return float (sys.argv[i])

class crop:
  pass

evencrop = crop()
evencrop.x = getFloatOpt (2)
evencrop.y = getFloatOpt (3)
evencrop.w = getFloatOpt (4)
evencrop.h = getFloatOpt (5)
oddcrop = crop()
oddcrop.x = getFloatOpt (6, evencrop.x)
oddcrop.y = getFloatOpt (7, evencrop.y)
oddcrop.w = getFloatOpt (8, evencrop.w)
oddcrop.h = getFloatOpt (9, evencrop.h)
fin = sys.argv[1]

out = PdfFileWriter()
inp = PdfFileReader (file (fin, "rb"))

w, h = mm(297), mm(210)
for p1, p2, flip in bookletPages(inp):
  p = out.addBlankPage (w, h)
  if (p1):
    mergePage (p, fitPage (p1, w/2, h, 0, 0, flip, oddcrop))
  if (p2):
    mergePage (p, fitPage (p2, w/2, h, w/2, 0, flip, evencrop))

outf = file (os.path.splitext (fin)[0] + ".booklet.pdf", "wb")
out.write (outf)
outf.close()
