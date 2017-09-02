import sys, os, getopt, re, inspect

# for parent dir
cmd_folder = os.path.realpath(os.path.abspath(os.path.pardir))
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])) + "\\lib"
if cmd_folder not in sys.path:
	#sys.path.insert(0, cmd_folder)
	sys.path.insert(0, cmd_folder + "\\PyPDF2")
	sys.path.insert(0, cmd_folder + "\\svglib")

import preamble, auxiliary, style_tex
from subprocess import call
import PyPDF2


class SongBooklet:
	
	def __init__(self, name, style, logo, indexing):
		
		self.makeDirs() # Generate used directories
		
		# Stored for later use
		self.name = name
		self.indexing = indexing
		self.lastPageChanged = False
		
		# Translates the specified style to the name of an existing one
		self.style = auxiliary.search_styles(style)
		
		# Creates the preamble of the tex file
		self.texPreamble = preamble.create_preamble(name, self.style, logo)
		self.texPreambleTest = preamble.create_preamble(name, "arabic", logo)
		
		# Retrieves the songs in the folder
		self.songLst = self.getSongs()
	
	
	# Main function
	def makeBooklet(self, boolean = True):
		self.songLst = self.sortSongs(self.songLst)
		
		self.makeIndex() # Generates the index file
		
		# Addes the songs to the preamble and generates a simplifyed pdf used to varify that the special conditions of songs are satisfied
		tex = self.makePDF("***SONGS***", self.songsToString(False), self.texPreambleTest, True)
		
		# retrieves the start and end page of each song
		self.checkPagesOfSongs()
		
		# The reason to generate the pdf multiple times is to make the internal latex references work
		tex = self.makePDF("***SONGS***", self.songsToString(), self.texPreamble, True, True)
		
		# Generates the final pdf booklet
		if(boolean):
			self.makePDF("%***BOOKLET***", "", tex)
		else:
			self.compilePDF()
		
		# Moves the pdf to the folder named "Booklet"
		if(os.path.isfile("temp/" + "SongBook-" + self.name + ".pdf")):
			os.replace("temp/" + "SongBook-" + self.name + ".pdf", "Booklet/" + "SongBook-" + self.name + ".pdf")

	
	# Prepares the tex file and generate it
	def makePDF(self, replace, string, tex, quiet = False, draft = False):
		tex = self.addString(replace, string, tex)
		
		# handles if a temporary page number change happens on the last page
		if(self.lastPageChanged):
			tex = self.addString("%***SPECIAL-PAGE-CHANGE***", "\\pagenumbering{" + self.style + "}\n\\setcounter{page}{\\value{temppage} + 1}\n", tex)
		
		self.compilePDF(quiet, draft)
		return tex
		
	
	# Calles pdflatex to generate the pdf
	def compilePDF(self, quiet = False, draft = False):
		args = ["pdflatex", "--output-directory", "temp/", "--jobname", "SongBook-" + self.name, "temp/SongBooklet.tex"]
		if(quiet):
			args.append("--quiet")
		if(draft):
			args.append("--draftmode")
		call(args)

	
	# Finds the start and end page number of each song
	def checkPagesOfSongs(self):
		f = open("temp/SongBook-" + self.name + ".pdf", "rb")
		pdf = PyPDF2.PdfFileReader(f)
		dests = pdf.getNamedDestinations()
		
		# finds the ending destination of each song
		for dest in dests:
			song = re.search("^song(\d*)-?(\d*)$", dest)
			if(song != None and song.group(2).isnumeric()):
				index = int(song.group(1)) - self.indexing
				if("endPage" in self.songLst[index]):
					self.songLst[index]["endPage"] = int(song.group(2)) if self.songLst[index]["endPage"] < int(song.group(2)) else self.songLst[index]["endPage"]
				else:
					self.songLst[index]["endPage"] = int(song.group(2))
		
		# finds the page of the ending destination and the start page of each song
		index = self.indexing
		for song in self.songLst:
			if("endPage" in song):
				song["startPage"] = pdf.getDestinationPageNumber(dests["song" + str(index)])
				song["endPage"] = pdf.getDestinationPageNumber(dests["song" + str(index) + "-" + str(song["endPage"])])
				#print(str(song["startPage"])  + "  " + str(song["endPage"]) + "  " + song["title"])
			index += 1
		f.close()
		
	
	# Loads songs
	def getSongs(self):
		songs = []
		for file in os.listdir("Songs/"):
			if(file.endswith(".txt")):
				song = self.fileRead("Songs/" + file)
				line0 = song[song.find("\\") + 1:song.find("]")]
				options = song[:song.find("\\")]
				title = re.search('(?<=song{)(.*?)}', line0)
				melody = re.search('(?<=sr={)(Melodi:)?\s*(.*?)}', line0)
				author = re.search('(?<=by={)\s*(.*?)}', line0)
				if(title != None):
					lst = {"title" : title.group(1), "text" : song[song.find("\\"):]}
					if(melody != None):
						lst["melody"] = melody.group(2)
					if(author != None):
						lst["author"] = author.group(1)
						
					lst["options"] = eval(options) if options != "" else {}
					
					songs.append(lst)
		return songs
		
		
	# Sort songs
	def sortSongs(self, songlst):
		specialSongs = [song for song in songlst if len(song["options"]) > 0]
		songs = [song for song in songlst if len(song["options"]) == 0]
		
		sortedSpecialSongs = sorted(specialSongs, key = lambda song: self.comparFun(song))
		for song in sortedSpecialSongs:
			index = self.comparFun(song, -1)
			if(index == -1):
				index = len(songs)
			elif(index < 0):
				index += 1
			songs.insert(index, song)
		return songs

	
	# Used for sorting
	def comparFun(self, song, title = True):
		if("pos" in song["options"]):
			return song["options"]["pos"]
		elif("num" in song["options"]):
			return song["options"]["num"] - self.indexing if song["options"]["num"] - self.indexing > 0 else 0
		elif(title is bool):
			return song["title"]
		else:
			return title
		
	
	# Retrieves the song text and handles special conditions of songs
	def songsToString(self, specialOptions = True):
		index = 0
		counter = self.indexing
		tempPageChange = False
		before = True
		after = True
		
		init = "\n\\setcounter{songnum}{" + str(self.indexing) + "}\n\\setcounter{page}{" + str(self.indexing) + "}\n"
		
		songStrLst = []
		
		for song in self.songLst:
			text = [self.handleNoConstraints(song, song["text"].find("]"), counter, specialOptions)]
			
			if(specialOptions):
				#before = song["options"]["pagebool"] if "pagebool" in song["options"] else True
				
				if(tempPageChange and counter == index):
					text.insert((0 if after else len(text)), "\\pagenumbering{" + self.style + "}\n\\setcounter{page}{\\value{temppage} + 1}\n")
					tempPageChange = False
					
				if("page" in song["options"]):
					before, after, index = self.evalPageChangeIndex(counter)
					text.insert((0 if before else len(text)), self.handlePageConstraints(song))
					tempPageChange = True
					
				if("num" in song["options"].keys()):
					text.insert(0, "\\setcounter{temp}{\\thesongnum}\n\\setcounter{songnum}{" + str(song["options"]["num"]) + "}")
					text.append("\n\\setcounter{songnum}{\\thetemp + 1}")
			
			songStrLst.append("".join(text))
			counter += 1
		return init + "\n".join(songStrLst)


	# The latex commands needed to handle temporary page changes
	def handlePageConstraints(self, song):
		tempStyle = song["options"]["style"] if "style" in song["options"].keys() else "arabic"
		return "\\setcounter{temppage}{\\value{page}}\n\\pagenumbering{" + tempStyle + "}\n\\setcounter{page}{" + str(song["options"]["page"]) + "}\n"


	# The latex commands needed to handle an arbitrary song
	def handleNoConstraints(self, song, j, counter, bool = True):
		bookmark = song["title"] if bool else "song" + str(counter)
		song["text"] = song["text"].replace("\\beginverse", "\\hypertarget{song" + str(counter) + "-\\arabic{versenum}}{}\\label{song" + str(counter) + "-\\arabic{versenum}}\n\\beginverse")
		return song["text"][:j+1] + "\\hypertarget{" + bookmark  + "}{}\n\\label{song" + str(counter) + "}\n" + song["text"][j+1:] + "\n"

	
	# Finds an appropriate place to change the page temporarily
	def evalPageChangeIndex(self, index):
		before = self.songLst[(index - 1 if index > 0 else 0)]["endPage"] == self.songLst[index]["startPage"]
		
		page = self.songLst[index]["startPage"]
		while(index < len(self.songLst) and self.songLst[index]["startPage"] == page):
			index += 1
		
		if(index == len(self.songLst)):
			self.lastPageChanged = True
			after = True
		else:
			after = self.songLst[(index - 1 if index > 0 else 0)]["endPage"] == self.songLst[index]["startPage"]
			
		return before, after, index

	
	# Generates the index file
	def makeIndex(self):
		index_file = open("temp/titlefile.sbx",'w+', encoding = 'utf-8')
		
		for i in range(0, len(self.songLst)):
			index_file.write("\\idxentry{" + self.songLst[i]["title"] + "}{Sang nummer: \\hyperlink{" + self.songLst[i]["title"] + "}{" + str(self.indexing + i) + "} På side: \pageref{song" + str(self.indexing + i) + "}}\n")
		
		index_file.close()


	# Made to handle UTF-8 with BOM, UTF-8 without BOM and ANSI
	def fileRead(self, file):
		try:
			text = open(file, 'r', encoding = 'utf-8-sig').read()
		except:
			text = open(file, 'r').read()
		return text

	
	# Replaces the tag with a string and writes it to the tex file
	def addString(self, tag, string, tex):
		f = open("temp/SongBooklet.tex", 'w+', encoding = 'utf-8')
		tex = tex.replace(tag, string)
		f.write(tex)
		f.close()
		return tex
		

	# Makes sure that used directories exists
	def makeDirs(self):
		if not os.path.isdir("temp"):
			os.mkdir("temp")
		if not os.path.isdir("Booklet"):
			os.mkdir("Booklet")
		if not os.path.isdir("Songs"):
			os.mkdir("Songs")
		if not os.path.isdir("Configs"):
			os.mkdir("Configs")
	
	
