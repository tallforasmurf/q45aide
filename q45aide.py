'''
Program to assist the conversion of a PyQt4/Python2 program to one that works
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
'''

import regex

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Fixup/detect functions, must be defined ahead of feature_dict
def fix_unicode(line) :
    '''
    line contains unicode(), not used in Python 3
    '''
    repat = regex.compile('unicode\\(([^)]+)\\)')
    (suggest, count) = repat.subn('\\1',line)
    if count :
        return [
            'The unicode function is not used in Python 3. Suggest recoding to:',
            suggest]
    else:
        return [
        'The unicode() function is not supported (or needed) in Python 3, delete it'
        ]
def fix_future(line) :
    '''
    line contains __future, indicating Python 2 dependency
    '''
    return [
        'There is no need to import from __future__ in Python 3 (the future is here).'
        ]
def fix_connect(line) :
    '''
    line contains SIGNAL, SLOT, or ".emit(" . If it contains
    xxx.connect(<source obj>, SIGNAL("signame(args)"), <slot executable>)
    suggest recoding it as
    <source obj>.signame.connect(<slot executable>)
    otherwise just flag it
    '''
    pat = '''.+?\.connect\(\s*([^\s,]+)\s*\,\s*SIGNAL\(['"](\w+)[^'"]*['"]\s*\)\s*\,\s*([^)]+)\)'''
    m = regex.match(pat, line)
    if m :
        return ['old-style signal, suggest recoding as',
        '{0}.{1}.connect({2})'.format(m.group(1),m.group(2),m.group(3)) ]
    else :
        return ['old-style signal, the new API is',
        'source_object.signalname.connect(slot_executable)' ]
def fix_variant(line) :
    '''
    line uses QVariant or perhaps ").toXxxx" showing dependence on QVariant
    '''
    return ['QVariant is no longer used. Delete it and just use the Python value']
def fix_nv(line) :
    '''
    line uses QPyNullVariant, warn of change
    '''
    return ['QPyNullVariant no longer exists, and the QVariant API is different.',
            'Refer to pyqt.sourceforge.net/Docs/PyQt5/pyqt_qvariant.html#ref-qvariant'
            ]
def fix_gofn(line) :
    '''
    line contains "getOpenFileName...", warn of changes
    '''
    return [
        "getOpenFileName[s]AndFilter no longer exists." ,
        "getOpenFileName[s] now take a filter= argument, and their",
        "returned value is now a tuple, not a single string, of",
        "  ( selected_path_or_null, value_of_filter_argument )"
    ]

def fix_gsfn(line):
    '''
    line contains "getSaveFileName...", warn of changes
    '''
    return [
        "getSaveFileNameAndFilter no longer exists. getSaveFileName now takes" ,
        "a filter= argument. Its returned is no longer a path string but",
        "a tuple of (selected_path_or_null, value_of_filter_arg)"
        ]
def fix_qgia(line) :
    '''
    line contains QGraphicsItemAnimation, warn of change
    '''
    return [
        'QGraphicsItemAnimation no longer exists. Consider QPropertyAnimation.'
        ]
def fix_qmat(line) :
    '''
    line contains QMatrix, warn of change
    '''
    return [
        'QMatrix no longer exists. Consider QTransform.'
        ]
def fix_qpto(line) :
    '''
    line contains QPyTextObject, warn of change
    '''
    return [
        'QPyTextObject no longer exists. PyQt5 supports defining a Python',
        'class sub-classed from more than one Qt class, refer to',
        'pyqt.sourceforge.net/Docs/PyQt5/pyqt4_differences.html#qpytextobject'
        ]
def fix_qset(line):
    '''
    line contains QSet, warn of different value in Python 2
    '''
    return [
        'QSet returned a list in PyQt4/Python 2. Now it returns a Python set.'
        ]
def fix_qml(line):
    '''
    line contains QtDeclarative, QtScript a/o QtScriptTools
    '''
    return [
        'QtDeclarative, QtScript and QtScriptTools modules no longer exist',
        'Consider recoding using QtQml and QtQuick.'
        ]
