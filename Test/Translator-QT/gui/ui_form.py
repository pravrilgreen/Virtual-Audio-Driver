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
    QLayout, QPushButton, QSizePolicy, QSpacerItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.setWindowModality(Qt.WindowModality.WindowModal)
        Widget.resize(548, 370)
        Widget.setMaximumSize(QSize(680, 16777215))
        icon = QIcon()
        icon.addFile(u":/assets/images/micro.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Widget.setWindowIcon(icon)
        self.verticalLayoutMain = QVBoxLayout(Widget)
        self.verticalLayoutMain.setSpacing(6)
        self.verticalLayoutMain.setObjectName(u"verticalLayoutMain")
        self.verticalLayoutMain.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.topLayout = QHBoxLayout()
        self.topLayout.setSpacing(0)
        self.topLayout.setObjectName(u"topLayout")
        self.topLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.layoutCustomer = QVBoxLayout()
        self.layoutCustomer.setObjectName(u"layoutCustomer")
        self.layoutCustomerAvatar = QVBoxLayout()
        self.layoutCustomerAvatar.setObjectName(u"layoutCustomerAvatar")
        self.horizontalLayoutCustomerAvatar = QHBoxLayout()
        self.horizontalLayoutCustomerAvatar.setObjectName(u"horizontalLayoutCustomerAvatar")
        self.spacerLeftCustomer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayoutCustomerAvatar.addItem(self.spacerLeftCustomer)

        self.labelCustomerAvatar = QLabel(Widget)
        self.labelCustomerAvatar.setObjectName(u"labelCustomerAvatar")
        self.labelCustomerAvatar.setMinimumSize(QSize(50, 50))
        self.labelCustomerAvatar.setMaximumSize(QSize(50, 50))
        self.labelCustomerAvatar.setPixmap(QPixmap(u":/assets/images/avatar.png"))
        self.labelCustomerAvatar.setScaledContents(True)
        self.labelCustomerAvatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutCustomerAvatar.addWidget(self.labelCustomerAvatar)

        self.spacerRightCustomer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayoutCustomerAvatar.addItem(self.spacerRightCustomer)


        self.layoutCustomerAvatar.addLayout(self.horizontalLayoutCustomerAvatar)


        self.layoutCustomer.addLayout(self.layoutCustomerAvatar)

        self.labelCustomerText = QLabel(Widget)
        self.labelCustomerText.setObjectName(u"labelCustomerText")
        self.labelCustomerText.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.layoutCustomer.addWidget(self.labelCustomerText)

        self.layoutCustomerLangBox = QHBoxLayout()
        self.layoutCustomerLangBox.setObjectName(u"layoutCustomerLangBox")
        self.spacerLeftCustomerLang = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutCustomerLangBox.addItem(self.spacerLeftCustomerLang)

        self.comboCustomerLang = QComboBox(Widget)
        icon1 = QIcon()
        icon1.addFile(u":/assets/images/jp.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.comboCustomerLang.addItem(icon1, "")
        icon2 = QIcon()
        icon2.addFile(u":/assets/images/uk.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.comboCustomerLang.addItem(icon2, "")
        icon3 = QIcon()
        icon3.addFile(u":/assets/images/vn.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.comboCustomerLang.addItem(icon3, "")
        self.comboCustomerLang.setObjectName(u"comboCustomerLang")
        self.comboCustomerLang.setMinimumSize(QSize(180, 20))
        self.comboCustomerLang.setMaximumSize(QSize(180, 20))

        self.layoutCustomerLangBox.addWidget(self.comboCustomerLang)

        self.spacerRightCustomerLang = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutCustomerLangBox.addItem(self.spacerRightCustomerLang)


        self.layoutCustomer.addLayout(self.layoutCustomerLangBox)


        self.topLayout.addLayout(self.layoutCustomer)

        self.layoutMic = QVBoxLayout()
        self.layoutMic.setObjectName(u"layoutMic")
        self.layoutMicInner = QVBoxLayout()
        self.layoutMicInner.setObjectName(u"layoutMicInner")
        self.horizontalLayoutMic = QHBoxLayout()
        self.horizontalLayoutMic.setObjectName(u"horizontalLayoutMic")
        self.spacerLeftMic = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayoutMic.addItem(self.spacerLeftMic)

        self.labelMic = QLabel(Widget)
        self.labelMic.setObjectName(u"labelMic")
        self.labelMic.setMinimumSize(QSize(80, 80))
        self.labelMic.setMaximumSize(QSize(80, 80))
        self.labelMic.setPixmap(QPixmap(u":/assets/images/micro.png"))
        self.labelMic.setScaledContents(True)
        self.labelMic.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutMic.addWidget(self.labelMic)

        self.spacerRightMic = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayoutMic.addItem(self.spacerRightMic)


        self.layoutMicInner.addLayout(self.horizontalLayoutMic)


        self.layoutMic.addLayout(self.layoutMicInner)

        self.layoutToggleButton = QHBoxLayout()
        self.layoutToggleButton.setObjectName(u"layoutToggleButton")
        self.spacerLeftToggle = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutToggleButton.addItem(self.spacerLeftToggle)

        self.buttonMicToggle = QPushButton(Widget)
        self.buttonMicToggle.setObjectName(u"buttonMicToggle")
        self.buttonMicToggle.setMinimumSize(QSize(120, 25))
        self.buttonMicToggle.setMaximumSize(QSize(120, 25))

        self.layoutToggleButton.addWidget(self.buttonMicToggle)

        self.spacerRightToggle = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutToggleButton.addItem(self.spacerRightToggle)


        self.layoutMic.addLayout(self.layoutToggleButton)


        self.topLayout.addLayout(self.layoutMic)

        self.layoutMe = QVBoxLayout()
        self.layoutMe.setObjectName(u"layoutMe")
        self.layoutMeAvatar = QVBoxLayout()
        self.layoutMeAvatar.setObjectName(u"layoutMeAvatar")
        self.horizontalLayoutMeAvatar = QHBoxLayout()
        self.horizontalLayoutMeAvatar.setObjectName(u"horizontalLayoutMeAvatar")
        self.spacerLeftMe = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayoutMeAvatar.addItem(self.spacerLeftMe)

        self.labelMeAvatar = QLabel(Widget)
        self.labelMeAvatar.setObjectName(u"labelMeAvatar")
        self.labelMeAvatar.setMinimumSize(QSize(50, 50))
        self.labelMeAvatar.setMaximumSize(QSize(50, 50))
        self.labelMeAvatar.setPixmap(QPixmap(u":/assets/images/avatar.png"))
        self.labelMeAvatar.setScaledContents(True)
        self.labelMeAvatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutMeAvatar.addWidget(self.labelMeAvatar)

        self.spacerRightMe = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayoutMeAvatar.addItem(self.spacerRightMe)


        self.layoutMeAvatar.addLayout(self.horizontalLayoutMeAvatar)


        self.layoutMe.addLayout(self.layoutMeAvatar)

        self.labelMeText = QLabel(Widget)
        self.labelMeText.setObjectName(u"labelMeText")
        self.labelMeText.setAutoFillBackground(False)
        self.labelMeText.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.layoutMe.addWidget(self.labelMeText)

        self.layoutMyLangBox = QHBoxLayout()
        self.layoutMyLangBox.setObjectName(u"layoutMyLangBox")
        self.spacerLeftMyLang = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutMyLangBox.addItem(self.spacerLeftMyLang)

        self.comboMyLang = QComboBox(Widget)
        self.comboMyLang.addItem(icon3, "")
        self.comboMyLang.addItem(icon2, "")
        self.comboMyLang.addItem(icon1, "")
        self.comboMyLang.setObjectName(u"comboMyLang")
        self.comboMyLang.setMinimumSize(QSize(180, 20))
        self.comboMyLang.setMaximumSize(QSize(180, 20))

        self.layoutMyLangBox.addWidget(self.comboMyLang)

        self.spacerRightMyLang = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutMyLangBox.addItem(self.spacerRightMyLang)


        self.layoutMe.addLayout(self.layoutMyLangBox)


        self.topLayout.addLayout(self.layoutMe)


        self.verticalLayoutMain.addLayout(self.topLayout)

        self.layoutNewAndSetting = QHBoxLayout()
        self.layoutNewAndSetting.setObjectName(u"layoutNewAndSetting")
        self.buttonNewConversation = QPushButton(Widget)
        self.buttonNewConversation.setObjectName(u"buttonNewConversation")
        self.buttonNewConversation.setMinimumSize(QSize(180, 25))
        self.buttonNewConversation.setMaximumSize(QSize(180, 25))

        self.layoutNewAndSetting.addWidget(self.buttonNewConversation)

        self.spacerBetweenNewAndSetting = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutNewAndSetting.addItem(self.spacerBetweenNewAndSetting)

        self.buttonSettings = QPushButton(Widget)
        self.buttonSettings.setObjectName(u"buttonSettings")
        self.buttonSettings.setMinimumSize(QSize(30, 30))
        self.buttonSettings.setMaximumSize(QSize(30, 30))
        icon4 = QIcon()
        icon4.addFile(u":/assets/images/settings.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonSettings.setIcon(icon4)
        self.buttonSettings.setIconSize(QSize(24, 24))
        self.buttonSettings.setFlat(True)

        self.layoutNewAndSetting.addWidget(self.buttonSettings)


        self.verticalLayoutMain.addLayout(self.layoutNewAndSetting)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.textChatBox = QTextEdit(Widget)
        self.textChatBox.setObjectName(u"textChatBox")

        self.hboxLayout.addWidget(self.textChatBox)

        self.textSummaryBox = QTextEdit(Widget)
        self.textSummaryBox.setObjectName(u"textSummaryBox")

        self.hboxLayout.addWidget(self.textSummaryBox)


        self.verticalLayoutMain.addLayout(self.hboxLayout)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"NS Team", None))
        self.labelCustomerText.setText(QCoreApplication.translate("Widget", u"Other(s)", None))
        self.comboCustomerLang.setItemText(0, QCoreApplication.translate("Widget", u"Japanese (\u65e5\u672c)", None))
        self.comboCustomerLang.setItemText(1, QCoreApplication.translate("Widget", u"English (English)", None))
        self.comboCustomerLang.setItemText(2, QCoreApplication.translate("Widget", u"Vietnamese (Vi\u1ec7t Nam)", None))

        self.buttonMicToggle.setText(QCoreApplication.translate("Widget", u"Live Translate: OFF", None))
        self.labelMeText.setText(QCoreApplication.translate("Widget", u"User", None))
        self.comboMyLang.setItemText(0, QCoreApplication.translate("Widget", u"Vietnamese (Vi\u1ec7t Nam)", None))
        self.comboMyLang.setItemText(1, QCoreApplication.translate("Widget", u"English (English)", None))
        self.comboMyLang.setItemText(2, QCoreApplication.translate("Widget", u"Japanese (\u65e5\u672c)", None))

        self.buttonNewConversation.setText(QCoreApplication.translate("Widget", u"NEW Conversation", None))
#if QT_CONFIG(tooltip)
        self.buttonSettings.setToolTip(QCoreApplication.translate("Widget", u"Settings", None))
#endif // QT_CONFIG(tooltip)
        self.textChatBox.setPlaceholderText(QCoreApplication.translate("Widget", u"Meeting chats...", None))
        self.textSummaryBox.setPlaceholderText(QCoreApplication.translate("Widget", u"LLM summary area...", None))
    # retranslateUi

