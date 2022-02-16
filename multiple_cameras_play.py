from __future__ import absolute_import, division, print_function

from typing import Dict, List, Any
from collections import OrderedDict
from functools import partial
import numpy as np
import cv2
import os

from PyQt5.QtWidgets import (QWidget, QDialog, QLabel, QGridLayout, QVBoxLayout, QSizePolicy, QApplication)
from PyQt5.QtCore import (QThread, pyqtSignal, pyqtSlot, QSize, Qt, QTimer, QTime, QDate, QObject, QEvent)
from PyQt5.QtGui import (QImage, QPixmap, QFont, QIcon)

os.environ['OPENCV_VIDEOIO_DEBUG'] = '1'
os.environ['OPENCV_VIDEOIO_PRIOROTY_MSMF'] = '0'

#QLabel Display
width,height=480*6,270*6
w=1920//2
h=1080//2
capture_delay=80

###____________

class Slot(QThread):
    signal = pyqtSignal(np.ndarray, int, int, bool)

    def __init__(self, parent: QWidget, index:int, cam_id:int, link: str) -> None:
        QThread.__init__(self, parent)
        self.parent = parent
        self.index = index
        self.cam_id = cam_id
        self.link = link

    def run(self) -> None:
        cap = cv2.VideoCapture(self.link)
        while cap.isOpened():
            has, im = cap.read()
            if not has: break
            im = cv2.resize(im,(w,h))
            self.signal.emit(im, self.index,self.cam_id, True)
            cv2.waitKey(capture_delay) & 0xFF

        im = np.zeros((h,w,3),dtype=np.uint8)
        self.signal.emit(im, self.index,self.cam_id,False)
        cv2.waitKey(capture_delay) & 0xFF


def clickable(widget):
    class Filter(QObject):
        clicked= pyqtSignal()
        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    self.clicked.emit()
                    return True
            return False
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

