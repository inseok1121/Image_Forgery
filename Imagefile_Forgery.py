import sys
import exifread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PIL import Image


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(800, 200, 300, 300)
        self.setWindowTitle("Exif ver 1.0")
        self.resize(1610, 886)
        
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(20,90,500, 750)
        self.tableWidget.setColumnCount(2)
        
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setHighlightSections(True)
        self.tableWidget.verticalHeader().setMinimumSectionSize(100)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 350)      
        self.setTableWidgetData()

        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(550, 90, 500, 300)


        self.exifTable = QTableWidget(self)
        self.exifTable.setGeometry(550, 420, 500, 420)
        self.exifTable.setColumnCount(2)
        self.exifTable.horizontalHeader().setVisible(True)
        self.exifTable.verticalHeader().setVisible(True)
        self.exifTable.verticalHeader().setCascadingSectionResizes(False)
        self.exifTable.verticalHeader().setHighlightSections(True)
        self.exifTable.verticalHeader().setMinimumSectionSize(100)
        self.exifTable.setColumnWidth(0, 150)
        self.exifTable.setColumnWidth(1, 348)      
        self.setExifTableData()

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(1)
        
        self.tree.setGeometry(1080, 90, 500, 750)
        self.header = QTreeWidgetItem(["Group List"])
        self.tree.setHeaderItem(self.header)
        

        self.Button_Open = QPushButton(self)
        self.Button_Open.setObjectName("Button_Open")
        self.Button_Open.setText("File Open")
        self.Button_Group = QPushButton(self)
        self.Button_Group.setObjectName("Button_Grouping")
        self.Button_Group.setText("Grouping")


        self.Button_Open.setGeometry(20, 20, 100, 50)
        self.Button_Group.setGeometry(1450, 20, 100, 50)
        self.Button_Open.clicked.connect(self.pushButtonClicked)
        self.Button_Group.clicked.connect(self.process_Grouping)
        self.tableWidget.cellClicked.connect(self.viewEXIFInfo)


    def setTableWidgetData(self):
        column_headers = ['Name', 'Path']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

    def setExifTableData(self):
        column_headers = ['Key', 'Values']
        self.exifTable.setHorizontalHeaderLabels(column_headers)

    def pushButtonClicked(self):
        files = QFileDialog.getOpenFileNames(self,"Select one or more files to open","./","Images (*.png *.xpm *.jpg)");
    
        for fname in files[0]:
            num_row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(num_row)
            filename = fname.split('/')[-1]
            filepath = fname
            self.tableWidget.setItem(num_row, 0, QTableWidgetItem(filename))
            self.tableWidget.setItem(num_row, 1, QTableWidgetItem(filepath))
    
        
    def viewEXIFInfo(self, row, col):
        self.ClearExifTable()
        indexnum = row
        filepath = self.tableWidget.item(indexnum, 1)

        f = open(filepath.text(), 'rb')
        tags = exifread.process_file(f)
        num_row = 0
        for tag in tags.keys():
            ##if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            self.exifTable.insertRow(num_row)
            self.exifTable.setItem(num_row, 0, QTableWidgetItem(str(tag)))
            self.exifTable.setItem(num_row, 1, QTableWidgetItem(str(tags[tag])))
            num_row = num_row + 1

         
        pixmap = QPixmap(filepath.text())
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)

    def ClearExifTable(self):
        count_row = self.exifTable.rowCount()        
        for i in range(0, count_row):
            self.exifTable.removeRow(0)
    
    def process_Grouping(self):
        filename_Array = []
        fileinfo_Array = []
        
        file_count = self.tableWidget.rowCount()

        for i in range(0, file_count):
            filename_Array.append(self.tableWidget.item(i, 1).text())

        for filename in filename_Array:
            file_Dict = {}
            f = open(filename, 'rb')
            tags = exifread.process_file(f)
            
            file_Dict = {filename:tags}
            f.close()
            fileinfo_Array.append(file_Dict)


        groupinfo_Array = []
        for i in range(0, len(fileinfo_Array)):
            im = Image.open(list(fileinfo_Array[i].keys())[0])
            width, height = im.size
            for value in fileinfo_Array[i].values():
                if str(value.get('EXIF DateTimeOriginal')).strip() != str(value.get('Image DateTime')).strip() or str(value.get('EXIF DateTimeOriginal')).strip() != str(value.get('EXIF DateTimeDigitized')).strip() or str(value.get('EXIF DateTimeDigitized')).strip() != str(value.get('Image DateTime')).strip():
                    temp = {list(fileinfo_Array[i].keys())[0] : "1"}
                    groupinfo_Array.append(temp)
                elif str(value.get('EXIF ExifImageWidth')).strip() != str(width) or str(value.get('EXIF ExifImageLength')).strip() != str(height):                   
                    temp = {list(fileinfo_Array[i].keys())[0] : "2"}
                    groupinfo_Array.append(temp)
                else:
                    temp = {list(fileinfo_Array[i].keys())[0] : "0"}
                    groupinfo_Array.append(temp)

        self.DiffTime = QTreeWidgetItem(self.tree)
        self.DiffTime.setText(0, "Diff Time")
        self.DiffTime.setFlags(Qt.ItemIsEnabled)

        self.DiffSize = QTreeWidgetItem(self.tree)
        self.DiffSize.setText(0, "Diff Size")
        self.DiffSize.setFlags(Qt.ItemIsEnabled)

        self.normal = QTreeWidgetItem(self.tree)
        self.normal.setText(0, "Original")
        self.normal.setFlags(Qt.ItemIsEnabled)

        for i in range(0, len(groupinfo_Array)):
            if list(groupinfo_Array[i].values())[0] == '0':
                self.itemWidget = QTreeWidgetItem(self.normal, 1)
                self.itemWidget.setText(0, list(groupinfo_Array[i].keys())[0].split('/')[-1])
            if list(groupinfo_Array[i].values())[0] == '1':
                self.itemWidget = QTreeWidgetItem(self.DiffTime, 1)
                self.itemWidget.setText(0, list(groupinfo_Array[i].keys())[0].split('/')[-1])
            if list(groupinfo_Array[i].values())[0] == '2':
                self.itemWidget = QTreeWidgetItem(self.DiffSize, 1)
                self.itemWidget.setText(0, list(groupinfo_Array[i].keys())[0].split('/')[-1])
        self.tree.expandAll()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()