# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.setWindowModality(Qt.WindowModality.WindowModal)
        Widget.resize(700, 400)
        Widget.setAutoFillBackground(False)
        self.verticalLayoutMain = QVBoxLayout(Widget)
        self.verticalLayoutMain.setObjectName(u"verticalLayoutMain")
        self.topLayout = QHBoxLayout()
        self.topLayout.setObjectName(u"topLayout")
        self.layoutCustomer = QVBoxLayout()
        self.layoutCustomer.setObjectName(u"layoutCustomer")
        self.layoutCustomerAvatar = QVBoxLayout()
        self.layoutCustomerAvatar.setObjectName(u"layoutCustomerAvatar")
        self.horizontalLayoutCustomerAvatar = QHBoxLayout()
        self.horizontalLayoutCustomerAvatar.setObjectName(u"horizontalLayoutCustomerAvatar")
        self.spacerLeftCustomer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutCustomerAvatar.addItem(self.spacerLeftCustomer)

        self.labelCustomerAvatar = QLabel(Widget)
        self.labelCustomerAvatar.setObjectName(u"labelCustomerAvatar")
        self.labelCustomerAvatar.setMinimumSize(QSize(50, 50))
        self.labelCustomerAvatar.setMaximumSize(QSize(50, 50))
        self.labelCustomerAvatar.setPixmap(QPixmap(u"avatar.png"))
        self.labelCustomerAvatar.setScaledContents(True)
        self.labelCustomerAvatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutCustomerAvatar.addWidget(self.labelCustomerAvatar)

        self.spacerRightCustomer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutCustomerAvatar.addItem(self.spacerRightCustomer)


        self.layoutCustomerAvatar.addLayout(self.horizontalLayoutCustomerAvatar)


        self.layoutCustomer.addLayout(self.layoutCustomerAvatar)

        self.labelCustomerText = QLabel(Widget)
        self.labelCustomerText.setObjectName(u"labelCustomerText")
        self.labelCustomerText.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.layoutCustomer.addWidget(self.labelCustomerText)

        self.comboCustomerLang = QComboBox(Widget)
        self.comboCustomerLang.addItem("")
        self.comboCustomerLang.addItem("")
        self.comboCustomerLang.addItem("")
        self.comboCustomerLang.setObjectName(u"comboCustomerLang")
        self.comboCustomerLang.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.comboCustomerLang.setCurrentText(u"Japanese")

        self.layoutCustomer.addWidget(self.comboCustomerLang)


        self.topLayout.addLayout(self.layoutCustomer)

        self.layoutMic = QVBoxLayout()
        self.layoutMic.setObjectName(u"layoutMic")
        self.layoutMicInner = QVBoxLayout()
        self.layoutMicInner.setObjectName(u"layoutMicInner")
        self.horizontalLayoutMic = QHBoxLayout()
        self.horizontalLayoutMic.setObjectName(u"horizontalLayoutMic")
        self.spacerLeftMic = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutMic.addItem(self.spacerLeftMic)

        self.labelMic = QLabel(Widget)
        self.labelMic.setObjectName(u"labelMic")
        self.labelMic.setMinimumSize(QSize(80, 80))
        self.labelMic.setMaximumSize(QSize(80, 80))
        self.labelMic.setPixmap(QPixmap(u"micro.png"))
        self.labelMic.setScaledContents(True)
        self.labelMic.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutMic.addWidget(self.labelMic)

        self.spacerRightMic = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutMic.addItem(self.spacerRightMic)


        self.layoutMicInner.addLayout(self.horizontalLayoutMic)


        self.layoutMic.addLayout(self.layoutMicInner)

        self.buttonMicToggle = QPushButton(Widget)
        self.buttonMicToggle.setObjectName(u"buttonMicToggle")

        self.layoutMic.addWidget(self.buttonMicToggle)


        self.topLayout.addLayout(self.layoutMic)

        self.layoutMe = QVBoxLayout()
        self.layoutMe.setObjectName(u"layoutMe")
        self.layoutMeAvatar = QVBoxLayout()
        self.layoutMeAvatar.setObjectName(u"layoutMeAvatar")
        self.horizontalLayoutMeAvatar = QHBoxLayout()
        self.horizontalLayoutMeAvatar.setObjectName(u"horizontalLayoutMeAvatar")
        self.spacerLeftMe = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutMeAvatar.addItem(self.spacerLeftMe)

        self.labelMeAvatar = QLabel(Widget)
        self.labelMeAvatar.setObjectName(u"labelMeAvatar")
        self.labelMeAvatar.setMinimumSize(QSize(50, 50))
        self.labelMeAvatar.setMaximumSize(QSize(50, 50))
        self.labelMeAvatar.setPixmap(QPixmap(u"avatar.png"))
        self.labelMeAvatar.setScaledContents(True)
        self.labelMeAvatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutMeAvatar.addWidget(self.labelMeAvatar)

        self.spacerRightMe = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutMeAvatar.addItem(self.spacerRightMe)


        self.layoutMeAvatar.addLayout(self.horizontalLayoutMeAvatar)


        self.layoutMe.addLayout(self.layoutMeAvatar)

        self.labelMeText = QLabel(Widget)
        self.labelMeText.setObjectName(u"labelMeText")
        self.labelMeText.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.layoutMe.addWidget(self.labelMeText)

        self.comboMyLang = QComboBox(Widget)
        self.comboMyLang.addItem("")
        self.comboMyLang.addItem("")
        self.comboMyLang.addItem("")
        self.comboMyLang.setObjectName(u"comboMyLang")

        self.layoutMe.addWidget(self.comboMyLang)


        self.topLayout.addLayout(self.layoutMe)


        self.verticalLayoutMain.addLayout(self.topLayout)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.hboxLayout.setContentsMargins(280, -1, 280, -1)
        self.buttonNewConversation = QPushButton(Widget)
        self.buttonNewConversation.setObjectName(u"buttonNewConversation")
        self.buttonNewConversation.setAutoFillBackground(False)
        self.buttonNewConversation.setFlat(False)

        self.hboxLayout.addWidget(self.buttonNewConversation)


        self.verticalLayoutMain.addLayout(self.hboxLayout)

        self.hboxLayout1 = QHBoxLayout()
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.textChatBox = QTextEdit(Widget)
        self.textChatBox.setObjectName(u"textChatBox")

        self.hboxLayout1.addWidget(self.textChatBox)

        self.textSummaryBox = QTextEdit(Widget)
        self.textSummaryBox.setObjectName(u"textSummaryBox")

        self.hboxLayout1.addWidget(self.textSummaryBox)


        self.verticalLayoutMain.addLayout(self.hboxLayout1)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Translator Tool", None))
        self.labelCustomerText.setText(QCoreApplication.translate("Widget", u"Customer", None))
        self.comboCustomerLang.setItemText(0, QCoreApplication.translate("Widget", u"Japanese", None))
        self.comboCustomerLang.setItemText(1, QCoreApplication.translate("Widget", u"English", None))
        self.comboCustomerLang.setItemText(2, QCoreApplication.translate("Widget", u"Vietnamese", None))

        self.buttonMicToggle.setText(QCoreApplication.translate("Widget", u"ON", None))
        self.labelMeText.setText(QCoreApplication.translate("Widget", u"Me", None))
        self.comboMyLang.setItemText(0, QCoreApplication.translate("Widget", u"Vietnamese", None))
        self.comboMyLang.setItemText(1, QCoreApplication.translate("Widget", u"English", None))
        self.comboMyLang.setItemText(2, QCoreApplication.translate("Widget", u"Japanese", None))

        self.buttonNewConversation.setText(QCoreApplication.translate("Widget", u"NEW Conversation", None))
        self.textChatBox.setPlaceholderText(QCoreApplication.translate("Widget", u"Meeting chats...", None))
        self.textSummaryBox.setPlaceholderText(QCoreApplication.translate("Widget", u"LLM summary area...", None))
    # retranslateUi

