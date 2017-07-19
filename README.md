# PySong generates pdf songbooklets

## Requirements and Installation:
* *Python 3*: https://www.python.org/downloads/
* *svglib*: `python pip install svglib`
* *rstr*:   `python pip install rstr`
* *MiKTeX*:  https://miktex.org/download
* *Songs*:   http://songs.sourceforge.net/downloads.html

## Command Line Parameters:
- -l, --logo \<file>
  - Used to specify logo to be used on the first page
- -n, --name \<name>
  - The name/title for the songbook
- -s, --style \<style>
  - Specifies the pagenumber style to be used
- -p, --new_style \<name regular expression>
  - Specifies a new style to be added.

## Usage example:
`python PySong.py -n SDC -s binary -l Resources/UNF_Logo.svg`

This gives a songbooklet where the title is SDC, that have binary pagenumbers, and with the logo UNF_Logo.svg.

## Remarks:
The _**--new_style**_ option takes a style name and a regular expression seperated by a space "**name** *regular-expression*"

e.g. `python Sangbog.py -p "example ([a-z]|[A-Z])\d"`

Logos have to be either *svg*, *png* or *jpg*.

If the style specified in the option _**--style**_ does not exist then *arabic* style will be used.

Add Experlantion of the new Option system.