def fix_xml(line):
    '''
    line contains QtXml, warn of change
    '''
    return [
        'QtXml no longer exists. Recode using QXMLStreamReader and QXMLStreamWriter',
        ' or Python’s standard XML modules.'
        ]
def fix_ascii(line):
    '''
    line contains .toAscii or .fromAscii, deprecated
    '''
    return [
        'methods .toAscii and .fromAscii are removed, use .toLatin1 or .fromLatin1'
        ]
def fix_uutf8(line):
    '''
    line contains UnicodeUTF8, deprecated
    '''
    return [
        'Qt enum value UnicodeUTF8 is deprecated, just remove it'
        ]
def fix_wsp(line):
    '''
    line contains QWorkspace, removed
    '''
    return [
        'QWorkspace no longer exists. Recode based on QMdiArea.'
        ]
def fix_timer(line):
    '''
    line contains QTimer, warn of resolution change
    '''
    return [
        'QTimer default resolution is now CoarseTimer. Set timer type to'
        'Qt.PreciseTimer for old default behavior.'
        ]
def fix_super(line):
    '''
    line contains super(; if it contains super(anything),
    advise use of simpler super().
    '''
    if regex.search('super\\(\s*[^)]', line) :
        return [
            'In Python 3 use the simpler form of super().__init__'
            ]
    return []

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Global dicts:
#  qname_dict relates QXxxx names to fixup functions.
#
#  fixup_dict relates strings other than QXxxx to fixup functions.
#
#  module_dict relates every QXxxxx to its Qt5 import module. It is
#  only loaded when --import is specified.
#
#  import_dict tabulates the QXxxxx names actually used in the
#     input, under their import module name, so we can
#     generate "from PyQt5.QtXXX import (....)" at the end.
#     When --import is not used, from_dict is not used either.

qname_dict = { 'QVariant' : fix_variant,
               'QGraphicsItemAnimation' : fix_qgia,
               'QMatrix' : fix_qmat,
               'QPyTextObject' : fix_qpto,
               'QSet' : fix_qset,
               'QPyNullVariant' : fix_nv,
               'QtDeclarative' : fix_qml,
               'QtScript' : fix_qml,
               'QtScriptTools' : fix_qml,
               'QtXml' : fix_xml,
               'QWorkspace' : fix_wsp,
               'QTimer' : fix_timer
              }
fixup_dict = { 'SIGNAL' : fix_connect,
                'SLOT' : fix_connect,
                '.emit(' : fix_connect,
                ').to' : fix_variant,
                'getOpenFileName' : fix_gofn,
                'getSaveFileName' : fix_gsfn,
                '.toAscii' : fix_ascii,
                '.fromAscii' : fix_ascii,
                'UnicodeUTF8' : fix_uutf8,
                '__future' : fix_future,
                'unicode(' : fix_unicode,
                'super(' : fix_super
                }
module_dict = { }
import_dict = { }

def load_module_dict():
    '''
    The --import option has been given. Fetch each PyQt5 module
    in turn and interrogate the resulting namespace to build
    module_dict with keys of class-names and values of module-names.
    Also fill in import_dict with keys of module names and values
    of empty sets.
    '''
    global module_dict, import_dict

    def load_namespace( ):
        global module_dict, import_dict
        # pick off QtXxxx from "PyQt5.QtXxxx"
        module_name = namespace.__name__.split('.')[1]
        import_dict[module_name] = set()
        for name in namespace.__dict__ :
            if name.startswith('Q') : # ignore e.g. __file__
                module_dict[name] = module_name

    import PyQt5.Qt as namespace ; load_namespace()
    import PyQt5.QtBluetooth as namespace ; load_namespace()
    import PyQt5.QtCore as namespace ; load_namespace()
    import PyQt5.QtDesigner as namespace ; load_namespace()
    import PyQt5.QtGui as namespace ; load_namespace()
    import PyQt5.QtHelp as namespace ; load_namespace()
    import PyQt5.QtMacExtras as namespace ; load_namespace()
    import PyQt5.QtMultimedia as namespace ; load_namespace()
    import PyQt5.QtMultimediaWidgets as namespace ; load_namespace()
    import PyQt5.QtNetwork as namespace ; load_namespace()
    import PyQt5.QtOpenGL as namespace ; load_namespace()
    import PyQt5.QtPositioning as namespace ; load_namespace()
    import PyQt5.QtPrintSupport as namespace ; load_namespace()
    import PyQt5.QtQml as namespace ; load_namespace()
    import PyQt5.QtQuick as namespace ; load_namespace()
    import PyQt5.QtSensors as namespace ; load_namespace()
    import PyQt5.QtSerialPort as namespace ; load_namespace()
    import PyQt5.QtSql as namespace ; load_namespace()
    import PyQt5.QtSvg as namespace ; load_namespace()
    import PyQt5.QtTest as namespace ; load_namespace()
    import PyQt5.QtWebKit as namespace ; load_namespace()
    import PyQt5.QtWebKitWidgets as namespace ; load_namespace()
    import PyQt5.QtWidgets as namespace ; load_namespace()
    import PyQt5.QtXmlPatterns as namespace ; load_namespace()

