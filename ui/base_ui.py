"""
Base UI - Pure Python UI class
main.ui o'rniga ishlatiladi
"""

from PyQt6 import QtCore, QtGui, QtWidgets

from ui.components.pages import (
    PageFace,
    PageHome,
    PageMain,
    PageNoInternet,
    PagePinfl,
    PageTest,
)


class Ui_MainWindow(object):
    """
    Pure Python UI class - generated_ui.py o'rniga
    Barcha sahifalar modular tarzda import qilinadi
    """

    def setupUi(self, MainWindow):
        """UI ni sozlash"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        MainWindow.resize(1365, 858)

        # Font
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("")

        # Central widget
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Main grid layout
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")

        # Stacked widget
        self.stack = QtWidgets.QStackedWidget(parent=self.centralwidget)
        self.stack.setAutoFillBackground(False)
        self.stack.setStyleSheet("""
            QStackedWidget#stack {
                background-image: url("resources/images/face_fon.jpg");
                background-repeat: no-repeat;
                background-position: center;
                background-origin: content;
            }
        """)
        self.stack.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.stack.setObjectName("stack")

        # ========== SAHIFALARNI YARATISH ==========

        # Page 0: Main (test tanlash)
        self.page_main = PageMain()
        self.stack.addWidget(self.page_main)

        # Page 1: Home (xodim yuz tekshiruvi)
        self.page_home = PageHome()
        self.stack.addWidget(self.page_home)

        # Page 2: PINFL (PINFL kiritish)
        self.page_pinfl = PagePinfl()
        self.stack.addWidget(self.page_pinfl)

        # Page 3: Face (nomzod yuz tekshiruvi)
        self.page_face = PageFace()
        self.stack.addWidget(self.page_face)

        # Page 4: Test (WebView)
        self.page_test = PageTest()
        self.stack.addWidget(self.page_test)

        # Page 5: No Internet
        self.page_no_internet = PageNoInternet()
        self.stack.addWidget(self.page_no_internet)

        # ========== SAHIFA ELEMENTLARIGA REFERENCE ==========
        # MainWindow dan to'g'ridan-to'g'ri foydalanish uchun

        # Page Main elements
        self.label_logo_2 = self.page_main.label_logo_2
        self.label_6 = self.page_main.label_6
        self.combo_choose_test = self.page_main.combo_choose_test
        self.btn_next_page = self.page_main.btn_next_page
        self.label_3 = self.page_main.label_3

        # Page Home elements
        self.label_org = self.page_home.label_org
        self.label_face = self.page_home.label_face
        self.label_9 = self.page_home.label_9
        self.label_response = self.page_home.label_response

        # Page PINFL elements
        self.label = self.page_pinfl.label
        self.input_pinfl = self.page_pinfl.input_pinfl
        self.btn_check_im = self.page_pinfl.btn_check_im
        self.label_4 = self.page_pinfl.label_4
        self.label_5 = self.page_pinfl.label_5
        self.label_10 = self.page_pinfl.label_10

        # Page Face elements
        self.label_face_check = self.page_face.label_face_check
        self.label_video_box = self.page_face.label_video_box
        self.label_result_face_candidate = self.page_face.label_result_face_candidate
        self.btn_candidate_next = self.page_face.btn_candidate_next

        # Page Test elements
        self.layout_test = self.page_test.layout_test

        # Page No Internet elements
        self.label_7 = self.page_no_internet.label_7
        self.label_8 = self.page_no_internet.label_8

        # ========== LAYOUT YAKUNLASH ==========

        self.gridLayout_4.addWidget(self.stack, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        # Translations
        self.retranslateUi(MainWindow)

        # Default page
        self.stack.setCurrentIndex(0)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """Tarjima (matnlarni o'rnatish)"""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Safe Browser"))

        # Matnlar allaqachon page classlarida o'rnatilgan
        # Bu method faqat backward compatibility uchun
