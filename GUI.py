
import os, sys, inspect, time

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

import tkinter as tk
from tkinter import ttk, font, filedialog

from PyUtil import GuiUtil, Util, DataFile

import PySong


class Application(ttk.Frame):
	""" GUI application that creates a story based on user input. """
	def __init__(self, master):
		""" Initialize Frame. """
		super(Application, self).__init__(master)
		
		self.styles = ttk.Style(self.master)
		
		self.grid()
		
		GuiUtil.GridColRowConfig(self.master)
		
		GuiUtil.GridColRowConfig(self)
		
		self.grid_rowconfigure(0, weight=0)
		
		self.initVars()
		
		self.create_widgets()
		
		
	def initVars(self):
		
		self.vcmdIsNum = GuiUtil.create_vcmd(self.master, {})
		self.vcmdTNI_10 = GuiUtil.create_vcmd(self.master, {"maxval" : 10})
		self.invcmd_10 = GuiUtil.create_invcmd(self.master, {"maxval" : 10})
		
		self.customFont = font.nametofont("TkTextFont").copy()
		self.customFontMedium = font.nametofont("TkTextFont").copy()
		self.customFontMedium["size"] = 12
		self.customFontLarge = font.nametofont("TkTextFont").copy()
		self.customFontLarge["size"] = 15
		
		self.EntryOptions    = {"font": self.customFontLarge}#, "validate": "key", "validatecommand": self.vcmdTNI_44, "invalidcommand": self.invcmd_44}
		self.EntryOptionsNum = {"font": self.customFontLarge, "justify": tk.RIGHT, "validate": "key", "validatecommand": self.vcmdIsNum}
		self.EntryOptions210 = {"font": self.customFontLarge, "justify": tk.RIGHT, "width": 2, "validate": "key", "validatecommand": self.vcmdTNI_10, "invalidcommand": self.invcmd_10}
		
		self.PathSaves = Util.getScriptPath() + "/Configs"
		
		self.FileOptionsJSON = {"initialdir": self.PathSaves, "filetypes": [("json", ".json"), ("all", "*")], "defaultextension": ".json"}
		
		self.BoolOptions = {"offvalue": "False", "onvalue": "True", "takefocus": False}
		
		self.widgetVars = {"name" : tk.StringVar(), "logo" : tk.StringVar(), "style" : tk.StringVar(), "indexing" : tk.IntVar(), "booklet" : tk.BooleanVar()}
		
		self.LOADED = False
		self.TreeReady = True
		self.filename = ""
		self.tooltip = None
	
	
	def create_widgets(self):
		
		self.create_menu()
		
		self.frameBooklet = ttk.Frame(self, takefocus = False)
		self.frameSongTree = ttk.Frame(self, takefocus = False)
		
		self.create_booklet_widgets()
		self.create_song_treeview()
		
		self.frameBooklet.grid(row = 0, column = 0, sticky=tk.NSEW)
		self.frameSongTree.grid(row = 1, column = 0, sticky=tk.NSEW)
		
		GuiUtil.setScrollBar(self.tree, 0, 1)
		
		self.grid(row = 0, column = 0, sticky=tk.NSEW)
		
		GuiUtil.GridColRowConfig(self.master)
		
		GuiUtil.GridColRowConfig(self)
		
		self.grid_rowconfigure(0, weight=0)
		
		
		
	def create_menu(self):
		self.menubar = ttk.tkinter.Menu(self.master)
		
		self.filemenu = ttk.tkinter.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Load", command=self.Load)
		self.filemenu.add_command(label="Save", command=self.Save)
		self.menubar.add_cascade(label="File", menu=self.filemenu)
		
		GuiUtil.styleMenue(self.master, self.menubar)
		
		self.master.config(menu = self.menubar)
	

	def create_booklet_widgets(self):
		ttk.Label(self.frameBooklet, text = "Titel: ", **self.EntryOptions).grid(row = 0, column = 0)
		self.name = ttk.Entry(self.frameBooklet, textvariable = self.widgetVars["name"], **self.EntryOptions); self.name.grid(row = 0, column = 1)
		
		ttk.Label(self.frameBooklet, text = "Logo: ", **self.EntryOptions).grid(row = 0, column = 2)
		self.logo = ttk.Entry(self.frameBooklet, textvariable = self.widgetVars["logo"], **self.EntryOptions); self.logo.grid(row = 0, column = 3)
		
		ttk.Label(self.frameBooklet, text = "PageNumber Style: ", **self.EntryOptions).grid(row = 0, column = 4)
		self.pstyle = ttk.Entry(self.frameBooklet, textvariable = self.widgetVars["style"], **self.EntryOptions); self.pstyle.grid(row = 0, column = 5)
		self.toolTips(self.pstyle, "E.g. arabic, (R/r)oman, binary, (H/h)ex, ...")
		
		ttk.Label(self.frameBooklet, text = "Indexing: ", **self.EntryOptions).grid(row = 0, column = 6)
		self.indexing = ttk.Entry(self.frameBooklet, textvariable = self.widgetVars["indexing"], width = 2, **self.EntryOptionsNum); self.indexing.grid(row = 0, column = 7)
		
		ttk.Label(self.frameBooklet, text = "Booklet: ", **self.EntryOptions).grid(row = 0, column = 8)
		self.booklet = ttk.Checkbutton(self.frameBooklet, variable = self.widgetVars["booklet"]); self.booklet.grid(row = 0, column = 9)
		
		ttk.Button(self.frameBooklet, text = "Generate", command = self.generate).grid(row = 0, column = 10)
		
		
	def create_song_treeview(self):