def handleNewStyle(string):
	name = string.split(" ")[0]		#split the argument into two parts, a name
	style = string.split(" ")[1]		#and the style, that will be a regular expression
	if auxiliary.search_styles(name) != name:		 #check if the name is already in use, cannot have two styles by the same name
		style_tex.new_page_style(name, style)
		return name
	return "arabic"
		
	
def usage():
	print("Usage: " + sys.argv[0] + " -p <used to define new pagenumbering style> -s <choose pagenumbering style> -n <name of sangbook> -l <logo file, svg or png>")
	print("Options: -i (start index)")


def main(argv):
	name = ""		#name of the songbook
	style = ""		#the chosen style
	logo = ""		#the file containing the logo for the front page
	indexing = 0
	try:
		opts, args = getopt.getopt(argv, "hs:n:l:p:i:", ["help", "style=", "name=", "logo=", "number_style=", "indexing="])
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
		elif opt in ("-i","--indexing"):		  #option used to print usage
			indexing = arg
		elif opt in ("-p", "--number_style"):		  #option used for making a new pagenumber style
			style = handleNewStyle(arg)
		else:
			usage()
			sys.exit()
			
	SongBooklet(name, style, logo, int(indexing)).makeBooklet()		 #call to create sangbog

if(__name__ == "__main__"):
	sys.exit(main(sys.argv[1:]))
