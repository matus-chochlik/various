#!/usr/bin/env python
# coding=utf-8
import png, numpy, itertools

# infile = 'in.png'
infile = 'bg-heart-big.png'

pngdata = png.Reader(open(infile ,'rb')).asDirect()
pnginfo = pngdata[3]
cols, rows = pnginfo["size"]
planes = pnginfo["planes"]
image_2d = numpy.vstack(pngdata[2])
image_3d = numpy.reshape(image_2d, (rows, cols, planes))

d = 2

potentials = list()

for row in xrange(d, rows-d):
	row_hits = 0
	row_total = 0
	bgn = 0
	end = 0
	prev = 0
	for col in xrange(0, cols):
		up = tuple(image_3d[row-d][col][:3])
		mi = tuple(image_3d[row+0][col][:3])
		dn = tuple(image_3d[row+d][col][:3])

		ud = numpy.absolute(numpy.subtract(up,dn))
		um = numpy.absolute(numpy.subtract(up,mi))
		dm = numpy.absolute(numpy.subtract(dn,mi))

		if (numpy.amax(ud) < 8) and (numpy.amax(um) > 4) and (numpy.amax(um) < 192):
			if prev > 0:
				end += 1
			else:
				bgn = col
				end = col
			prev += 3
		else:
			if prev > 0:
				prev -= 5
			elif end - bgn >= 32:
				prev = 0
				row_hits += 1
				row_total += end - bgn
				#print("row %d : (%d - %d)" % (row, bgn, end))
				bgn = 0
				end = 0
	if row_hits:
		potentials.append((row, row_hits, row_total))
	print(row)

lines = list()

for i in xrange(0, len(potentials)):
	row, row_hits, row_total = potentials[i]

	if row_hits >= 3 and row_total > (cols * 0.055):
		lines.append(row)
	else:
		for ofs in [-1, 1]:
			try:
				row2, row_hits2, row_total2 = potentials[i+ofs]
				if (abs(row-row2) < 5) and ((row_hits+row_hits2 >= 3) and (row_total+row_total2 > (cols * 0.065))):
					lines.append(row)
					break
			except: pass

print(lines)

for row in lines:
	for col in xrange(0, cols):
		up = tuple(image_3d[row-d][col][:3])
		mi = tuple(image_3d[row+0][col][:3])
		dn = tuple(image_3d[row+d][col][:3])

		ud = numpy.absolute(numpy.subtract(up,dn))
		um = numpy.absolute(numpy.subtract(up,mi))

		if (numpy.amax(ud) < 8) and (numpy.amax(um) > 4) and (numpy.amax(um) < 192):
			for o in xrange(1-d,d):
				for clr in [0,1,2]:
					image_3d[row+o][col][clr] = (up[clr]+dn[clr])/2



png.Writer(
	width=cols,
	height=rows,
	greyscale=False,
	planes=planes,
	bitdepth=pnginfo["bitdepth"],
	interlace=pnginfo["interlace"],
	alpha=pnginfo["alpha"]
).write(open('out.png','wb'), numpy.reshape(image_3d, (-1, cols*planes)))
