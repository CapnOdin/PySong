import re

standard = ["arabic", "roman", "Roman", "alph", "Alph", "hex", "binary", "oct"]		 #the standard defined pagenumber styles in latex


"""This function is used to search for a specific pagenumber style,
in the file page_numbering.tex, if the style does not exist,
it returns arabic"""
def search_styles(style):
	if style == "":		 #if not style is defined just return arabic
		style = "arabic"
	else:
		list_styles = getStyles()
		if style not in list_styles:		#check if the style is in the list
			style = "arabic"		#if not return arabic
	if style == "hex":
		style = "hexX"
	elif style == "binary":
		style = "binaryX"
	elif style == "oct":
		style = "octX"
	return style		#otherwise return the style

def getStyles():
	f_style = open("Resources/page_numbering.tex", 'r')		   #open the tex file for reading only
	text = f_style.read()
	list_styles = re.findall('\@\w*}',text)	 #use a regular expressions to get the strings where a specific combination of chars occur
	for i in range(len(list_styles)):		   #go through the list of strings found
		list_styles[i] = list_styles[i][1:len(list_styles[i])-1]		#remove the first char from all entries in the list
		
	return list_styles + standard		  #concat the list with the standard pagenumber style
	