from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCustom
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import re
class LatexEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8
    ident_key_list = ['\\section','\\chapter','\\begin','\\subsection','\\subsubsection','\\subsubsubsection']
    unident_key_list = ['\\end']
    bgcolor = 'darkslategray'
    clicked = pyqtSignal()

    prevkey = None
    curkey = None

    def __init__(self, parent=None, bc = '#303841', type = 'tex'):
        super(LatexEditor, self).__init__(parent)

        # Set the default font
        font = QFont()

        font.setFamily('Consolas')
        #font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("blue"),
            self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        #self.setCaretLineVisible(True)
        #self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        
        self.setCaretWidth(2)
        # Set Python lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        #

        #lexer = QsciLexerPython()
        

        text = bytearray(str.encode("Times New Roman"))

        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, text)

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # not too small
        #self.setMinimumSize(600, 450)

        self.setTheme(bc, type)


        

    def mousePressEvent(self, event):
        self.clicked.emit()
        QsciScintilla.mousePressEvent(self, event)

    def setTheme(editor, bc , type):
        
        #editor.textChanged.connect(lambda: func(editor))
        editor.setTabWidth(4);
        #editor.setMarginWidth(0,'0000');
        editor.setMarginWidth(1,20);


        font = QFont()

        font.setFamily('Consolas')
        #font.setFixedPitch(True)
        font.setPointSize(14)
        if type=='tex':
            lexer = ConfigTexLexer(editor)
        elif type=='bib':
            lexer = ConfigBibLexer(editor)
        lexer.setDefaultFont(font)
        lexer.bgcolor = bc
        editor.setLexer(lexer)

        editor.bgcolor = 'white'
        editor.setCaretForegroundColor(QColor('white'))
        editor.setMargins(3)

        editor.setFoldMarginColors(QColor('darkslategray'),QColor(bc))
        editor.setMarginsForegroundColor(QColor('gray'))


        editor.setMarginsBackgroundColor(QColor(bc));
        editor.setAutoIndent(True)
        editor.setFolding(True)
        editor.SendScintilla(editor.SCI_STYLESETBACK, editor.STYLE_DEFAULT, QColor(bc));
        editor.setWrapMode(True)
        editor.setWrapIndentMode(True)
        
    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)
     
        
