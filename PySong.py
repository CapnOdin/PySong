import sys, os, getopt, re
import preamble, auxiliary, style_tex
from subprocess import call
current_version = sys.version_info
import pyPdf


"""This function is used to create the tex file that is the songbook"""
def create_sangbog(name, style, logo):
	makeDirs()
	
	style = auxiliary.search_styles(style)	  #check if the specified style exist
	
	texPreamble = preamble.create_preamble(name, style, logo)	   #create the preamble of the tex file
	
	songLst = getSongs()

	tex = addString("***SONGS***", songsToString(songLst, style), texPreamble)
	
	makeIndex(songLst)
	
	#call(["pdflatex", "-output-directory", "temp/", "temp/SongBooklet.tex"])
	call(["pdflatex", "-output-directory", "temp/", "-jobname", "SongBook-" + name, "temp/SongBooklet.tex"])
	
	f = open("temp/SongBook-" + name + ".pdf", "rb")
	pdf = pyPdf.PdfFileReader(f)
	#print(pdf.trailer["/Root"]["/PageLabels"]["/Nums"])
	
	inconsistency = False
	for song in songLst:
		if("page" in song["options"]):
			song["options"]["pagebool"] = isSongOnPage(song["title"], song["options"]["page"], pdf.pages)
			if(not song["options"]["pagebool"]):
				inconsistency = True
				
	f.close()
	
	if(inconsistency):
		tex = addString("***SONGS***", songsToString(songLst, style), texPreamble)
		call(["pdflatex", "-output-directory", "temp/", "-jobname", "SongBook-" + name, "temp/SongBooklet.tex"])
	
	addString("%***BOOKLET***", "", tex)
	call(["pdflatex", "-output-directory", "temp/", "-jobname", "SongBook-" + name, "temp/SongBooklet.tex"])
	
	if(os.path.isfile("temp/" + "SongBook-" + name + ".pdf")):
		os.replace("temp/" + "SongBook-" + name + ".pdf", "Booklet/" + "SongBook-" + name + ".pdf")
	

def isSongOnPage(title, pageNum, pages):
	boolean = False
	index = 0
	for page in pages:
		if(index < len(pages) - 1):
			if(re.search("\d+" + title.replace(" ", ""), page.extractText())): # if page contains the song
				if(re.search(str(pageNum) + "$", page.extractText()) != None): # if page ends with the expected page number
					boolean = True
		index += 1
	return boolean
	

def getSongs():
	specialSongs = []
	songs = []
	for file in os.listdir("Songs/"):
		if(file.endswith(".txt")):
			song = fileRead("Songs/" + file)
			line0 = song[:song.find("\n")]
			options = line0[:line0.find("\\")]
			title = re.search('(?<=song{)(.*?)}', line0)
			if(title != None):
				title = title.group(1)
				if(options != ""):
					specialSongs.append({"title" : title, "text" : song[song.find("\\"):], "options" : eval(options)})
				else:
					songs.append({"title" : title, "text" : song[song.find("\\"):], "options" : {}})
	
	sortedSpecialSongs = sorted(specialSongs, key = lambda song: song["options"]["num"])
	for song in sortedSpecialSongs:
		songs.insert(song["options"]["num"], song)
		
	return songs


