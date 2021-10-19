from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sqlite3
from datetime import date, datetime
from SyntaxHighightEditors import LatexEditor

class database():
    def open(self):
        self.conn = sqlite3.connect('version_history.db')
        print("Database Connected")
        self.create_table()
        
    def close(self):
        self.conn.close()
        print("Database Closed")
    
    def clearTable(self):
        cmd  = f"DELETE FROM VERSIONS"
        self.conn.execute(cmd);
        self.conn.commit()

    def create_table(self):
        try:
            self.conn.execute('''CREATE TABLE VERSIONS
             (Version INT NOT NULL,
             filename            TEXT   ,
             filename_Ver        CHAR(500) NOT NULL,
             version_Date         DATE, 
             PRIMARY KEY (Version, filename_Ver));''')
            print("Table VERSIONS Created")
        except:
            pass

        try:
            self.conn.execute('''CREATE TABLE RECENT
             (filename            TEXT ,        
             PRIMARY KEY (filename));''')
            
            print("Table RECENT Created")
        except:
            pass

        try:
            self.conn.execute('''CREATE TABLE DOCCLASS
             (classname            TEXT ,        
             classfile            TEXT , 
             PRIMARY KEY (classname));''')
            
            print("Table DOCCLASS Created")
        except:
            pass
        '''
        cmd  = f"INSERT INTO DOCCLASS (classname, classfile) \
                    VALUES ('IEEE Transaction', 'IEEEtran' )"

        self.conn.execute(cmd);

        cmd  = f"INSERT INTO DOCCLASS (classname, classfile) \
                    VALUES ('IISc Thesis Chapter', 'iiscthes' )"

        self.conn.execute(cmd);

        '''

    def create_version(self, fname):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        dt_string1 = now.strftime("%Y-%m-%d")
        ver_fname = fname.replace(':','-').replace('/','-')+'_'+ dt_string;
        ver = self.getLatestVersion(fname)+1


        cmd  = f"INSERT INTO VERSIONS (Version,filename,filename_Ver,version_Date) \
                    VALUES ({ver}, '{fname}', '{ver_fname}','{dt_string1}' )"

        self.conn.execute(cmd);
        self.conn.commit()
        print(f"Version {ver} created for '{fname}'")
        return ver_fname

    def create_record(self, ver, fname, fname_ver, ver_date):
        cmd  = f"INSERT INTO VERSIONS (Version,filename,filename_Ver,version_Date) \
                    VALUES ({ver}, '{fname}', '{fname_ver}','{ver_date}' )"
        try:
            self.conn.execute(cmd);
            print(f"Created record ({ver}, '{fname}', '{fname_ver}','{ver_date}'' )." )
            self.conn.commit()
        except sqlite3.Error as er:
            print("Error: Version Already Exist")
    def addrecent(self, fname):
        
        r = self.getRecentFiles()
        if(len(r) == 10):
            print(r[0])
            q= "DELETE FROM RECENT WHERE filename =='" + r[0] + "'"
            self.query(q)

        cmd  = f"INSERT INTO RECENT (filename) \
                    VALUES ('{fname}')"
        try:
            self.conn.execute(cmd);
            
            self.conn.commit()
        except sqlite3.Error as er:
            print("Error: Version Already Exist")
    def getRecentFiles(self):
        q= "SELECT * from RECENT"
        r = self.query(q)
        return r

    def showAll(self):
        cursor = self.conn.execute("SELECT * from VERSIONS")
        for row in cursor:
            print(row)
    def showAllFiles(self):
        cursor = self.conn.execute("SELECT DISTINCT(filename) from VERSIONS")
        vals = []
        for row in cursor:
            vals.append(row[0])
        return vals
    def query(self, query):
        cursor = self.conn.execute(query)
        self.conn.commit()
        vals = []
        for row in cursor:
            vals.append(row[0])
        return vals

    def getLatestVersion(self, fname):
        print(f"SELECT Version from VERSIONS where filename = '{fname}'")
        cursor = self.conn.execute(f"SELECT Version from VERSIONS where filename = '{fname}'")
        mx = 0
        for row in cursor:
            if(row[0] > mx):
                mx = row[0]
        return mx
    def getVersion(self, fname, ver):
        print(f"SELECT filename_Ver from VERSIONS where filename = '{fname} and Version = {ver}'")
        cursor = self.conn.execute(f"SELECT filename_Ver from VERSIONS where filename = '{fname}' and Version = {ver}")
        for row in cursor:
            return row[0]

