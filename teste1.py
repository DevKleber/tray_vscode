import os
import sys
import sqlite3
conn = sqlite3.connect('tray.db')
c = conn.cursor()

import Tkinter
import tkFileDialog

from PySide2 import QtWidgets, QtGui

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip('Code Tray by Bitter')
        global menu
        menu = QtWidgets.QMenu(parent)
	
        c.execute('SELECT * FROM projects')
        rows = c.fetchall()
        for row in rows:
                path = row[0]
                name = path
                last = path.split('/')[-1]
                open_app = menu.addAction(last)
                open_app.triggered.connect( lambda: self.vscode(path))
                open_app.setIcon(QtGui.QIcon("img/vscode.svg"))
        
        menu.addSeparator()

        addNew = menu.addAction("Adicionar")
        addNew.triggered.connect(self.add)
        addNew.setIcon(QtGui.QIcon("img/plus.png"))
		
        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())
        exit_.setIcon(QtGui.QIcon("img/logout.png"))

        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)

    def vscode(self, index):
        os.system('code '+str(index))

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
                QtWidgets.QApplication.exit()
                
    def add(self):
        Tkinter.Tk().withdraw() # Close the root window
        in_path = tkFileDialog.askdirectory()
        
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='projects' ''')
        if c.fetchone()[0]==0 : {    
            c.execute('''CREATE TABLE projects(path text)''')# Create table
        }
        
        # c.execute("INSERT INTO projects VALUES ('"+str(in_path)+"')")
        # conn.commit()
        

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("img/icon.png"), w)
    tray_icon.show()
    tray_icon.showMessage('TrayCode', 'Hi "bitter')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()