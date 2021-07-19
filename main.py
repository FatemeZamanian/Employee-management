# This Python file uses the following encoding: utf-8
import sys
from functools import partial

from PyQt5.QtGui import QImage
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import *
from PySide6.QtCore import QThread, Signal, QDir
from database import Database
import cv2

def convertCVImage2QtImage(cv_img):
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    height, width, channel = cv_img.shape
    bytesPerLine = 3 * width
    qimg = QImage(cv_img.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)

class Camera(QThread):
    set_camera_signal = Signal(object)

    def __init__(self):
        super(Camera, self).__init__()

    def run(self):
        self.video = cv2.VideoCapture(0)

        face_detector = cv2.CascadeClassifier('fd.xml')
        while True:
            valid, self.frame = self.video.read()
            if valid is not True:
                break
            frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(frame_gray, 3.1)

            for face in faces:
                x, y, w, h = face
                image_face = self.frame[y:y + h, x:x + w]
                org_checkered = cv2.resize(image_face, (0, 0), fx=0.1, fy=0.1, interpolation=cv2.INTER_LINEAR)
                resized_checkered = cv2.resize(org_checkered, (w, h), interpolation=cv2.INTER_NEAREST)
                self.frame[y:y + h, x:x + w] = resized_checkered
            self.set_camera_signal.emit(self.frame)
            cv2.waitKey(30)

    def stop(self):
        try:
            self.video.release()
        except:
            pass





class MessageBox(QWidget):
    def __init__(self):
        super(MessageBox, self).__init__()
        loader = QUiLoader()
        self.ui = loader.load("form.ui")
        self.Addui = loader.load("Addform.ui")
        self.cameraui = loader.load("pictureform.ui")
        self.editui=loader.load("Editform.ui")
        self.ui.show()
        self.readInfo()
        self.ui.btn_Add.clicked.connect(self.openAdd)
        self.thread_cameras = Camera()
        self.thread_cameras.set_camera_signal.connect(self.show_e)


    def readInfo(self):
        for i in reversed(range(self.ui.gl_info.count())):
            self.ui.gl_info.itemAt(i).widget().setParent(None)
        infos = Database.select()
        for i, info in enumerate(infos):
            label = QLabel()
            label.setText(info[2] + '  ' + info[3])
            label.setFixedHeight(25)
            self.ui.gl_info.addWidget(label, i, 0)
            # labell = QLabel()
            # pixmap = QPixmap(info[5])
            # labell.setPixmap(pixmap)
            # labell.setFixedHeight(25)
            # self.ui.gl_info.addWidget(labell, i, 1)
            btn = QPushButton()
            btn.setMinimumSize(25, 25)
            btn.setMaximumSize(25, 25)
            btn.clicked.connect(partial(self.openEdite,i))
            btn.setText("Edit")
            btn.setFixedHeight(25)
            self.ui.gl_info.addWidget(btn, i, 1)


    def openAdd(self):
        self.Addui.show()
        self.Addui.btnAdd.clicked.connect(self.addNewEmployee)
        self.Addui.btn_pic.clicked.connect(self.run_cameras)
        self.Addui.btn_pic.clicked.connect(self.getPicture)

    def getPicture(self):
        self.cameraui.show()


    def run_cameras(self):
        self.thread_cameras.start()



    def show_e(self,img):
        res_img = convertCVImage2QtImage(img)
        # self.cameraui.lbl00.setPixmap(res_img)
        # self.cameraui.fbtn_01.setIcon(res_img)

    def addNewEmployee(self):
        code=self.Addui.txt_codemelli.text()
        name = self.Addui.txt_name.text()
        family=self.Addui.txt_family.text()
        birthdate=self.Addui.txt_birthdate.text()
        image='eee'
        if name != "" and code != "" and family !="" and birthdate !="":
            res = Database.insert(code,name,family,birthdate,image)
            if res:
                label = QLabel()
                label.setText(name + ' ' + family)
                label.setFixedHeight(25)
                btn = QPushButton()
                btn.setMinimumSize(25,25)
                btn.setMaximumSize(25,25)
                btn.setText("Edit")

                infos = Database.select()
                for i in range(len(infos), 0, -1):
                    btn.clicked.connect(partial(self.openEdite,i))
                    self.ui.gl_info.addWidget(label, i, 0)
                    self.ui.gl_info.addWidget(btn, i, 1)
                    break
            else:
                msgBox = QMessageBox()
                msgBox.setText("DB Error")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setText("Error Fields are empty")
            msgBox.exec_()

    def openEdite(self,i):
        self.editui.show()
        infos = Database.select()
        ids = []
        for info in infos:
            ids.append({"id": info[0], "code": info[1], "name": info[2], "family": info[3], "birthdate": info[4]})
        temp = ids[i]
        self.editui.ecode.setText(str(temp["code"]))
        self.editui.ename.setText(temp["name"])
        self.editui.efamily.setText(temp["family"])
        self.editui.ebirthdate.setText(temp["birthdate"])
        self.editui.esave.clicked.connect(partial(self.edit,i))

    def edit(self,id):
        infos=Database.select()
        ids=[]
        for info in infos:
            ids.append({"id":info[0],"code":info[1],"name":info[2],"family":info[3],"birthdate":info[4]})
        temp=ids[id]
        code=self.editui.ecode.text()
        name=self.editui.ename.text()
        family=self.editui.efamily.text()
        birthdate=self.editui.ebirthdate.text()
        Database.edit(temp["id"],code,name,family,birthdate,'eee')
        self.readInfo()


if __name__ == "__main__":
    app = QApplication([])
    widget = MessageBox()
    sys.exit(app.exec_())