class ConfigTexLexer(QsciLexerCustom):
     bgcolor = ''
     def __init__(self, parent):
         QsciLexerCustom.__init__(self, parent)
         self._styles = {
             0: 'Default',
             1: 'Comment',
             2: 'Section',
             3: 'Key',
             4: 'Assignment',
             5: 'Value',
             6: 'Cite',
             7: 'Graphics',
             8: 'DollarEqn',
             9: 'Reference',

             }
         for key,value in self._styles.items():
             setattr(self, value, key)
         self._foldcompact = True

         self.setPaper(QColor("#ffffff"), 10)   # Style 10: white
         self.setColor(QColor("#000000"), 10)   # Style 10: black

         editor = self.parent()
         editor.SendScintilla(editor.SCI_STYLESETHOTSPOT, 1, True)

     def foldCompact(self):
         return self._foldcompact

     def setFoldCompact(self, enable):
         self._foldcompact = bool(enable)

     def language(self):
         return 'Latex'

     def description(self, style):
         return self._styles.get(style, '')

     def defaultColor(self, style):
         if style == self.Default:
             return QColor('white')
         elif style == self.Comment:
             return QColor('#A0A0A0')
         elif style == self.Section:
             return QColor('yellow')
         elif style == self.Key:
             return QColor('yellow')
         elif style == self.Assignment:
             return QColor('#CC0000')
         elif style == self.Cite:
             return QColor('#00CC00')
         elif style == self.Graphics:
             return QColor('red')
         elif style == self.DollarEqn:
             return QColor('magenta')
         elif style == self.Reference:
             return QColor('cyan')
         elif style == 10:
             return QColor(QColor('black'))
             
         return QsciLexerCustom.defaultColor(self, style)

     def defaultPaper(self, style):
         if style == 10:
            return QColor("white")

         return  QColor(self.bgcolor)

     def defaultEolFill(self, style):
         if style == self.Section:
             return True
         return QsciLexerCustom.defaultEolFill(self, style)

     def defaultFont(self, style):
         if style == self.Comment:
             if sys.platform in ('win64','win32', 'cygwin'):
                 return QFont('Comic Sans MS', 10)
             return QFont('Bitstream Vera Serif', 10)
         if not style == self.Default:
            font = QsciLexerCustom.defaultFont(self, style)
            font.setBold( QFont.Bold)
            return font
             
         
         return QsciLexerCustom.defaultFont(self, style)

     def styleText(self, start, end):
         editor = self.editor()

         
        
         if editor is None:
             return

         SCI = editor.SendScintilla
         GETFOLDLEVEL = QsciScintilla.SCI_GETFOLDLEVEL
         SETFOLDLEVEL = QsciScintilla.SCI_SETFOLDLEVEL
         HEADERFLAG = QsciScintilla.SC_FOLDLEVELHEADERFLAG
         LEVELBASE = QsciScintilla.SC_FOLDLEVELBASE
         NUMBERMASK = QsciScintilla.SC_FOLDLEVELNUMBERMASK
         WHITEFLAG = QsciScintilla.SC_FOLDLEVELWHITEFLAG
         set_style = self.setStyling

         source = ''
         if end > editor.length():
             end = editor.length()
         if end > start:
             source = bytearray(end - start)
             SCI(QsciScintilla.SCI_GETTEXTRANGE, start, end, source)
         if not source:
             return

         compact = self.foldCompact()

         index = SCI(QsciScintilla.SCI_LINEFROMPOSITION, start)
         if index > 0:
             pos = SCI(QsciScintilla.SCI_GETLINEENDPOSITION, index - 1)
             state = SCI(QsciScintilla.SCI_GETSTYLEAT, pos)
         else:
             state = self.Default
         state1 = self.Default
         self.startStyling(start, 0x1f)
         cnt = 0;
         for or_line in source.splitlines(True):
             cnt = cnt + 1
             or_length = len(or_line)
             line = or_line.strip()
             length = len(line)
             whitespace = False
             state = self.Default
             pos = 0
             tp = 0
             if or_length == 1:
                whitespace = True
                state = self.Default
             elif length>0:
                 whitespace = False
                 
                 if line.startswith(b'%[-A'):
                    state = self.Section
                    
                 elif line.startswith(b'%'):
                    
                    state = self.Comment
                
                 elif line.startswith(b'\\section'):
                    state = self.Section
                    
                 elif line.startswith(b'\\begin'):
                    state = self.Key
                 
                 
                 elif line.startswith(b'\\end'):
                    state = self.Key
                 elif line.startswith(b'\\chapter'):
                    state = self.Key

                 elif line.startswith(b'\\subsection'):
                    state = self.Key
                    
                 elif line.startswith(b'\\subsubsection'):
                    state = self.Key
                 elif line.startswith(b'\\subsubsubsection'):
                    state = self.Key
                 
                 

                 
              

                 pos = or_line.find(b'\\absract')>-1  or or_line.find(b'\\title')>-1  or or_line.find(b'\\author')>-1  or  or_line.find(b'\\includegraphics')>-1  or or_line.find(b'\\label')>-1

                 pos1 =  or_line.find(b'\\caption')>-1 or or_line.find(b'\\centering')>-1

                 pos2 =  or_line.find(b'\\cite') > -1 or or_line.find(b'\\ref')>0 or or_line.find(b'$')>-1

                 if(pos):
                    pos = [(m.start(0), m.end(0)-m.start(0)) for m in re.finditer(r"(?:\\author|\\title|\\abstract|\\includegraphics|\\label|\{(.*?)\})", or_line.decode('utf-8'))]
                    
                    
                    pre = 0
                    for p in range(len(pos)):

                         set_style(pos[p][0] - pre , state)
                         set_style(pos[p][1], self.Graphics)
                         pre = pos[p][0] + pos[p][1]
                    or_length = or_length - pos[p][0] - pos[p][1]
                 elif (pos1):
                    pos = [(m.start(0), m.end(0)-m.start(0)) for m in re.finditer(r"(?:\\caption|\\centering)", or_line.decode('utf-8'))]
                    
                    
                    pre = 0
                    for p in range(len(pos)):
                         set_style(pos[p][0] - pre , state)
                         set_style(pos[p][1], self.Graphics)
                         pre = pos[p][0] + pos[p][1]
                    or_length = or_length - pos[p][0] - pos[p][1]
                 elif pos2:
                    pos = [(m.start(0), m.end(0)-m.start(0), m.group()) for m in re.finditer(r"(?:\\cite\{(.*?)\}|\\ref\{(.*?)\}|\$(.*?)\$)", or_line.decode('utf-8'))]
                    
                    
                    pre = 0
                    if(len(pos)>0):
                        for p in range(len(pos)):
                             locState = self.Cite
                             if(pos[p][2].startswith('$')):
                                locState = self.DollarEqn
                             elif (pos[p][2].startswith('\\ref')):
                                locState = self.Reference

                             set_style(pos[p][0] - pre , state)
                             set_style(pos[p][1], locState)
                             pre = pos[p][0] + pos[p][1]
                        or_length = or_length - pos[p][0] - pos[p][1]





                 '''
                 if(pos>0):
                     pos = [i for i in range(len(or_line)) if or_line.startswith(b'\\cite', i)]
                     print(pos)
                     pre = 0
                     for p in range(len(pos)):
                         set_style(pos[p] - pre , state)
                         set_style(5, self.Cite)
                         pre = pos[p] + 5
                     
                     or_length = or_length - pos[p] - 5
                 '''


                 
                

                 

  
                 
             set_style(or_length, state)

             if state == self.Section:
                 
                 level = LEVELBASE | HEADERFLAG
             
             elif index > 0:
                 lastlevel = SCI(GETFOLDLEVEL, index - 1)
                 if lastlevel & HEADERFLAG:
                     level = LEVELBASE + 1
                 else:
                     level = lastlevel & NUMBERMASK
            
             else:
                 level = LEVELBASE
            
             if whitespace:
                 level |= WHITEFLAG
             if level != SCI(GETFOLDLEVEL, index):
                 SCI(SETFOLDLEVEL, index, level)
          
             index += 1


         if index > 0:
             lastlevel = SCI(GETFOLDLEVEL, index - 1)
             if lastlevel & HEADERFLAG:
                 level = LEVELBASE + 1
             else:
                 level = lastlevel & NUMBERMASK
         else:
             level = LEVELBASE
            

         lastlevel = SCI(GETFOLDLEVEL, index)
         SCI(SETFOLDLEVEL, index, level | lastlevel & ~NUMBERMASK)
         
