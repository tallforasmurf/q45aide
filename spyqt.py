'''
Spy on the initial setup of a PyQt application and report

USAGE: You must start a Qt application before calling tellall.
It requires the app to exist. Pass a reference to the application
if you want to see the Qt Library paths. Typical:
    from PyQt5.QtWidgets import QApplication
    The_App = QApplication( sys.argv )
    import spyqt; spyqt.tellall( The_App )
'''
__all__ = ['tellall']

def tellall( The_QApplication = None ) :

    def fink(title=str, value=None) :
        if value : # is not None
            print( title, 'is:', value )
        else :
            print( title )

    from PyQt5.Qt import PYQT_VERSION_STR, QT_VERSION_STR
    fink( 'PyQt version', PYQT_VERSION_STR )
    fink( 'Qt version', QT_VERSION_STR )

    import sys
    if getattr( sys, 'frozen', False ) :
        fink( '_MEIPASS', sys._MEIPASS )
    else :
        fink( '(not frozen)' )

    import os
    fink( 'QTWEBENGINEPROCESS_PATH', os.environ.get('QTWEBENGINEPROCESS_PATH',None) )


    from PyQt5.QtCore import QLibraryInfo

    fink( 'Qt Prefix Path', QLibraryInfo.location( QLibraryInfo.PrefixPath ) )
    fink( 'Qt LibraryExecutables', QLibraryInfo.location( QLibraryInfo.LibraryExecutablesPath ) )
    fink( 'Qt Plugins Path', QLibraryInfo.location( QLibraryInfo.PluginsPath ) )
    fink( 'QML 2 Imports Path', QLibraryInfo.location( QLibraryInfo.Qml2ImportsPath ) )
    fink( 'Qt Data (resources) path', QLibraryInfo.location( QLibraryInfo.DataPath ) )
    fink( 'Qt arch-dep. data', QLibraryInfo.location( QLibraryInfo.ArchDataPath ) )
    fink( 'Qt Translations', QLibraryInfo.location( QLibraryInfo.TranslationsPath ) )

    if The_QApplication :
        fink( 'QApplication dir path', The_QApplication.applicationDirPath() )
        # QApplication.libraryPaths() returns a list of strings
        library_paths = The_QApplication.libraryPaths()
        for (index, one_path) in enumerate(library_paths) :
            fink( 'QApplication library path {}'.format(index), one_path )

if __name__ == '__main__' :
    # Start the application so LibraryInfo will work
    from PyQt5.QtWidgets import QApplication
    TheApp = QApplication( [] )
    tellall( TheApp )