#---------------------------------------------Song TreeView-------------------------------------------------
		
		# Boolean Example
		# {"text" : "columnName", "popup" : "menubutton", "choices" : ("True", "False")}
		
		# Laste Example
		# {"text" : "columnName", "headanchor" : tk.W, "stretch" : 1, "width" : 150, "colanchor" : tk.W}


		self.Cols = ("#0", "title", "melody", "author", "options", "song")
		
		data = {"#0" 				: {"text" : "#",		"headanchor" : tk.E, "width" : 40, "popup" : "tag", "tag" : "red"},
				"title" 			: {"text" : "Title",	"colanchor" : tk.W, "width" : 160},
				"melody" 			: {"text" : "Melody",	"colanchor" : tk.W, "width" : 160},
				"author" 			: {"text" : "Author",	"colanchor" : tk.W, "width" : 160},
				"song" 				: {"text" : "Song",	"colanchor" : tk.W, "stretch" : 1},
				"options" 			: {"text" : "Options", "width" : 100}}
				
		self.tree = GuiUtil.TreeView(self, self.frameSongTree, columns = self.Cols, dataColumns = data, selectmode = 'extended') # editableParents = False
		
		self.tree.tag_configure("red", foreground="#8800ff", background="#eeeeee")
		
		# self.tree.bind("<Double-Button-1>", lambda event, widget = self.tree : self.songSelected(event, widget))
		self.tree.bind("<Return>", 			lambda event, widget = self.tree : self.songSelected(event, widget))
		
		self.tree.bind("<<Edited>>", lambda event: self.storeChanges(event))
		
		self.tree.bind("<<TreeReady>>", lambda event: self.Is_Tree_Ready(True))
		
		self.tree.bind("<<TreeBusy>>", lambda event: self.Is_Tree_Ready(False))
		
		
		for song in PySong.SongBooklet("sdc", "arabic", "Resources/UNF_Logo.svg", 0).getSongs():
			values = (song["title"], (song["melody"] if "melody" in song else ""), (song["author"] if "author" in song else ""), song["options"], song["text"])
			self.tree.insert("", tk.END, iid = None, values = values)
	
	def Is_Tree_Ready(self, boolean):
		self.TreeReady = boolean
	
	def wait_for_tree(self):
		while(not self.TreeReady):
			time.sleep(0.2)
	
	def storeChanges(self, event):
		index = self.tree.index(event.data["rowid"])
		indey = None if event.data["column"] == None else int(event.data["column"][1:])
		
		parent = self.tree.parent(event.data["rowid"])
		dest = parent[0].lower() + parent[1:]
		
		if(parent in ("Equipment", "DefaultEquipment")):
			if(parent == "Equipment"):
				slot = index
			else:
				slot = -1
			for i in self.tree.item(event.data["rowid"], "value"):
				if(i != ""):
					self.tree.set(event.data["rowid"], "#3", slot)
					break
		
		if(event.data["column"] == "#0"):
			value = self.tree.item(event.data["rowid"], "text")
		elif(event.data["column"] == None):
			value = self.tree.item(event.data["rowid"], "value")
		else:
			value = self.tree.set(event.data["rowid"], column = event.data["column"])
			
		self.setItem(index, dest, value = value, keyindex = indey)
	
		
