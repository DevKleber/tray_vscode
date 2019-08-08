from PySide2 import QtCore, QtGui, QtWidgets, QtSql
import inspect,os
pathRaiz = os.path.dirname(os.path.abspath(__file__))

def create_connection():
    db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(pathRaiz)+"/tray.db")

    if not db.open():
        QMessageBox.critical(
            None,
            QtWidgets.qApp.tr("Cannot open database"),
            QtWidgets.qApp.tr(
                "Unable to establish a database connection.\n"
                "This example needs SQLite support. Please read "
                "the Qt SQL driver documentation for information "
                "how to build it.\n\n"
                "Click Cancel to exit."
            ),
            QtWidgets.QMessageBox.Cancel,
        )
        return False

    query = QtSql.QSqlQuery(
        "CREATE TABLE IF NOT EXISTS projects(PATH text NOT NULL UNIQUE)"
    )
    if not query.exec_():
        print(query.lastError().text())
        return False
    return True


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        self._path_actions = []

        self._menu = QtWidgets.QMenu(parent)
        self.setContextMenu(self._menu)

        self._separator = self._menu.addSeparator()
        add_action = QtWidgets.QAction(
            "Adicionar", self, icon=QtGui.QIcon(str(pathRaiz)+"/img/plus.png"), triggered=self.add
        )
        quit_action = QtWidgets.QAction(
            "Exit",
            self,
            icon=QtGui.QIcon(str(pathRaiz)+"/img/logout.png"),
            triggered=QtWidgets.QApplication.quit,
        )
        self._menu.addAction(add_action)
        self._menu.addAction(quit_action)

        self.refresh_menu()

        self.activated.connect(self.onTrayIconActivated)

    @QtCore.Slot(QtWidgets.QSystemTrayIcon.ActivationReason)
    def onTrayIconActivated(self, reason):
        if reason in (
            # QtWidgets.QSystemTrayIcon.Trigger,
            QtWidgets.QSystemTrayIcon.DoubleClick,
        ):
            QtWidgets.QApplication.quit()

    def refresh_menu(self):
        menu = self.contextMenu()

        for action in self._path_actions:
            action.deleteLater()

        query = QtSql.QSqlQuery("SELECT * FROM projects")
        self._path_actions = []
        while query.next():
            directory = query.value(0)
            info = QtCore.QFileInfo(directory)
            action = QtWidgets.QAction(info.fileName(), self, triggered=self.vscode)
            action.setIcon(QtGui.QIcon(str(pathRaiz)+"/img/vscode.svg"))
            action.setData(directory)
            self._path_actions.append(action)
        menu.insertActions(self._separator, self._path_actions)

    @QtCore.Slot()
    def add(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            None, self.tr("Open getExistingDirectory")
        )
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO projects VALUES (?)")
        query.addBindValue(directory)
        if not query.exec_():
            print(query.lastError().text())
            return
        self.refresh_menu()

    @QtCore.Slot()
    def vscode(self):
        action = self.sender()
        directory = action.data()
        os.system('code '+str(directory))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    if not create_connection():
        sys.exit(-1)

    if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
        QtWidgets.QMessageBox.critical(
            None, "Systray", "I couldn't detect any system tray on this system."
        )
        sys.exit(1)
    print inspect.getfile(inspect.currentframe()) # script filename (usually with path)
    
    QtWidgets.QApplication.setQuitOnLastWindowClosed(False)
    tray_icon = SystemTrayIcon(QtGui.QIcon(str(pathRaiz)+"/img/icon.png"))
    tray_icon.show()
    tray_icon.showMessage("TrayCode", 'Hi "bitter"')
    sys.exit(app.exec_())