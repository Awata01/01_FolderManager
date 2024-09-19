import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QStyle, QFileIconProvider
from PyQt6.QtCore import Qt, QFileInfo, QRect
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap, QPainter, QPen, QColor

class FileManager(QWidget):
    def __init__(self, title="FileManager", extensions=["*"]):
        """
        FileManager クラスの初期化。ファイル選択ダイアログやドラッグ＆ドロップをサポートするウィンドウを作成。

        Args:
            title (str): ウィンドウのタイトル。
            extensions (list): 許可されたファイル拡張子のリスト。デフォルトは全てのファイルを許可。
        """
        super().__init__()
        self.title = title
        self.extensions = extensions  # 許可されたファイル拡張子を設定
        self.initUI()

    def initUI(self):
        """
        ウィンドウのUIを初期化。ボタン、ラベル、ドラッグ＆ドロップの設定を行う。
        """
        # ドラッグ＆ドロップを受け付ける設定
        self.setAcceptDrops(True)

        # ファイル選択用ボタンの作成
        self.button = QPushButton('📁エクスプローラを開く', self)
        self.button.setFixedSize(200, 50)  # ボタンのサイズを設定（幅200px, 高さ50px）
        self.button.clicked.connect(self.showDialog)

        # ファイル名を表示するラベルを作成
        self.label = QLabel('ここにファイルをドラッグ＆ドロップしてください', self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # アイコン表示用のラベルを追加
        self.iconLabel = QLabel(self)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.iconLabel.setFixedSize(64, 64)  # アイコンサイズを64x64に設定

        # レイアウトの設定
        layout = QVBoxLayout()
        layout.addWidget(self.iconLabel, alignment=Qt.AlignmentFlag.AlignCenter)  # アイコン
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)  # ボタン
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)    # 文字列
        layout.addStretch(1)  # 下部スペース
        self.setLayout(layout)

        # ウィンドウの設定
        self.setWindowTitle(self.title)  # ウィンドウタイトルを設定
        self.setGeometry(300, 300, 400, 400)  # ウィンドウのサイズと位置を設定
        self.center()  # ウィンドウを画面中央に配置

    def showDialog(self):
        """
        ファイル選択ダイアログを表示し、選択されたファイルパスをラベルに表示する。
        """
        # ファイルフィルター文字列の作成
        file_filter = ';;'.join([f"{ext.upper()} Files (*.{ext})" for ext in self.extensions])
        # ファイルダイアログの表示
        options = QFileDialog.Option.ReadOnly
        file, _ = QFileDialog.getOpenFileName(self, '📁エクスプローラを開く', '', file_filter, options=options)

        if file:
            self.label.setText(f'{file}')  # 選択されたファイルのパスをラベルに表示
            self.displayIcon(file)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        ドラッグがウィンドウに入った時のイベント処理。

        Args:
            event (QDragEnterEvent): ドラッグイベントオブジェクト。
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # ドラッグされたファイルを受け入れる
        else:
            event.ignore()  # ドラッグされたファイルを無視

    def dropEvent(self, event: QDropEvent):
        """
        ドラッグ＆ドロップでファイルがウィンドウ内にドロップされた時の処理。

        Args:
            event (QDropEvent): ドロップイベントオブジェクト。
        """
        files = event.mimeData().urls()
        if files:
            file_path = files[0].toLocalFile()  # ドロップされたファイルのローカルパスを取得
            # 許可された拡張子であるかをチェック
            if any(file_path.lower().endswith(f".{ext.lower()}") for ext in self.extensions):
                self.label.setText(f'{file_path}')
                self.displayIcon(file_path)
            else:
                self.label.setText(f'指定された拡張子のファイルをドロップしてください：\n\t{self.extensions}')

    def displayIcon(self, file_path):
        """
        選択されたファイルのアイコンを表示する。

        Args:
            file_path (str): ファイルのパス。
        """
        # QFileIconProviderを使用してファイルのアイコンを取得
        icon_provider = QFileIconProvider()
        file_info = QFileInfo(file_path)
        icon = icon_provider.icon(file_info)

        # アイコンをQPixmapに変換してラベルに設定
        pixmap = icon.pixmap(64, 64)
        self.iconLabel.setPixmap(pixmap)

    def center(self):
        """
        ウィンドウを画面中央に配置する。
        """
        # ウィンドウのサイズを取得
        qr = self.frameGeometry()
        # デスクトップスクリーンのサイズを取得
        cp = QApplication.primaryScreen().availableGeometry().center()
        # ウィンドウを中央に配置
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def paintEvent(self, event):
        """
        点線の四角形を描画するためのイベント処理。

        Args:
            event (QPaintEvent): ペイントイベントオブジェクト。
        """
        # QPainterオブジェクトの作成
        painter = QPainter(self)
        # 点線ペンの作成
        pen = QPen(QColor(255, 255, 255), 2, Qt.PenStyle.DotLine)
        painter.setPen(pen)

        # 角丸四角形の描画
        rect = QRect(50, 100, 300, 200)  # 四角形の位置とサイズを設定
        radius = 20  # 角丸の半径を設定
        painter.drawRoundedRect(rect, radius, radius)

if __name__ == '__main__':
    # QApplicationオブジェクトを作成
    app = QApplication(sys.argv)

    ff_extensions = ["xlsx", "xls"]
    # 引数に基づいてウィンドウのタイトルとファイルフィルターを設定
    ex = FileManager(title="Excelファイル管理", extensions=ff_extensions)

    ex.show()
    # アプリケーションのメインループを開始
    sys.exit(app.exec())
