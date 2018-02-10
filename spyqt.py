'''
Spy on the initial setup of a PyQt application and report

USAGE: You must start a Qt application before calling tellall.
It requires the app to exist. However, you should call tellall
immediately (or at least soon) after creating the app.

'''
__all__ = ['tellall']

def tellall() :

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
    fink( 'QTWEBENGINEPROCESS_PATH', os.environ['QTWEBENGINEPROCESS_PATH'] )


    from PyQt5.QtCore import QLibraryInfo

    fink( 'Qt Prefix Path', QLibraryInfo.location( QLibraryInfo.PrefixPath ) )
    fink( 'Qt LibraryExecutables', QLibraryInfo.location( QLibraryInfo.LibraryExecutablesPath ) )
    fink( 'Qt Plugins', QLibraryInfo.location( QLibraryInfo.PluginsPath ) )
    fink( 'Qt Data (resources) path', QLibraryInfo.location( QLibraryInfo.DataPath ) )
    fink( 'Qt Translations', QLibraryInfo.location( QLibraryInfo.TranslationsPath ) )

if __name__ == '__main__' :
    # Start the application so LibraryInfo will work
    from PyQt5.QtWidgets import QApplication
    TheApp = QApplication( [] )
