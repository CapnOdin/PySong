# -*- coding: utf-8 -*-
import re, os, shutil
from PIL import Image
from svglib.svglib import svg2rlg

from reportlab.graphics import renderPDF

def create_preamble(name, style, logo):
	if ".svg" in logo:		  #check if the logo is in svg format
		tempf = open(logo, 'r')	  #open the file for reading
		s = tempf.read()
		height_k = re.search('height=\"(\d*).(\d*)', s)		  #get the height of the picture, using regular expressions
		height_l = float(re.search('\"(\d*).(\d*)', height_k.group(0)).group(0)[1:])		 #get only the height

		width_k = re.search('width=\"(\d*).(\d*)', s)			#get the width of the picture, using regular expressions
		width_l = float(re.search('\"(\d*).(\d*)', width_k.group(0)).group(0)[1:])		   #get only the width
		
		drawing = svg2rlg(logo)		 #draw the picture
		logo = logo.replace(".svg", ".pdf")		 #replace the .svg part with .pdf
		renderPDF.drawToFile(drawing, "temp/" + logo[logo.rfind("/") + 1:])			#draw the picture to the file and render it
		
	else:
		width_l, height_l = Image.open(logo).size
		if(os.path.isfile(logo)):
			shutil.copy(logo, "temp/" + logo[logo.rfind("/") + 1:])
			
	logo = logo[logo.rfind("/") + 1:]
	
	scale_height = 622.519685 / height_l
	scale_width = 418.110236 / width_l
	scale = (min(scale_height, scale_width))		 #calculate how much the logo can be scaled
	
		
	f = open("Resources/SongBookletTemplate.tex", 'r', encoding = 'utf-8')		#now create the tex file for the songbook itself

	tex = f.read()
	f.close()
	
	return tex.replace("***NAME***", name).replace("***LOGO***", logo).replace("***NUMBERING***", style).replace("***SCALE***", str(scale * 0.4))

