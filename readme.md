q45aide.py
==========

A program to assist the conversion of a PyQt4/Python2 program to one that works
in PyQt5 on Python 3.

    python3 q45aide.py [-i | --imports] [-v | --vertical] [-o output] input

  * input is a path to a python source file presumably using PyQt4 under Python v2.

  * -o output is a path to a writable destination, if omitted, sys.stdout is used.

  * --imports or -i causes appending suggested import statements of the form:
        from PyQt5.Qxxx import (list-of-class-names-alphabetic-order)
      to the output file covering all/only the Qt classes named in the input.

  * --vertical or -v causes the -i import statements to be spaced vertically,
       from PyQt5.Qxxx import (
           Qxxxx,
           ...
           )

The output file is the input file with inserted annotations in the form of
comments all beginning "#!". These comments precede lines that need attention
before they will work with PyQt5. In a few cases the comments contain suggested
recodings, but most just document deprecated classes or changed APIs.

This code does not attempt to perform automatic conversion of the source
text. There are too many variations possible in Python syntax to do a
source-to-source translation based on reading single lines. The only reliable
way to translate would be to use the ast module to parse the source, and then
walk the syntax tree. That's above my pay grade.
