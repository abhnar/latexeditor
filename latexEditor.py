#pyuic5 -o main_window_ui.py ui/main_window.ui
import sys
import sqlite3
import re
import os

from PyQt5 import sip
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from SyntaxHighightEditors import LatexEditor

from versioncontrol import database, versionWindow ,queryWindow          
import logging
import wizard 
import importlib    
import find
import shutil
import subprocess
import re
import traceback

class MyWebView(QWebEngineView):
    def javaScriptConsoleMessage(a,b,d):
        print('')
class Worker(QObject):

    finished = pyqtSignal(int)
    progress = pyqtSignal(int)
    log = ''
    def setDirectory(self,d):
        self.directory = d
    def run(self):
        
        logging.debug("Thread started")

        CREATE_NO_WINDOW = 0x08000000
        if sys.platform == 'linux':
            subprocess.call(['sh', self.directory+'compile.sh'], cwd= self.directory)
            self.finished.emit(0)
        else:
            subprocess.call([self.directory + 'compile.bat'],  cwd= self.directory, creationflags=CREATE_NO_WINDOW)
            self.finished.emit(0)
        
        
        

class EditorMainWindow(QMainWindow):
    doc_class = 'iiscthes'
    file = ''
    original_text_tex = ''
    original_text_bib = ''
    pdf_tex_indicator = (0,0,0,0,1)
    def newTexFile(self):
        importlib.reload(wizard)
        self.mySubwindow=wizard.Wizard(parent = self)

        
    def setData(self,data, filename):
        data = data.split("<<*#tex_seperator*#>>")
        self.texEditor.setText(data[0].strip())
        self.bibEditor.setText(data[1].strip())
        self.pkgEditor.setText(data[2].strip())

        self.doc_class = data[3].strip()
        self.bibsyle = data[4].strip()
        self.doc_params = data[5].strip()
        self.toCopy = data[6].strip()
        self.file = filename[:-4]
        if self.bibsyle == "ieeetran":
            if sys.platform == 'linux':
                self.bibsyle = "ieeetr"
        print(self.file)

        self.saveAction.setEnabled(True)
        self.viewVersions.setEnabled(True)
        self.selectedTex.setEnabled(True)
        self.selectedPDF.setEnabled(True)
        self.openfolder.setEnabled(True)
        self.createDraft.setEnabled(True)
        self.compileAction.setEnabled(True)
        '''
        
        '''

        
        
        
        '''
        if self.file == '':
            fn = 'Untitled'
        else:
            fn = self.file

        if self.original_text_tex !=  self.texEditor.text() or self.original_text_bib !=  self.bibEditor.text():
            reply = QMessageBox.question(
            self, "Message",
            f"Do you want to save '{fn}'? Any unsaved work will be lost.",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save)

            if reply ==  QMessageBox.Discard:
                self.texEditor.setText('')
                self.bibEditor.setText('')
                self.webEngineView.load(QUrl('about::blank'))
            elif reply ==  QMessageBox.Save:
                self.saveTexFile()
                self.texEditor.setText('')
                self.bibEditor.setText('')
                self.webEngineView.load(QUrl('about::blank'))
        '''

    def __init__(self):
        super(EditorMainWindow, self).__init__()
        logging.basicConfig(format='%(levelname)7s: %(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p', filename='femlog.log',filemode='w', level=logging.DEBUG)
        logging.debug('Setting up the Main Window')
        self._createMenuBar()
        self._createToolbar()
        # Window setup
        # --------------

        # 1. Define the geometry of the main window
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowTitle("Latex Editor")
        self.setWindowIcon(QIcon("resources/icons/main.png"))

        # 2. Create frame and layout
        self.__frm = QFrame(self)
        self.__frm.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        self.__lyt = QVBoxLayout()
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        self.__myFont = QFont()
        self.__myFont.setPointSize(12)
        self.__myFont.setBold(True)

       
        


   
        self.texEditor = LatexEditor()  # Will be overridden by lexer!
        self.bibEditor = LatexEditor(type = 'bib', bc ='#103841')
        self.pkgEditor = LatexEditor(type = 'bib', bc ='#103841')

        

        
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tabs.setFont(self.__myFont)
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300,200)
        self.tabs.addTab(self.tab1,"Latex")
        self.tabs.addTab(self.tab2,"Bibtex")
        self.tabs.addTab(self.tab3,"Packages")
        
        self.tab1.layout = QVBoxLayout()
        self.tab2.layout = QVBoxLayout()
        self.tab3.layout = QVBoxLayout()
        
        

        self.tab1.layout.addWidget(self.texEditor )
        self.tab2.layout.addWidget(self.bibEditor )
        self.tab3.layout.addWidget(self.pkgEditor )
        self.texEditor.clicked.connect(self.clearIndicator)

        self.tab1.setLayout(self.tab1.layout)
        self.tab2.setLayout(self.tab2.layout)
        self.tab3.setLayout(self.tab3.layout)
        
        
        self.webEngineView = MyWebView ()
        self.webEngineView.load(QUrl('about::blank'))

        splitter1 = QSplitter(Qt.Horizontal)
        topleft = QFrame()
        textedit = QTextEdit()

        splitter1.addWidget(self.tabs)
        splitter1.addWidget(self.webEngineView)
        splitter1.setSizes([100,100])


        self.__lyt.addWidget(splitter1)

        self.label = QLabel('ABC')
        self.labelStatus = QLabel('Idle')

        self.statusBar = QStatusBar()
        
        self.statusBar.addWidget(self.label)
        self.statusBar.addWidget(self.labelStatus)
        
        self.setStatusBar(self.statusBar)
        self.movie = QMovie("resources/icons/loading.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()

        #self.newTexFile()
        self.show()

    ''''''

    def precompileTex(self):

        idx = self.file.rfind('/')
        directory = self.file[0:idx]
        directory = directory+'/'
        
        #text = self.texEditor.text()
        self.inc_bib = ''
        self.inc_pkg = ''

        txt = self.texEditor.text()
        include = re.findall(r"\\include\{(.*?)\}",txt)
        
        for r in include:
            
            pos  = [(m.start(0), m.end(0))  for m in re.finditer(r"\\include{"+ r +"}", txt)]
            print(r"\\include{"+ r +"}", pos[0])
            #
            indx = txt.rfind('\n',0,pos[0][0])
            
            fl = (txt[indx:pos[0][0]]).strip()
            print(fl)


            if not fl.startswith('%'):
                with open(directory+ r+'.pax','r') as f:
                    inc_txt = f.read()

                data = inc_txt.split("<<*#tex_seperator*#>>")
                #self.texEditor.setText(data[0].strip())
                #self.bibEditor.setText(data[1].strip())
                #self.pkgEditor.setText(data[2].strip())
                txt = txt.replace(r"\include{"+ r +"}",data[0])
                self.inc_bib = self.inc_bib +  data[1].strip()
                self.inc_pkg = self.inc_pkg +  data[2].strip()


        x = self.inc_bib.split('@');
        self.bib_list = {}
        self.bib_merged = {}
        for i in x:
            if i.strip() == '' or i == None:
                continue
            j = i.split(',')
            entry = (j[0].split('{')[1].strip())
            #print('Here:',entry,i)
            if not entry in self.bib_list.keys():
                self.bib_list[entry]='@'+i
                self.bib_merged[entry] = '@'+i
            else:
                print('Here:', self.bib_list[entry])
                print('Here1:', self.bib_merged[entry])
                self.bib_merged[entry] = self.bib_merged[entry]+'@'+i

        
        
        #self.texEditor.setText(txt)
        self.inc_tex = txt
        text = txt


        r1 = re.findall(r"\\cite\{(.*?)\}",text)
        pos = [(m.start(0)) for m in re.finditer(r"\\cite\{(.*?)\}",text)]
        vals = []
        indxs = []
        for r in r1:
               rr = r.split(',')
               for rrr in rr:
                      if not rrr in vals:
                             vals.append(rrr.strip())
        bibtext = self.bibEditor.text() + self.inc_bib
        cite_error = False
        cnt = 0
        for cite in vals:
            if bibtext.find(cite) == -1:
                logging.debug(f"Citation error at {cite}")
                
                pos = text.find(cite)
                indxs.append(pos)
                
                cite_error = True
                break;
            cnt = cnt+1
        if(cite_error):
            self.texEditor.SendScintilla(self.texEditor.SCI_GOTOPOS, indxs[0])
            lineno = self.texEditor.getCursorPosition()
            logging.debug("Cannot Compile due to citation error %d", indxs)
            reply = QMessageBox.critical(
            self, "Error",
            f"Cannot Compile due to citation error @ Line {lineno[0]+1}",
            QMessageBox.Ok)
            

            return
        else:
            if cnt>0:
                self.compileLatex(bib = True)
            else:
                self.compileLatex(bib = False)
    def reportProgress(self, status):
        if status == 1:
            self.movie.stop()
            self.labelStatus.setText("Compilation Eror")
            logging.debug("Compilation Error")
            return
        f = open(self.worker.directory + "temp.log", "r")
        log = f.read()
        
        f.close()
        
        
   
        self.cleanTemp(self.worker.directory)
        
        idx = log.find('!')
        print('index',idx)
        
        if idx >-1:
            print('Exception')
            self.webEngineView.load(QUrl('about::blank'))
            idx_end = log.find('\n\n',idx)
            #print([ord(c) for c in log[idx:idx_end]])
            #print([c for c in log[idx:idx_end]])
            errmsg = log[idx:idx_end]
            errmsg = errmsg.replace('\n','').split('Here is how much of')[0]
            error_dialog = QErrorMessage()
            reply = QMessageBox.critical(
            self, "Error in Compilation",
            errmsg,
            QMessageBox.Ok)
            self.movie.stop()
            self.labelStatus.setText("Compilation Eror")
            logging.debug("Compilation Error")

            return
        else:
            if (os.path.isfile(self.file + '.pdf')):
                try:
                    os.remove(self.file + '.pdf')
                except Exception:
                    print("Unable to write file")  
                    traceback.print_exc() 
                    self.movie.stop()
                    self.labelStatus.setText("Completed Latex compilation: Unable to write pdf file")
                    logging.debug("Completed Latex compilation: Unable to write pdf file") 
                    return
            try:
                os.rename(self.worker.directory+'temp.pdf', self.file + '.pdf')
            except Exception:
                print("Unable to write file")
                traceback.print_exc()
                self.movie.stop()
                self.labelStatus.setText("Completed Latex compilation: Unable to write pdf file")
                logging.debug("Completed Latex compilation: Unable to write pdf file")
                return
            

        
            curdir = os.getcwd().replace("\\","/")
            if (os.path.isfile(self.file + '.pdf')):
                self.webEngineView.load(QUrl(f"file:///{curdir}/resources/web/viewer.html?file={self.file}.pdf"))
        self.movie.stop()
        self.labelStatus.setText("Completed Latex compilation")
        logging.debug("Compilation complete")

    def compileLatex(self, bib = False):
        
        
        self.movie.start()
        self.labelStatus.setText("Beginiing Latex compilation")
        logging.debug("Began compilation")

        with open('resources/compile/doc_classes/pre_general.txt',"r") as f:
            tex = f.read()
        tex = tex.replace("%#*%classname", self.doc_class)
        tex = tex.replace("%#*%bibstyle", self.bibsyle)
        tex = tex.replace("%#*%parameters", self.doc_params)
        
        
        
        if bib:
            tex = tex.replace("%#*%bib_",'\\bibliography{temp}')
        
        tex = tex.replace('%#*%content_',self.inc_tex).replace('%#*%packages_',self.pkgEditor.text()+ self.inc_pkg)
        tex = tex.replace('\r','')
        f = open("./resources/compile/temp.tex", "w")
        f.write(tex)
        f.close()
        f = open("./resources/compile/temp.bib", "w")
        f.write(self.bibEditor.text()+self.inc_bib)
        f.close()

        idx = self.file.rfind('/')
        directory = self.file[0:idx]
        directory = directory+'/'
        
        shutil.copy('./resources/compile/temp.tex', directory + 'temp.tex')
        shutil.copy('./resources/compile/temp.bib', directory + 'temp.bib')
        if not self.toCopy == '':
            shutil.copy('./resources/compile/doc_classes/' + self.doc_class +'.cls', directory + self.doc_class + '.cls')
        if sys.platform == 'linux':
            shutil.copy('./resources/compile/compile.sh', directory + 'compile.sh')
        else:
            shutil.copy('./resources/compile/compile.bat', directory + 'compile.bat')
        
        

        
        self.thread = QThread()
        self.worker = Worker()
        self.worker.setDirectory(directory)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.reportProgress)
        self.thread.start()
        
        

    def cleanTemp(self, dir):
        
        os.remove(dir+'temp.tex')
        os.remove(dir+'temp.bib')
        #os.remove(dir+'temp.log')

        if (os.path.isfile(dir+'temp.aux')):
            os.remove(dir+'temp.aux')
        if (os.path.isfile(dir+'temp.log')):
            os.remove(dir+'temp.log')
        if (os.path.isfile(dir+'temp.out')):
            os.remove(dir+'temp.out')
        
        if (os.path.isfile(dir+'temp.idx')):
            os.remove(dir+'temp.idx')
        if (os.path.isfile(dir+'temp.bbl')):
            os.remove(dir+'temp.bbl')
        if (os.path.isfile(dir+'temp.blg')):
            os.remove(dir+'temp.blg')
        if (os.path.isfile(dir+self.toCopy + '.cls')):
            os.remove(dir+self.toCopy + '.cls')
        if (os.path.isfile(dir+'compile.bat')):
            os.remove(dir+'compile.bat')
        if (os.path.isfile(dir+'compile.sh')):
            os.remove(dir+'compile.sh')
        if (os.path.isfile(dir+self.toCopy+'.cls')):
            os.remove(dir+self.toCopy+'.cls')




    def dbTest(self):
        db = database()
        db.open()
        db.clearTable()
        db.close()
        
    def _createToolbar(self):
        self.fileToolBar = self.addToolBar("File")
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        self.newAction.setIcon(QIcon("resources/icons/new-document.png"))

        self.openAction = QAction(self)
        self.openAction.setText("&Open")
        self.openAction.setIcon(QIcon("resources/icons/open.png"))


        self.saveAction = QAction(self)
        self.saveAction.setText("&Open")
        self.saveAction.setIcon(QIcon("resources/icons/save.png"))

        self.findAction = QAction(self)
        self.findAction.setText("&FInd")
        #self.findAction.setIcon(QIcon("resources/icons/compile.png"))

        self.compileAction = QAction(self)
        self.compileAction.setText("&Compile")
        self.compileAction.setIcon(QIcon("resources/icons/compile.png"))

       

        self.compileAbout = QAction(self)
        self.compileAbout.setText("&About")
        #self.compileAction.setIcon(QIcon("resources/icons/compile.png"))

        
        

        

        self.selectedPDF = QAction(self)
        self.selectedPDF.setText("&Find in Tex")
        self.selectedPDF.setIcon(QIcon("resources/icons/right-arrow.png"))
        

        self.selectedTex = QAction(self)
        self.selectedTex.setText("&Find in PDF")
        self.selectedTex.setIcon(QIcon("resources/icons/left-arrow.png"))
        

        self.openfolder = QAction(self)
        self.openfolder.setText("&Open Folder")
        self.openfolder.setIcon(QIcon("resources/icons/file-explorer.png"))
        
        self.createVersion = QAction(self)
        self.createVersion.setText("&Create Version")
        #self.createVersion.setIcon(QIcon("resources/icons/draft.png"))

        self.createDraft = QAction(self)
        self.createDraft.setText("&Create Draft")
        self.createDraft.setIcon(QIcon("resources/icons/draft.png"))
        

        self.viewVersions = QAction(self)
        self.viewVersions.setText("&Version History")
        self.viewVersions.setIcon(QIcon("resources/icons/version.png"))

        self.saveAction.setEnabled(False)
        self.viewVersions.setEnabled(False)
        self.selectedTex.setEnabled(False)
        self.selectedPDF.setEnabled(False)
        self.openfolder.setEnabled(False)
        self.createDraft.setEnabled(False)
        self.compileAction.setEnabled(False)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.fileToolBar.addAction(self.newAction)
        self.fileToolBar.addAction(self.openAction)
        self.fileToolBar.addAction(self.saveAction)
        
        
        self.fileToolBar.addSeparator()
      
        self.fileToolBar.addAction(self.compileAction)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.selectedPDF)
        self.fileToolBar.addAction(self.selectedTex)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.spacer)
        self.fileToolBar.addAction(self.createVersion)
        self.fileToolBar.addAction(self.createDraft)
        self.fileToolBar.addAction(self.openfolder)
        self.fileToolBar.addAction(self.viewVersions)


        self.recentfileMenu = QMenu("&Recent", self)
        
      
        
        exitAction = QAction("&Exit",self)
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addMenu(self.recentfileMenu)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(exitAction)

        self.editMenu.addAction(self.findAction)
        self.editMenu.addAction(self.compileAction)
        self.helpMenu.addAction(self.compileAbout)
        db = database()
        db.open()
        q = db.query("select * from DOCCLASS")
        print(q)
        r = db.getRecentFiles()
        self.recent = r
        db.close()
        cnt = 0

        for i in reversed(r):
            rec = QAction(self)
            rec.setText(i)
            #rec.triggered.connect(lambda :self.openTexFile(recent = i))
            rec.triggered.connect(self.whichitem)
           
            self.recentfileMenu.addAction(rec)
            cnt = cnt + 1

        self.openAction.triggered.connect(self.openPaxFile)
        self.saveAction.triggered.connect(self.savePaxFile)
        self.newAction.triggered.connect(self.newTexFile)
        self.compileAction.triggered.connect(self.precompileTex)
        self.compileAbout.triggered.connect(self._showAbout)
        self.viewVersions.triggered.connect(self.showVersions)
        self.selectedPDF.triggered.connect(self.gotoTex)
        self.selectedTex.triggered.connect(self.gotoPDF)
        
        self.openfolder.triggered.connect(self.openExplorer)
        self.createDraft.triggered.connect(self.createNewDraft)
        self.findAction.triggered.connect(self.findTextDialog)
        self.createVersion.triggered.connect(self.updateVersion)

    def findTextDialog(self):
        importlib.reload(find)
        self.mySubwindow = find.Find(parent = self)
        self.mySubwindow.show()
        self.texttoFind = ''
        self.curFindix = 0

    def findText(self, text):
        if text == "":
            return

        tex = text.replace('\\','\\\\')
        if(tex == self.texttoFind):
            self.curFindix = self.curFindix + 1
            if(self.curFindix == len(self.findpos)):
                self.curFindix = 0
        else:
            self.texttoFind = tex
            self.findpos  = [(m.start(0), m.end(0)-m.start(0))  for m in re.finditer(self.texttoFind, self.texEditor.text())]


        
        
        self.clearIndicator()
        
        
        
        
        print(self.findpos)
        if len(self.findpos) == 0:
            #print("Not found")
            logging.debug("Not found the text '%s' in Tex", tex)
            return
        logging.debug(self.findpos)
        self.texEditor.SendScintilla(self.texEditor.SCI_GOTOPOS, self.findpos[self.curFindix][0])
            
        self.texEditor.SendScintilla(self.texEditor.SCI_STYLESETHOTSPOT, 10, True)
        DEFAULT_INDICATOR_ID = 1
        lineno = self.texEditor.getCursorPosition()

        
        self.texEditor.indicatorDefine(self.texEditor.StraightBoxIndicator, DEFAULT_INDICATOR_ID)
        
        self.texEditor.fillIndicatorRange(lineno[0], lineno[1], lineno[0], lineno[1]+self.findpos[self.curFindix][1], DEFAULT_INDICATOR_ID)
        self.texEditor.setIndicatorForegroundColor(QColor("green"))
        self.texEditor.setIndicatorDrawUnder(True)
        self.texEditor.setIndicatorOutlineColor(QColor("yellow"))

        self.texEditor.setHotspotUnderline(True)
        self.pdf_tex_indicator = (lineno[0], lineno[1], lineno[0], lineno[1]+self.findpos[self.curFindix][1], DEFAULT_INDICATOR_ID)


    def createNewDraft(self):
        
        idx = self.file.rfind('/')
        directory = self.file[0:idx]
        directory1 = directory+'/draft'
        files = os.listdir(directory)
        

        shutil.copytree(directory, directory1)

    def whichitem(self, button):
        self.openPaxFile(recent =self.sender().text())

    def openExplorer(self):

        if sys.platform == 'linux':
            pass
        else:
            ix = self.file.rfind("/")
            q = (r'explorer /select,"' + self.file[0:ix] +'"').replace("/","\\")
            subprocess.Popen(q)
    
    def gotoTex(self):
        
        self.clearIndicator()
        sel_tex = (self.webEngineView.selectedText())
        if sel_tex == "":
            QMessageBox.information(self, "Find in PDF", "Select some text in PDF")
            return
        
        pos  = [(m.start(0), m.end(0)-m.start(0))  for m in re.finditer(sel_tex.replace(' ','\\s*') , self.texEditor.text())]
        if len(pos) == 0:
            #print("Not found")
            logging.debug("Not found the text '%s' in Tex", sel_tex)
            return
        logging.debug(pos)
        self.texEditor.SendScintilla(self.texEditor.SCI_GOTOPOS, pos[0][0])
            
        self.texEditor.SendScintilla(self.texEditor.SCI_STYLESETHOTSPOT, 10, True)
        DEFAULT_INDICATOR_ID = 1
        lineno = self.texEditor.getCursorPosition()

        
        self.texEditor.indicatorDefine(self.texEditor.StraightBoxIndicator, DEFAULT_INDICATOR_ID)
        
        self.texEditor.fillIndicatorRange(lineno[0], lineno[1], lineno[0], lineno[1]+pos[0][1], DEFAULT_INDICATOR_ID)
        self.texEditor.setIndicatorForegroundColor(QColor("red"))
        self.texEditor.setIndicatorDrawUnder(True)
        self.texEditor.setIndicatorOutlineColor(QColor("yellow"))


      

        self.texEditor.setHotspotUnderline(True)
        self.pdf_tex_indicator = (lineno[0], lineno[1], lineno[0], lineno[1]+pos[0][1], DEFAULT_INDICATOR_ID)
        
        self.texEditor.setFocus()

    def gotoPDF(self):
        key = self.texEditor.selectedText().replace("  "," ")
        if key == "":
            QMessageBox.information(self, "Find in PDF", "Select some text in Tex file")
            return

        code = f'PDFViewerApplication.findController.executeCommand(''find'', {\
            caseSensitive: false,\
            findPrevious: undefined,\
            highlightAll: true, \
            phraseSearch: true, \
            query: "key"\
            });'
        code = code.replace("key",key)
        self.webEngineView.page().runJavaScript(code)

    def clearIndicator(self):
        self.texEditor.clearIndicatorRange(self.pdf_tex_indicator[0],self.pdf_tex_indicator[1],\
            self.pdf_tex_indicator[2],self.pdf_tex_indicator[3],self.pdf_tex_indicator[4])
    
    def showVersions(self):
        
        self.mySubwindow=versionWindow(parent = self)
        self.mySubwindow.createWindow(640,400)
        self.mySubwindow.show()
        '''
        self.mySubwindow=queryWindow(parent = self)
        self.mySubwindow.createWindow(640,400)
        self.mySubwindow.show()
        '''

    def _showAbout(self)    :
         QMessageBox.about(self, "About", "This is a latex editor created by Abhijith (abhijithbn@gmail.com). \
                \nIcons made by Freepik from www.flaticon.com")
    
    def _createMenuBar(self):
        self.menuBar = self.menuBar()
        self.setMenuBar(self.menuBar)
        
        self.fileMenu = QMenu("&File", self)
        self.menuBar.addMenu(self.fileMenu)

        self.editMenu = self.menuBar.addMenu("&Tools")
        self.helpMenu = self.menuBar.addMenu("&Help")
        

    
    def openPaxFile(self, recent = -1):
        #print(recent)
        if recent == -1 or recent == False:
            options = QFileDialog.Options()
            #options |= QFileDialog.DontUseNativeDialog
            fld = QFileDialog()
            fld.setFileMode(QFileDialog.ExistingFile)
            file, _ = fld.getOpenFileName(self,"Open Tex File", "","Latex Files (*.pax)", options=options)
        else:
            if not (os.path.isfile(recent)):
                return
            else:
                file = recent
        

        if file:
            self.file = file[0:len(file)-4]
            
           
            db = database()
            db.open()
            db.addrecent(file)
            db.close()

            
            

            with open(self.file + ".pax", 'r') as f:
                intext = f.read()

            #tex = intext.split("<<*#tex_seperator*#>>")
            self.setData(intext, file)
            #print(tex[3])

            
            curdir = os.getcwd().replace("\\","/")
            if (os.path.isfile(self.file + '.pdf')):
                self.webEngineView.load(QUrl(f"file:///{curdir}/resources/web/viewer.html?file={self.file}.pdf"))

            self.saveAction.setEnabled(True)
            self.viewVersions.setEnabled(True)
            self.selectedTex.setEnabled(True)
            self.selectedPDF.setEnabled(True)
            self.openfolder.setEnabled(True)
            self.createDraft.setEnabled(True)
            self.compileAction.setEnabled(True)


    def savePaxFile(self):
        if self.file == '':
            self.savePaxFileAs()
            return

        
        tex = self.texEditor.text().replace('\r','')
     
   

        
        bib=self.bibEditor.text().replace('\r','')
        
        
        pkg = self.pkgEditor.text().replace('\r','')

        
        
       
       
        outtext = tex + " <<*#tex_seperator*#>>" + bib + " <<*#tex_seperator*#>>"  + pkg + " <<*#tex_seperator*#>>"  \
            + self.doc_class + " <<*#tex_seperator*#>>"+ self.bibsyle  + " <<*#tex_seperator*#>>" + \
            self.doc_params  + " <<*#tex_seperator*#>>" + self.toCopy + ' '

        f = open(self.file +".pax", "w")
        
        f.write(outtext)
        f.close()
        
        #self.updateVersion()

    
    
    def savePaxFileAs(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fld = QFileDialog()
        fld.setFileMode(QFileDialog.ExistingFile)
        file, _ = fld.getSaveFileName(self,"Save Tex File", "","Latex Files (*.pax)", options=options)
        if file:
            tex = self.texEditor.text().replace('\r','')

            bib=self.bibEditor.text().replace('\r','')
            
            pkg = self.pkgEditor.text().replace('\r','')

            outtext = tex + " <<*#tex_seperator*#>>" + bib + " <<*#tex_seperator*#>>"  + pkg + " <<*#tex_seperator*#>>"  \
            + self.doc_class + " <<*#tex_seperator*#>>"+ self.bibsyle  + " <<*#tex_seperator*#>>" + \
            self.doc_params  + " <<*#tex_seperator*#>>" + self.toCopy + ' '

            f = open(self.file +".pax", "w")
            
            f.write(outtext)
            f.close()
            
            #self.updateVersion()

    def updateVersion(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter text:')
        if ok:
            comment = str(text)
        else:
            return
        
        tex = self.texEditor.text().replace('\r','')
        
        bib=self.bibEditor.text().replace('\r','')
        
        pkg = self.pkgEditor.text().replace('\r','')
       
        outtext = tex + " <<*#tex_seperator*#>>" + bib + " <<*#tex_seperator*#>>"  + pkg + " <<*#tex_seperator*#>>"  \
            + self.doc_class + " <<*#tex_seperator*#>>"+ self.bibsyle  + " <<*#tex_seperator*#>>" + \
            self.doc_params  + " <<*#tex_seperator*#>>" + self.toCopy + ' '

        db = database();
            
        db.open()
        
        ver_fname = db.create_version(self.file, comment)
        db.close()
        var_fname = 'resources/texversions/'+ ver_fname

        if not (os.path.isfile('resources/texversions/')):
            os.mkdir('resources/texversions/')
            
        f = open(var_fname +".pax", "w")
        f.write(outtext)
        f.close()
        
        logging.debug(f"Created{var_fname}")
        self.original_text_tex = self.texEditor.text()
        self.original_text_bib = self.bibEditor.text()
        self.original_text_pkg = self.pkgEditor.text()
        self.labelStatus.setText("Created verion " + var_fname)







if __name__ == '__main__':

    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = EditorMainWindow()

    sys.exit(app.exec_())