class NewWindow(QDialog):
    def __init__(self,parent: QWidget) -> None:
        QDialog.__init__(self, parent)
        self.parent = parent
        self.index: int = 0

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.label.setScaledContents(True)
        self.label.setFont(QFont("Times", 10))
        self.label.setStyleSheet(
            "color: rgb(255,0,255);"
            "background-color: rgb(0,0,0);"
            "qproperty-alignment: AligenCenter;")
        layout= QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        # layout.setSpacing(2)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowTitle('Camera {}'.format(self.index))

    def sizeHint(self) ->QSize:
        return QSize(width//3,height//3)
    def resizeEvent(self, event) -> None:
        self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.key_Escape:
            self.accept()
###___________________
class Window(QWidget):
    def __init__(self, cams: Dict[int, str]) -> None:
        super(Window, self).__init__()
        # initilize the cameras with emety values

        self.cameras: Dict[int, List[Any]] = OrderedDict()
        index: int
        for index in range(len(cams.keys())):
            self.cameras[index]=[None,None,False]
        index=0
        for cam_id, link in cams.items():
            self.cameras[index]=[cam_id,link,False]
            index += 1

        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)

        self.labels: List[QLabel] = []
        self.threads: List[Slot] = []
        for index, value in self.cameras.items():
            cam_id,link,active = value

            slot = Slot(self, index, cam_id, link)
            slot.signal.connect(self.ReadImage)
            self.threads.append(slot)

            label = QLabel()
            label.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
            label.setScaledContents(True)
            label.setFont(QFont("Times", 10))
            label.setStyleSheet(
                "color: rgb(255,0,255); background-color: rgb(0,0,0);"
                "qproperty-alignment: AligenCenter;")

            clickable(label).connect(partial(self.showCam, index))
            self.labels.append(label)

            if index ==0:
                layout.addWidget(label,0,0)
            elif index ==1:
                layout.addWidget(label,0,1)
            elif index ==2:
                layout.addWidget(label,0,2)
            elif index ==3:
                layout.addWidget(label,0,3)

            elif index ==4:
                layout.addWidget(label,1,0)
            elif index ==5:
                layout.addWidget(label,1,1)
            elif index ==6:
                layout.addWidget(label,1,2)
            elif index ==7:
                layout.addWidget(label,1,3)

            elif index ==8:
                layout.addWidget(label,2,0)
            elif index ==9:
                layout.addWidget(label,2,1)
            elif index ==10:
                layout.addWidget(label,2,2)
            elif index ==11:
                layout.addWidget(label,2,3)

            elif index ==12:
                layout.addWidget(label,3,0)
            elif index ==13:
                layout.addWidget(label,3,1)
            elif index ==14:
                layout.addWidget(label,3,2)
            elif index ==15:
                layout.addWidget(label,3,3)

            else:
                raise ValueError("n Cameras != rows/cols")

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1) #1000= 1s
        self.showTime()

        # timer_th = QTimer(self)
        # timer_th.timeout.connect(self.refresh)
        # timer_th.start(60000*60*3) # 3 h

        self.setLayout(layout)
        self.setWindowTitle('CCTV')
        self.setWindowIcon(QIcon('icon.png'))

        self.newWindow = NewWindow(self)

        self.refresh()

    def sizeHint(self) ->QSize:
        return QSize(width,height)

    def resizeEvent(self, event) -> None:
        self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.keyEscape:
            self.close()

    def closeEvent(self, event): pass

    def showCam(self,index: any) -> None:
        self.newWindow.index = index
        if not self.cameras[index][2]:
            text_ = "Camera {}\n not active!".format(self.cameras[index][0])
            self.newWindow.label.setText(text_)
        self.newWindow.setWindowTitle("Camera {}".format(self.cameras[index][0]))
        self.newWindow.show()

    def showTime(self) -> None:
        time = QTime.currentTime()
        textTime=time.toString('hh:mm:ss')

        date = QDate.currentDate()
        textDate = date.toString('ddd, mmmm,d')

        text = '{}\n{}'.format(textTime, textDate)

        for index, value in self.cameras.items():
            cam_id, link, active = value
            if not active:
                text_ ='Camera {}\n'.format(cam_id) + text
                self.labels[index].setText(text_)

    @pyqtSlot(np.ndarray, int, int, bool)
    def ReadImage(self, im: np.ndarray, index: int, cam_id: int, active:bool) -> None:
        self.cameras[index][2] = active
        cam_id, link, active = self.cameras[index]

        im = QImage(im.data, im.shape[1],im.shape[0],QImage.Format_RGB888).rgbSwapped()
        self.labels[index].setPixmap(QPixmap.fromImage(im))

        if index == self.newWindow.index:
            self.newWindow.label.setPixmap(QPixmap.fromImage(im))

    def refresh(self) -> None:
        for slot in self.threads:
            slot.start()
if __name__=='__main__':
    import sys
    cams : Dict[int, Any] = OrderedDict()
    cams[1] = 0
    cams[2] = "G:\Perput\Python_API/videos/t1.mp4"
    cams[3] = "G:\Perput\Python_API/videos/t2.mp4"
    cams[4] = "G:\Perput\Python_API/videos/t3.mp4"
    cams[5] = 'G:\Perput\Python_API/videos/t4.mp4'
    cams[6] = "G:\Perput\Python_API/videos/t5.mp4"
    cams[7] = "G:\Perput\Python_API/videos/t6.mp4"
    cams[8] = "G:\Perput\Python_API/videos/t7.mp4"
    cams[9] = "G:\Perput\Python_API/videos/t8.mp4"
    cams[10] = "G:\Perput\Python_API/videos/t9.mp4"
    cams[11] = "G:\Perput\Python_API/videos/t10.mp4"
    cams[12] = "G:\Perput\Python_API/videos/t11.mp4"
    cams[13] = "G:\Perput\Python_API/videos/t12.mp4"
    cams[14] = "G:\Perput\Python_API/videos/t13.mp4"
    cams[15] = "G:\Perput\Python_API/videos/t14.mp4"
    cams[16] = "G:\Perput\Python_API/videos/t15.mp4"

    app = QApplication(sys.argv)
    win = Window(cams=cams)
    win.show()
    sys.exit(app.exec_())
