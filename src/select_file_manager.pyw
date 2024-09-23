import sys
import os
import re
from PySide6.QtWidgets import (
    QApplication, QDialog, QLabel, QPushButton, QTableWidget
    , QTableWidgetItem, QCheckBox, QHBoxLayout, QVBoxLayout, QFileDialog
    , QHeaderView, QWidget, QAbstractItemView, QFileIconProvider
)
from PySide6.QtCore import Qt, QFileInfo
from PySide6.QtGui import QIcon, QFont, QColor, QBrush

sys.path.append(r"C:\Users\awata\Awata01\Programming\00_Common\src")
from custom_logging import CustomLogging

class SelectFileManager(QDialog):
    # SelectFileManager.Accepted（1）: 正常終了
    # SelectFileManager.Rejected（0）：異常終了
    def __init__(self, file_filter: str="All Files (*.*)", parent=None) -> None:
        """
        SelectFileManagerの初期化メソッド

        Args:
            file_filter (str): ファイル選択ダイアログで使用するフィルタ\n
                記述テンプレート：表示テキスト (*.{拡張子1} *.{拡張子2}...)\n
                Default: All Files (\*.\*)
            parent (QWidget): 親ウィジェット
        """
        self.logger = CustomLogging("SelectFileManager")

        super().__init__(parent)

        # インスタンス変数
        self.file_filter = file_filter
        self.file_path_list: list[str] = []

        # ウィンドウの設定
        self.setWindowTitle("SelectFileManger")
        self.resize(500, 300)
        self.setWindowIcon(QIcon(r"C:\Users\awata\Awata01\Programming\01_FolderManager\SelectFileManager-icon.png"))

        # ラベルの設定
        self.label_list = QLabel("📝選択ファイルリスト")
        self.label_accept_extension = QLabel(f"許可するファイル： {self.file_filter}")
        self.label_accept_extension.setStyleSheet("font-size: 10px;")
        self.label_folder = QLabel("📄D&Dでも選択可能")
        self.label_folder.setStyleSheet("font-size: 10px;")
        self.label_folder.setAlignment(Qt.AlignRight)

        # ボタンの設定
        self.push_button_select_file = QPushButton("📂エクスプローラーから選択")
        self.push_button_select_file.clicked.connect(lambda: self.select_by_explorer())

        self.push_button_next = QPushButton("次へ")
        self.push_button_next.setFixedSize(80, 25)
        self.push_button_next.setDisabled(True)
        self.push_button_next.clicked.connect(self.button_next_event)

        self.push_button_delete = QPushButton("削除")
        self.push_button_delete.setFixedSize(80, 25)
        self.push_button_delete.setDisabled(True)
        self.push_button_delete.clicked.connect(self.button_delete_event)

        # テーブルの設定
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["☒", "ファイル名", "ファイルパス"])
        self.table_widget.setColumnWidth(0, 30)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(1, 250)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.doubleClicked.connect(self.cell_doubleClicked_event)

        # レイアウトの設定
        layout_V = QVBoxLayout()
        layout_V.addWidget(self.label_list)
        layout_V.addWidget(self.label_accept_extension)
        layout_V.addWidget(self.table_widget)
        layout_V.addSpacing(5)

        layout_H = QHBoxLayout()
        layout_H.addWidget(self.push_button_delete)
        layout_H.addWidget(self.push_button_next)
        layout_H.addWidget(self.push_button_select_file)
        layout_V.addWidget(self.label_folder)

        layout_V.addLayout(layout_H)

        self.setLayout(layout_V)

        # ドラッグ＆ドロップの設定
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event) -> None:
        """
        ドラッグイベントが発生した際の処理

        Args:
            event (QDragEnterEvent): ドラッグされたオブジェクトに関するイベント
        """
        if event.mimeData().hasUrls():
            extension_list = self.get_extension_from_file_filter()
            for url in event.mimeData().urls():


                if (
                    url.isLocalFile()   # ローカルファイル存在チェック
                    and not os.path.isdir(url.toLocalFile())    # ディレクトリの場合は除外
                    and (
                        os.path.splitext(url.toLocalFile())[1] in extension_list    # 拡張子チェック
                        or ".*" in extension_list   # フィルタが「All Files (*.*)」の場合はTrue
                    )
                ):
                    event.acceptProposedAction()
                else: break

    def dropEvent(self, event) -> None:
        """
        ドロップイベントが発生した際の処理

        Args:
            event (QDropEvent): ドロップされたオブジェクトに関するイベント
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.add_file_to_table(file_path)

    def select_by_explorer(self) -> None:
        """
        ファイルダイアログを使ってファイルを選択する処理
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        # ショートカットファイルの表示を無効化
        file_dialog.setNameFilter(self.file_filter)
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec():
            for file_path in file_dialog.selectedFiles():
                self.add_file_to_table(file_path)

    def add_file_to_table(self, file_path: str) -> None:
        """
        テーブルにファイルを追加する処理

        Args:
            file_path (str): 追加するファイルのパス
        """
        file_name = QTableWidgetItem(os.path.basename(file_path))
        file_icon = QFileIconProvider().icon(QFileInfo(file_path))
        file_name.setIcon(file_icon)
        file_name.setForeground(QBrush(QColor("blue")))
        font = QFont()
        font.setUnderline(True)
        file_name.setFont(font)

        self.delete_file_from_table(file_path)

        last_row = self.table_widget.rowCount()
        self.table_widget.insertRow(last_row)

        chk_bx = QCheckBox()
        chk_bx.stateChanged.connect(self.checkbox_state_changed)
        chk_wdg = QWidget()
        chk_layout = QHBoxLayout(chk_wdg)
        chk_layout.addWidget(chk_bx)
        chk_layout.setAlignment(Qt.AlignCenter)
        chk_layout.setContentsMargins(0, 0, 0, 0)

        self.table_widget.setCellWidget(last_row, 0, chk_wdg)
        self.table_widget.setItem(last_row, 1, file_name)
        self.table_widget.setItem(last_row, 2, QTableWidgetItem(file_path))

        self.logger.info(f"ファイル追加, 表示行番号:{last_row+1}, ファイル名:{file_name.text()}, ファイルパス:{file_path}")

        self.table_item_count()

    def delete_file_from_table(self, file_path: str) -> None:
        """
        テーブルからファイルを削除する処理

        Args:
            file_path_item str: 削除対象のファイルパスアイテム
        """
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 2)
            if item is not None and item.text() == file_path:
                file_name = self.table_widget.item(row, 1).text()
                self.table_widget.removeRow(row)
                self.logger.info(f"ファイル削除, 表示行番号:{row+1}, ファイル名:{file_name}, ファイルパス:{file_path}")
                break

    def checkbox_state_changed(self) -> None:
        """
        チェックボックスの状態が変更されたときの処理
        """
        checked_count = sum(
            self.table_widget.cellWidget(row, 0).findChild(QCheckBox).isChecked()
            for row in range(self.table_widget.rowCount())
        )
        self.push_button_delete.setEnabled(checked_count > 0)

    def table_item_count(self) -> None:
        """
        テーブル内のアイテム数を確認し、ボタンの有効・無効を設定する処理
        """
        item_count = self.table_widget.rowCount()
        self.push_button_next.setEnabled(item_count > 0)
        if item_count == 0:
            self.push_button_delete.setEnabled(False)

    def button_next_event(self) -> None:
        """
        「次へ」ボタンが押されたときの処理
        """
        self.file_path_list = []
        for row in range(self.table_widget.rowCount()):
            file_path = self.table_widget.item(row, 2).text()
            self.file_path_list.append(file_path)

        self.accept()
        self.logger.info("SelectFileMangerが正常終了しました。")

    def button_delete_event(self) -> None:
        """
        「削除」ボタンが押されたときの処理
        """
        for row in reversed(range(self.table_widget.rowCount())):
            chk_bx = self.table_widget.cellWidget(row, 0).findChild(QCheckBox)
            if chk_bx.isChecked():
                file_path = self.table_widget.item(row, 2).text()
                self.delete_file_from_table(file_path)
        self.table_item_count()
        self.checkbox_state_changed()

    def cell_doubleClicked_event(self, index) -> None:
        """テーブルのセルがダブルクリックされたときの処理

        Args:
            index (QModelIndex): クリックされたセルのインデックス
        """
        row = index.row()
        column = index.column()
        if column == 1:  # ファイル名の列がクリックされた場合
            file_path_item = self.table_widget.item(row, 2)
            if file_path_item:
                file_path = file_path_item.text()
                # vscodeでファイルを開く
                os.system(fr'code "{file_path}"')
                self.logger.info(f"ファイルを開きます。{file_path}")

    def get_extension_from_file_filter(self) -> list:
        """
        ファイルフィルタから拡張子を取得する処理

        Returns:
            str: ファイルフィルタから拡張子をリストで取得
        """
        pattern = r"(\.[^\s,\)]+)"
        matches = re.findall(pattern, self.file_filter)

        return matches

if __name__ == "__main__":
    logger = CustomLogging("SelectFileManager_main")
    logger.process_start()

    app = QApplication(sys.argv)
    dialog = SelectFileManager()

    match dialog.exec():
        case SelectFileManager.Accepted:
            file_list = dialog.file_path_list
            logger.info(f"選択されたファイルリスト：{file_list}")
            logger.process_end()
        case SelectFileManager.Rejected:
            logger.info("SelectFileManagerが強制的に終了")