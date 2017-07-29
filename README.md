# PySong
This package allows for the generation of pdf songbooklets.

## Requirements and Installation:
* *Python 3*: https://www.python.org/downloads/
* *PyPDF2*: `python pip install PyPDF2`
* *svglib*: `python pip install svglib`
* *rstr*:   `python pip install rstr`
* *MiKTeX*:  https://miktex.org/download
* *Songs*:   http://songs.sourceforge.net/downloads.html (You do not need Vim nor Adobe Acrobat Reader)

## Command Line Parameters:
- -l, --logo \<file>
  - Used to specify logo to be used on the first page
- -n, --name \<name>
  - The name/title for the songbook
- -s, --style \<style>
  - Specifies the pagenumber style to be used
- -p, --new_style \<name regular expression>
  - Specifies a new style to be added.
- -i, --indexing \<integer>
  - Specifies the indexation, 0 or 1 works best.

## Usage example:
`python PySong.py -n SDC -s binary -l Resources/UNF_Logo.svg`

This gives a songbooklet where the title is SDC, that have binary pagenumbers, and with the logo UNF_Logo.svg.

## Special Options:
Songs requarering special conditions can specefi the needed information at the start of the song.
The data need to be formatted like a dictionary. e.g. `{"key1" : value1, "key2" : value2}`

### Supported Options
- "num" : int
  - Used to specify the number of the song and its position
- "pos" : int
  - Used to specify the position of the song
- "page" : int
  - Used to specify the page number of the song
- "style" : str
  - Used to specify the page number style of the song

### Song Examples
Fulbert og Beatrice `{"num" : 12, "page" : 10, "style" : "arabic"}`

Vi kan ikke li' `{"pos" : 0}`

## Remarks:
The _**--new_style**_ option takes a style name and a regular expression seperated by a space "**name** *regular-expression*"
> e.g. `python Sangbog.py -p "example ([a-z]|[A-Z])\d"`

Logos have to be either *svg*, *png* or *jpg*.

If the style specified in the option _**--style**_ does not exist then *arabic* style will be used.

**pos** have priority over **num** in regards to positioning.

Currently the temporary **page** number, is only guaranteed to work if no song is longer than a page.