#---------------------------------------------GUI Methods-------------------------------------------------
		
	
	def toolTips(self, widget, string = None):
		widget.bind("<Enter>", lambda event: self.generate_tooltip(event, string))
		widget.bind("<Leave>", self.delete_tooltip)
	
	def generate_tooltip(self, event, text = None):
		self.tooltip = GuiUtil.ToolTip(event, text)
	
	def delete_tooltip(self, event):
		if(self.tooltip != None and self.tooltip.winfo_exists()):
			self.tooltip.destroy()

		
#---------------------------------------------Logic Methods-------------------------------------------------
#---------------------------------------------Logic Methods-------------------------------------------------

		
	def Load(self, path = ""):
		if(not path):
			self.filename = filedialog.askopenfilename(**self.FileOptionsJSON)
		else:
			self.filename = path
			
		if(self.filename):
			f = open(self.filename, "r", encoding = "utf-8")
			try:
				save = eval(f.read())
				for key in save["booklet"]:
					self.widgetVars[key].set(save["booklet"][key])
				
				for parent in self.tree.get_children():
					if(self.tree.set(parent, "title") in save["songs"]):
						self.tree.item(parent, tag = ("red",))
						self.tree.set(parent, "options", save["songs"][self.tree.set(parent, "title")])
			except:
				pass
			f.close()
			
		
	def Save(self):
		# self.saveChangesToChar()
		self.filename = filedialog.asksaveasfilename(**self.FileOptionsJSON)
		if(self.filename):
			f = open(self.filename, "w", encoding = "utf-8")
			
			lst = {"booklet" : {}, "songs" : {}}

			for key in self.widgetVars:
				lst["booklet"][key] = self.widgetVars[key].get()
			
			for parent in self.tree.tag_has("red"):
				song = self.tree.set(parent)
				lst["songs"][song["title"]] = song["options"]
			
			f.write(str(lst))
			f.close()
	
	
	def songSelected(self, event, widget, setParents = False):
		if(event.keysym == "Return"):
			rowid = widget.selection()
		else:
			rowid = [widget.identify_row(event.y)]
		
		self.set_songs(rowid, widget, setParents = setParents)
		
		
	def set_songs(self, rowids, widget, boolean = False, setParents = False):
		if(boolean):
			rowids = widget.get_children(rowids)
		for rowid in rowids:
			if(setParents or len(widget.get_children(rowid)) == 0): # widget.parent(rowid) != "" and
				if(not widget.tag_has("red", rowid)):
					widget.item(rowid, tags=("red",))
				else:
					widget.item(rowid, tags=())
			elif(boolean):
				self.set_songs(rowid, widget, True)
		
	
	def generate(self):
		pdf = PySong.SongBooklet(self.widgetVars["name"].get(), self.widgetVars["style"].get(), self.widgetVars["logo"].get(), self.widgetVars["indexing"].get())
		pdf.songLst = [{"title" : self.tree.set(x, "title"), "text" : self.tree.set(x, "song"), "options" : eval(self.tree.set(x, "options"))} for x in self.tree.tag_has("red")]
		pdf.makeBooklet(self.widgetVars["booklet"].get())


# main
root = ttk.setup_master()
root.title("SongBooklet")

icon = tk.PhotoImage(data = DataFile.Valknut)

root.iconphoto(root, icon)

root.focus_force()

app = Application(root)

root.mainloop()
