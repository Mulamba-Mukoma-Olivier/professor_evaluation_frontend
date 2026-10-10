"""Shared frameless window chrome and drag support."""

from PyQt5.QtCore import QObject, Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)


class WindowDragFilter(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.drag_offset = None

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.window.frameGeometry().topLeft()
        elif event.type() == QEvent.MouseMove and self.drag_offset is not None:
            if event.buttons() & Qt.LeftButton and not self.window.isMaximized():
                self.window.move(event.globalPos() - self.drag_offset)
        elif event.type() == QEvent.MouseButtonRelease:
            self.drag_offset = None
        elif event.type() == QEvent.MouseButtonDblClick and event.button() == Qt.LeftButton:
            self.window.showNormal() if self.window.isMaximized() else self.window.showMaximized()
        return False


def install_drag_handle(window, widgets):
    drag_filter = WindowDragFilter(window)
    for widget in widgets:
        if widget is not None:
            widget.installEventFilter(drag_filter)
    window._frameless_drag_filter = drag_filter


class FramelessTitleBar(QFrame):
    def __init__(self, window, title):
        super().__init__()
        self.window = window
        self.setObjectName("framelessTitleBar")
        self.setFixedHeight(42)
        self.setStyleSheet(
            "QFrame#framelessTitleBar { background: transparent; border: none; }"
            "QLabel { color: #123b66; background: transparent; font-size: 12px; font-weight: 700; }"
            "QPushButton { color: #123b66; background: transparent; border: none; border-radius: 6px; "
            "font-size: 16px; min-width: 32px; max-width: 32px; min-height: 28px; max-height: 28px; }"
            "QPushButton:hover { background: rgba(37, 99, 235, 35); color: #123b66; }"
            "QPushButton#windowClose:hover { background: #dc2626; color: white; }"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 8, 0)
        layout.setSpacing(6)
        icon = window.windowIcon()
        if not icon.isNull():
            logo = QLabel()
            logo.setFixedSize(24, 24)
            logo.setPixmap(icon.pixmap(24, 24))
            layout.addWidget(logo)
        label = QLabel(title)
        layout.addWidget(label)
        layout.addStretch(1)

        minimize = QPushButton("−")
        minimize.setToolTip("Réduire")
        maximize = QPushButton("□")
        maximize.setToolTip("Agrandir / restaurer")
        close = QPushButton("×")
        close.setObjectName("windowClose")
        close.setToolTip("Fermer")
        layout.addWidget(minimize)
        layout.addWidget(maximize)
        layout.addWidget(close)
        minimize.clicked.connect(window.showMinimized)
        maximize.clicked.connect(lambda: window.showNormal() if window.isMaximized() else window.showMaximized())
        close.clicked.connect(window.close)
        install_drag_handle(window, [self, label])


class _ResizeGripPositioner(QObject):
    def __init__(self, window, grip):
        super().__init__(window)
        self.window = window
        self.grip = grip

    def position_grip(self):
        size = self.grip.sizeHint()
        self.grip.setGeometry(
            self.window.width() - size.width(),
            self.window.height() - size.height(),
            size.width(),
            size.height(),
        )
        self.grip.raise_()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Resize:
            self.position_grip()
        return False


class _TitleBarPositioner(QObject):
    def __init__(self, window, title_bar):
        super().__init__(window)
        self.window = window
        self.title_bar = title_bar

    def position_title_bar(self):
        self.title_bar.setGeometry(0, 0, self.window.width(), self.title_bar.height())
        self.title_bar.raise_()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Resize:
            self.position_title_bar()
        return False


def install_size_grip(window):
    """Add a visible bottom-right resize handle to a frameless top-level window."""
    grip = QSizeGrip(window)
    grip.setToolTip("Redimensionner")
    grip.setFixedSize(18, 18)
    positioner = _ResizeGripPositioner(window, grip)
    window.installEventFilter(positioner)
    window._frameless_size_grip = grip
    window._frameless_grip_positioner = positioner
    positioner.position_grip()
    grip.show()
    return grip


def install_frameless_chrome(window, title, central_widget=None):
    """Wrap an ordinary top-level widget with a compact draggable title bar."""
    flags = window.windowFlags() & ~Qt.WindowType_Mask
    window.setWindowFlags(
        flags
        | Qt.Window
        | Qt.FramelessWindowHint
        | Qt.WindowMinimizeButtonHint
        | Qt.WindowMaximizeButtonHint
        | Qt.WindowCloseButtonHint
    )
    install_size_grip(window)
    if isinstance(window, QMainWindow):
        content = central_widget or window.takeCentralWidget()
        shell = QFrame()
        shell.setObjectName("framelessWindowShell")
        shell.setStyleSheet(
            "QFrame#framelessWindowShell { background: transparent; border: 1px solid #dbe4f0; "
            "border-radius: 12px; }"
        )
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        layout.addWidget(FramelessTitleBar(window, title))
        if content is not None:
            layout.addWidget(content, 1)
        window.setCentralWidget(shell)
        return shell

    window.setWindowFlags(window.windowFlags() | Qt.FramelessWindowHint)
    install_size_grip(window)
    content_layout = window.layout()
    if content_layout is not None:
        left, top, right, bottom = content_layout.getContentsMargins()
        content_layout.setContentsMargins(left, top + 42, right, bottom)

    title_bar = FramelessTitleBar(window, title)
    title_bar.setParent(window)
    positioner = _TitleBarPositioner(window, title_bar)
    window.installEventFilter(positioner)
    window._frameless_titlebar = title_bar
    window._frameless_titlebar_positioner = positioner
    positioner.position_title_bar()
    title_bar.show()
    return title_bar