class queryWindow(QWidget):
    file = ''
    def createWindow(self, WindowWidth,WindowHeight, parent = None):
        super(queryWindow,self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.Window|Qt.WindowStaysOnTopHint)
        self.resize(WindowWidth,WindowHeight)
        self.setFocus()
        but = QPushButton("OK")
        txt = QEditText("OK")
        wid1 = QWidget();
        self.layout = QVBoxLayout(wid1)
        self.layout.addWidget(txt)
        self.layout.addWidget(but)
        self.setCentralWidget(wid1)
        self.show()


class versionWindow(QWidget):
    file = ''
    def createWindow(self, WindowWidth,WindowHeight, parent = None):
       
        super(versionWindow,self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.Window|Qt.WindowStaysOnTopHint)
        self.resize(WindowWidth,WindowHeight)
        self.setFocus()
       

        but = QPushButton("OK")

        db = database();
        db.open();
        files = db.showAllFiles();
        ver = []
        for item in files:
            ver.append(db.getLatestVersion(item))
        print(files,ver)
        db.close();

        self.tableWidget = QTableView()
  
        #Row count
        rc = len(ver)
        
        
      
        
        wid1 = QWidget();

        
        model = QStandardItemModel()
        model.setColumnCount(2)  
        model.setHorizontalHeaderLabels(['File Name', 'Latest Version'])
        model.setRowCount(rc)

        for i in range(rc):
            model.setItem(i,0, QStandardItem(files[i]))
            model.setItem(i,1, QStandardItem(str(ver[i])))

        self.tableWidget.setModel(model)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnWidth(0,500)

        but.clicked.connect(self.close)
        self.layout = QVBoxLayout(wid1)
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(but)

        wid1.setLayout(self.layout)

        wid2 = QWidget();
        wd2vbox = QVBoxLayout(wid2)
        wd2hbox = QHBoxLayout()


        self.texEditor = LatexEditor()  
        self.bibEditor = LatexEditor(type = 'bib', bc ='#103841')


        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        #self.tabs.setFont(self.__myFont)
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300,200)
        self.tabs.addTab(self.tab1,"Latex")
        self.tabs.addTab(self.tab2,"Bibtex")
        
        self.tab1.layout = QVBoxLayout()
        self.tab2.layout = QVBoxLayout()
        
        

        self.tab1.layout.addWidget(self.texEditor )
        self.tab2.layout.addWidget(self.bibEditor )

        self.tab1.setLayout(self.tab1.layout)
        self.tab2.setLayout(self.tab2.layout)

        self.list = QListWidget()
        self.list.setMaximumWidth(200)
        self.list.currentItemChanged.connect(self.selectionChanged)
        wd2hbox.addWidget(self.list)
        wd2hbox.addWidget(self.tabs)
        wd2vbox.addLayout(wd2hbox)
        self.btn = QPushButton("Back")
        wd2vbox.addWidget(self.btn)
        wid2.setLayout(wd2vbox)


        self.Stack = QStackedWidget(self)

        

        self.Stack.addWidget(wid1)
        self.Stack.addWidget(wid2)
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.Stack)
        self.setLayout(hbox)

        self.setWindowFlag(Qt.WindowCloseButtonHint)
        self.tableWidget.doubleClicked.connect(self.showVersions)
        self.btn.clicked.connect(self.showPage1)
        #self.Stack.setCurrentIndex(0)
    def showVersions(self):
        index = self.tableWidget.selectionModel().currentIndex()
        value=index.sibling(index.row(),index.column()).data()
        ver =int(index.sibling(index.row(),1).data())
        print(value)
        self.list.clear()
        for i in range(ver):
            self.list.addItem('Version '+ str(i+1))
        self.list.setCurrentItem(self.list.item(0))
        self.file = value

        db= database()
        db.open()
        verfname = db.getVersion(value,1)
        db.close()

        with open('./texversions/'+ verfname +'.tex', 'r') as f:
            tex = f.read()
        self.texEditor.setText(tex)

        self.Stack.setCurrentIndex(1)
    def showPage1(self):
        self.Stack.setCurrentIndex(0)

    def selectionChanged(self):
        ver = self.list.currentItem()
        if ver == None:
            return
        ver = ver.text()
        ver = int(ver[7:])
        db= database()
        db.open()
        verfname = db.getVersion(self.file,ver)
        db.close()
        if not (verfname == None):
            with open('./texversions/'+ verfname +'.pax', 'r') as f:
                intext = f.read()
            tex = intext.split("<<*#tex_seperator*#>>" )
            self.texEditor.setText(tex[0])
            self.bibEditor.setText(tex[1])


        
        
       