class ConfigBibLexer(QsciLexerCustom):
     def __init__(self, parent):
         QsciLexerCustom.__init__(self, parent)
         self._styles = {
             0: 'Default',
             1: 'Comment',
             2: 'Section',
             3: 'Key',
             4: 'Assignment',
             5: 'Value',
             6: 'Cite',
             7: 'Graphics',
             8: 'DollarEqn',
             9: 'Reference',
             }
         for key,value in self._styles.items():
             setattr(self, value, key)
         self._foldcompact = True

     def foldCompact(self):
         return self._foldcompact

     def setFoldCompact(self, enable):
         self._foldcompact = bool(enable)

     def language(self):
         return 'Latex'

     def description(self, style):
         return self._styles.get(style, '')

     def defaultColor(self, style):
         if style == self.Default:
             return QColor('white')
         elif style == self.Comment:
             return QColor('#A0A0A0')
         elif style == self.Section:
             return QColor('yellow')
         elif style == self.Key:
             return QColor('yellow')
         elif style == self.Assignment:
             return QColor('#CC0000')
         elif style == self.Cite:
             return QColor('#00CC00')
         elif style == self.Graphics:
             return QColor('red')
         elif style == self.DollarEqn:
             return QColor('magenta')
         elif style == self.Reference:
             return QColor('cyan')
             
         return QsciLexerCustom.defaultColor(self, style)

     def defaultPaper(self, style):
         
         return  QColor(self.bgcolor)

     def defaultEolFill(self, style):
         if style == self.Section:
             return True
         return QsciLexerCustom.defaultEolFill(self, style)

     def defaultFont(self, style):
         if style == self.Comment:
             if sys.platform in ('win64','win32', 'cygwin'):
                 return QFont('Comic Sans MS', 10)
             return QFont('Bitstream Vera Serif', 10)
         if not style == self.Default:
            font = QsciLexerCustom.defaultFont(self, style)
            font.setBold( QFont.Bold)
            return font
             
         
         return QsciLexerCustom.defaultFont(self, style)

     def styleText(self, start, end):
         editor = self.editor()

         
        
         if editor is None:
             return

         SCI = editor.SendScintilla
         GETFOLDLEVEL = QsciScintilla.SCI_GETFOLDLEVEL
         SETFOLDLEVEL = QsciScintilla.SCI_SETFOLDLEVEL
         HEADERFLAG = QsciScintilla.SC_FOLDLEVELHEADERFLAG
         LEVELBASE = QsciScintilla.SC_FOLDLEVELBASE
         NUMBERMASK = QsciScintilla.SC_FOLDLEVELNUMBERMASK
         WHITEFLAG = QsciScintilla.SC_FOLDLEVELWHITEFLAG
         set_style = self.setStyling

         source = ''
         if end > editor.length():
             end = editor.length()
         if end > start:
             source = bytearray(end - start)
             SCI(QsciScintilla.SCI_GETTEXTRANGE, start, end, source)
         if not source:
             return

         compact = self.foldCompact()

         index = SCI(QsciScintilla.SCI_LINEFROMPOSITION, start)
         if index > 0:
             pos = SCI(QsciScintilla.SCI_GETLINEENDPOSITION, index - 1)
             state = SCI(QsciScintilla.SCI_GETSTYLEAT, pos)
         else:
             state = self.Default
         state1 = self.Default
         self.startStyling(start, 0x1f)
         cnt = 0;
         for or_line in source.splitlines(True):
             cnt = cnt + 1
             or_length = len(or_line)
             line = or_line.strip()
             length = len(line)
             whitespace = False
             state = self.Default
             pos = 0
             tp = 0
             if or_length == 1:
                whitespace = True
                state = self.Default
             elif length>0:
                 whitespace = False
                 
                 if line.startswith(b'@ARTICLE'):
                    state = self.Section
                 elif line.startswith(b'@article'):
                    state = self.Section
                 elif line.startswith(b'@book'):
                    state = self.Section
                 elif line.startswith(b'@BOOK'):
                    state = self.Section
                 elif line.startswith(b'@INPROCEEDINGS'):
                    state = self.Section
                 elif line.startswith(b'@TECHREPORT'):
                    state = self.Section
                 
                 
                 

                 
              

                 pos =     or_line.find(b'\\includegraphics')>-1  or or_line.find(b'\\label')>-1

                 pos1 =  or_line.find(b'\\caption')>-1 or or_line.find(b'\\centering')>-1

                 pos2 =  or_line.find(b'\\cite') > -1 or or_line.find(b'\\ref')>0 or or_line.find(b'$')>-1

                 if(pos):
                    pos = [(m.start(0), m.end(0)-m.start(0)) for m in re.finditer(r"(?:\\includegraphics|\\label|\{(.*?)\})", or_line.decode('utf-8'))]
                    
                    
                    pre = 0
                    for p in range(len(pos)):

                         set_style(pos[p][0] - pre , state)
                         set_style(pos[p][1], self.Graphics)
                         pre = pos[p][0] + pos[p][1]
                    or_length = or_length - pos[p][0] - pos[p][1]
                 elif (pos1):
                    pos = [(m.start(0), m.end(0)-m.start(0)) for m in re.finditer(r"(?:\\caption|\\centering)", or_line.decode('utf-8'))]
                    
                    
                    pre = 0
                    for p in range(len(pos)):
                         set_style(pos[p][0] - pre , state)
                         set_style(pos[p][1], self.Graphics)
                         pre = pos[p][0] + pos[p][1]
                    or_length = or_length - pos[p][0] - pos[p][1]
                 elif pos2:
                    pos = [(m.start(0), m.end(0)-m.start(0), m.group()) for m in re.finditer(r"(?:\\cite\{(.*?)\}|\\ref\{(.*?)\}|\$(.*?)\$)", or_line.decode('utf-8'))]
                    
                    
                    pre = 0
                    if(len(pos)>0):
                        for p in range(len(pos)):
                             locState = self.Cite
                             if(pos[p][2].startswith('$')):
                                locState = self.DollarEqn
                             elif (pos[p][2].startswith('\\ref')):
                                locState = self.Reference

                             set_style(pos[p][0] - pre , state)
                             set_style(pos[p][1], locState)
                             pre = pos[p][0] + pos[p][1]
                        or_length = or_length - pos[p][0] - pos[p][1]





                 '''
                 if(pos>0):
                     pos = [i for i in range(len(or_line)) if or_line.startswith(b'\\cite', i)]
                     print(pos)
                     pre = 0
                     for p in range(len(pos)):
                         set_style(pos[p] - pre , state)
                         set_style(5, self.Cite)
                         pre = pos[p] + 5
                     
                     or_length = or_length - pos[p] - 5
                 '''


                 
                

                 

  
                 
             set_style(or_length, state)

             if state == self.Section:
                 
                 level = LEVELBASE | HEADERFLAG
             
             elif index > 0:
                 lastlevel = SCI(GETFOLDLEVEL, index - 1)
                 if lastlevel & HEADERFLAG:
                     level = LEVELBASE + 1
                 else:
                     level = lastlevel & NUMBERMASK
            
             else:
                 level = LEVELBASE
            
             if whitespace:
                 level |= WHITEFLAG
             if level != SCI(GETFOLDLEVEL, index):
                 SCI(SETFOLDLEVEL, index, level)
          
             index += 1


         if index > 0:
             lastlevel = SCI(GETFOLDLEVEL, index - 1)
             if lastlevel & HEADERFLAG:
                 level = LEVELBASE + 1
             else:
                 level = lastlevel & NUMBERMASK
         else:
             level = LEVELBASE
            

         lastlevel = SCI(GETFOLDLEVEL, index)
         SCI(SETFOLDLEVEL, index, level | lastlevel & ~NUMBERMASK)
         