def songsToString(songs, style):
	songsStr = ""
	next_page = 0
	counter = 0
	bool = False
	linesPerPage = 64 * 2
	
	for song in songs:
		text = ""
		j = song["text"].find("]")
		
		before = song["options"]["pagebool"] if "pagebool" in song["options"] else True
		
		if("page" in song["options"] and before):
			tempStyle = song["options"]["style"] if "style" in song["options"].keys() else "arabic"
			text += "\\setcounter{temppage}{\\value{page}}\n\\pagenumbering{" + tempStyle + "}\n\\setcounter{page}{" + str(song["options"]["page"]) + "}\n"
			next_page = linesPerPage
			bool = True
			
		if("num" in song["options"].keys()):
			text += "\\setcounter{temp}{\\thesongnum}\n\\setcounter{songnum}{" + str(song["options"]["num"]) + "}"
			text += song["text"][:j+1] + "\\hypertarget{" + song["title"] + "}{}\n\\label{song" + str(counter) + "}\n" + song["text"][j+1:] + "\n"
			text += "\n\\setcounter{songnum}{\\thetemp + 1}"
		else:
			next_page -= getNumOfLines(song["text"][j+1:])
			if(bool and next_page < 0):
				text += "\\pagenumbering{" + style + "}\n\\setcounter{page}{\\value{temppage} + 1}\n"
				bool = False
			text += song["text"][:j+1] + "\\hypertarget{" + song["title"] + "}{}\n\\label{song" + str(counter) + "}\n" + song["text"][j+1:] + "\n"
		
		if("page" in song["options"] and not before):
			tempStyle = song["options"]["style"] if "style" in song["options"].keys() else "arabic"
			text += "\\setcounter{temppage}{\\value{page}}\n\\pagenumbering{" + tempStyle + "}\n\\setcounter{page}{" + str(song["options"]["page"]) + "}\n"
			next_page = linesPerPage * 1.5
			bool = True
			
		songsStr += "\n" + text + "\n"
		counter += 1
	return songsStr

	

def getNumOfLines(song):
	num = 0
	song = re.sub("\\\w+", "a", song)
	for line in re.split("\n+", song):
		num += 1 + len(line) / 40
	return num



def makeIndex(songLst):
	index_file = open("temp/titlefile.sbx",'w+', encoding = 'utf-8')
	
	for i in range(0, len(songLst)):
		index_file.write("\\idxentry{" + songLst[i]["title"] + "}{Sang nummer: \\hyperlink{" + songLst[i]["title"] + "}{" + str(i) + "} På side: \pageref{song" + str(i) + "}}\n")
	
	index_file.close()


def fileRead(file):
	try:
		text = open(file, 'r', encoding = 'utf-8-sig').read()
	except:
		text = open(file, 'r').read()
	return text


def addString(tag, string, tex):
	f = open("temp/SongBooklet.tex", 'w+', encoding = 'utf-8')
	tex = tex.replace(tag, string)
	f.write(tex)
	f.close()
	return tex
	

def makeDirs():
	if not os.path.isdir("temp"):
		os.mkdir("temp")
	if not os.path.isdir("Booklet"):
		os.mkdir("Booklet")
	if not os.path.isdir("Songs"):
		os.mkdir("Songs")
	
	
def usage():
	print("Usage: " + sys.argv[0] + " -p <used to define new pagenumbering style> -s <choose pagenumbering style> -n <name of sangbook> -l <file for logo, svg or png>")
	print("Options: -c (if it is a camp) -u (if it is UNF) -e (if you do no want a front page) -S (if you want the songs to be sorted by title) -f (if you want the songs to be sorted by a fixed number)")


def main(argv):
	name = ""		   #name of the songbook
	style = ""		  #the chosen style
	logo = ""		   #the file containing the logo for the front page
	try:
		opts, args = getopt.getopt(argv, "hs:n:l:p:", ["help", "style=", "name=", "logo=", "number_style="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h","--help"):		  #option used to print usage
			usage()
			sys.exit()
		elif opt in ("-s", "--style"):	   #option used to set the pagenumber style in the tex file
			style = arg
		elif opt in ("-n", "--name"):		   #option used to set the name
			name = arg
		elif opt in ("-l", "--logo"):		   #option used to get a logo on the front page
			logo = arg
		elif opt in ("-p", "--number_style"):		  #option used for making a new pagenumber style
			new_style = arg
			n = new_style.split(" ")[0]		#split the argument into two parts, a name
			s = new_style.split(" ")[1]		#and the style, that will be a regular expression
			if auxiliary.search_styles(n) != n:		 #check if the name is already in use, cannot have two styles by the same name
				style_tex.new_page_style(n, s)
				style = n
			else:
				print("There is already a style with that name.")
		else:
			usage()
			sys.exit()
			
	create_sangbog(name, style, logo)		 #call to create sangbog

if __name__=='__main__':
	sys.exit(main(sys.argv[1:]))