def main(in_file, out_file, arg_i, arg_v ):
    global module_dict, import_dict, qname_dict, fixup_dict

    indent_re = regex.compile('^\s*(#*)')
    qnames_re = regex.compile('Q\w+')

    # If we will do suggested imports, load all the classnames
    # in the module_dict. This may take some little while!
    if arg_i :
        load_module_dict()

    line = in_file.readline()
    while line:

        out_lines = []
        indent_m = indent_re.match(line)
        skip = 0 < len(indent_m.group(1)) # is a comment or
        skip |= line.startswith('import') # ..an import or
        skip |= (line.startswith('from') and (0 > line.find('__future')) )
        if not skip :
            # set up appropriate indent for comments
            indent = indent_m.group(0) + '#! '

            # Note all the QXxxx names in this line
            qnames_in_line = qnames_re.findall(line)

            if arg_i :
                # Add each to the set of its module
                for qname in qnames_in_line :
                    if qname in module_dict : # only valid ones
                        import_dict[module_dict[qname]].add(qname)

            # Check the QXxxx names for the troublesome ones.
            for qname in qnames_in_line :
                if qname in qname_dict :
                    out_lines += qname_dict[qname](line)

            # Run through the non-QXxxx indicator strings.
            for (indicator, fixup) in fixup_dict.items() :
                if indicator in line :
                    out_lines += fixup(line)

            # Write any annotation comments.
            for comment in out_lines:
                out_file.write( indent + comment + '\n')
        #endif skip

        out_file.write( line )
        line = in_file.readline()
    # end while line
    if arg_i :
        out_file.write('\n\n#! Suggested import statements for class-names seen above.\n')
        out_file.write('#! You must move these to the top of the file replacing any\n')
        out_file.write('#! existing PyQt4 import statements.\n')
        for (mod_name, class_set) in import_dict.items() :
            if len(class_set) : # not an empty set
                out_file.write('from PyQt5.{0} import\n   ('.format(mod_name))
                join_string = ',\n    ' if arg_v else ', '
                out_file.write(join_string.join(sorted(class_set)))
                out_file.write(')\n')

if __name__ == '__main__' :
    import argparse
    import sys
    parser = argparse.ArgumentParser(
        description='''
    Examine a PyQt4/Python 2.x source file for upgrade to PyQt5 and
    output an annotated copy with comments marking code that needs attention.'''
    )
    parser.add_argument('input_file', type=argparse.FileType('r'),
                        help='Python source file to be examined')
    parser.add_argument('-i,--import',action='store_true',default=False,
            help='write suggested "from PyQt5.QtXxx import(list)" statements' )
    parser.add_argument('-v,--vertical',action='store_true',default=False,
            help='arrange suggested import statements as vertical lists' )
    parser.add_argument('-o,--output', type=argparse.FileType('w'), default=sys.stdout,
            help='output destination, defaults to stdout' )
    args = vars(parser.parse_args())
    main(args['input_file'], args['o,__output'], args['i,__import'], args['v,__vertical'])