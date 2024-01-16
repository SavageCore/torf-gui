#!/usr/bin/env python3

import json
import os
import stat
import sys
from datetime import datetime
from fnmatch import fnmatch

import humanfriendly
import qdarktheme
import torf
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColorConstants, QPalette
from PyQt5.QtWidgets import QApplication
from qdarktheme import _style_loader

from torf_gui import Ui_AboutDialog, Ui_MainWindow, __version__

PROGRAM_NAME = "torf-gui"
PROGRAM_NAME_VERSION = f"{PROGRAM_NAME} {__version__}"
CREATOR = f"torf-gui/{__version__} (https://github.com/SavageCore/torf-gui)"

PIECE_SIZES = [None] + [2**i for i in range(14, 26)]

if getattr(sys, "frozen", False):
    _basedir = sys._MEIPASS
else:
    _basedir = os.path.dirname(__file__)


class CreateTorrentQThread(QtCore.QThread):
    progress_update = QtCore.pyqtSignal(str, int, int)
    onError = QtCore.pyqtSignal(str)

    def __init__(self, torrent, save_path):
        super().__init__()
        self.torrent = torrent
        self.save_path = save_path
        self.success = False

    def run(self):
        def progress_callback(*args):
            # Args: torrent, filepath, piece_count, piece_total
            # Emit: filename, piece_count, piece_total
            filename = os.path.split(args[1])[1]
            self.progress_update.emit(filename, args[2], args[3])
            return None

        self.torrent.creation_date = datetime.now()
        self.torrent.created_by = CREATOR
        try:
            self.success = self.torrent.generate(callback=progress_callback)
        except Exception as exc:
            self.onError.emit(str(exc))
            return
        if self.success:
            self.torrent.write(self.save_path, overwrite=True)


class CreateTorrentBatchQThread(QtCore.QThread):
    progress_update = QtCore.pyqtSignal(str, int, int)
    onError = QtCore.pyqtSignal(str)

    def __init__(
        self,
        path,
        exclude,
        save_dir,
        trackers,
        web_seeds,
        private,
        source,
        randomize_infohash,
        comment,
        include_md5,
    ):
        super().__init__()
        self.path = path
        self.exclude = exclude
        self.save_dir = save_dir
        self.trackers = trackers
        self.web_seeds = web_seeds
        self.private = private
        self.source = source
        self.randomize_infohash = randomize_infohash
        self.comment = comment
        self.include_md5 = include_md5

    def has_hidden_attribute(self, filepath):
        return bool(
            os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN
        )

    def is_hidden_file(self, path):
        name = os.path.basename(os.path.abspath(path))
        return name.startswith(".") or self.has_hidden_attribute(path)

    def run(self):  # noqa: C901
        def callback(*args):
            return None

        self.success = False

        if os.path.isdir(self.path):
            if os.listdir(self.path):
                for file in os.listdir(self.path):
                    if os.path.isfile(file) and not self.is_hidden_file(file):
                        break
                else:
                    self.onError.emit("Input path must be non-empty")
                    return

        entries = os.listdir(self.path)

        for i, p in enumerate(entries):
            if any(fnmatch(p, ex) for ex in self.exclude):
                continue
            p = os.path.join(self.path, p)

            # Check if the file (p) is hidden
            if os.path.isfile(p) and not self.is_hidden_file(p):
                sfn = os.path.split(p)[1] + ".torrent"
                self.progress_update.emit(sfn, i, len(entries))
                t = torf.Torrent(
                    path=p,
                    exclude_globs=self.exclude,
                    trackers=self.trackers,
                    webseeds=self.web_seeds,
                    private=self.private,
                    source=self.source,
                    randomize_infohash=self.randomize_infohash,
                    comment=self.comment,
                    creation_date=datetime.now(),
                    created_by=CREATOR,
                )
                try:
                    self.success = t.generate(callback=callback)
                except Exception as exc:
                    self.onError.emit(str(exc))
                    return
                if self.isInterruptionRequested():
                    return
                if self.success:
                    t.write(os.path.join(self.save_dir, sfn), overwrite=True)


class TorfGUI(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        self.torrent = None
        self.MainWindow = MainWindow

        self.actionImportProfile.triggered.connect(self.import_profile)
        self.actionExportProfile.triggered.connect(self.export_profile)
        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.actionQuit.triggered.connect(self.MainWindow.close)

        self.fileRadioButton.toggled.connect(self.inputModeToggle)
        self.fileRadioButton.setChecked(True)
        self.directoryRadioButton.toggled.connect(self.inputModeToggle)

        self.browseButton.clicked.connect(self.browseInput)
        self.batchModeCheckBox.stateChanged.connect(self.batchModeChanged)

        self.inputEdit.dragEnterEvent = self.inputDragEnterEvent
        self.inputEdit.dropEvent = self.inputDropEvent
        self.pasteButton.clicked.connect(self.pasteInput)

        self.pieceCountLabel.hide()
        self.pieceSizeComboBox.addItem("Auto")
        for x in PIECE_SIZES[1:]:
            self.pieceSizeComboBox.addItem(
                humanfriendly.format_size(x, binary=True)
            )

        self.pieceSizeComboBox.currentIndexChanged.connect(
            self.pieceSizeChanged
        )

        self.privateTorrentCheckBox.stateChanged.connect(
            self.privateTorrentChanged
        )

        self.commentEdit.textEdited.connect(self.commentEdited)

        self.sourceEdit.textEdited.connect(self.sourceEdited)

        self.randomizeInfoHashCheckBox.stateChanged.connect(
            self.randomizeInfohashChanged
        )

        self.md5CheckBox.stateChanged.connect(self.md5Changed)

        self.progressBar.hide()
        self.createButton.setEnabled(False)
        self.createButton.clicked.connect(self.createButtonClicked)
        self.cancelButton.hide()
        self.cancelButton.clicked.connect(self.cancel_creation)
        self.resetButton.clicked.connect(self.reset)

        self._statusBarMsg("Ready")

    def getSettings(self):
        portable_fn = PROGRAM_NAME + ".ini"
        portable_fn = os.path.join(_basedir, portable_fn)
        if os.path.exists(portable_fn):
            return QtCore.QSettings(portable_fn, QtCore.QSettings.IniFormat)
        return QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            PROGRAM_NAME,
            PROGRAM_NAME,
        )

    def loadSettings(self):
        settings = self.getSettings()
        if settings.value("input/mode") == "directory":
            self.directoryRadioButton.setChecked(True)
        batch_mode = bool(int(settings.value("input/batch_mode") or 0))
        self.batchModeCheckBox.setChecked(batch_mode)
        exclude = settings.value("input/exclude")
        if exclude:
            self.excludeEdit.setPlainText(exclude)
        trackers = settings.value("seeding/trackers")
        if trackers:
            self.trackerEdit.setPlainText(trackers)
        web_seeds = settings.value("seeding/web_seeds")
        if web_seeds:
            self.webSeedEdit.setPlainText(web_seeds)
        private = bool(int(settings.value("options/private") or 0))
        self.privateTorrentCheckBox.setChecked(private)
        source = settings.value("options/source")
        if source:
            self.sourceEdit.setText(source)
        randomize_infohash = bool(
            int(settings.value("options/randomize_infohash") or 0)
        )
        self.randomizeInfoHashCheckBox.setChecked(randomize_infohash)
        compute_md5 = bool(int(settings.value("options/compute_md5") or 0))
        if compute_md5:
            self.md5CheckBox.setChecked(compute_md5)
        mainwindow_size = settings.value("geometry/size")
        if mainwindow_size:
            self.MainWindow.resize(mainwindow_size)
        mainwindow_position = settings.value("geometry/position")
        if mainwindow_position:
            self.MainWindow.move(mainwindow_position)
        self.last_input_dir = settings.value("history/last_input_dir") or None
        self.last_output_dir = (
            settings.value("history/last_output_dir") or None
        )

    def saveSettings(self):
        settings = self.getSettings()
        settings.setValue("input/mode", self.inputMode)
        settings.setValue(
            "input/batch_mode", int(self.batchModeCheckBox.isChecked())
        )
        settings.setValue("input/exclude", self.excludeEdit.toPlainText())
        settings.setValue("seeding/trackers", self.trackerEdit.toPlainText())
        settings.setValue("seeding/web_seeds", self.webSeedEdit.toPlainText())
        settings.setValue(
            "options/private", int(self.privateTorrentCheckBox.isChecked())
        )
        settings.setValue("options/source", self.sourceEdit.text())
        settings.setValue(
            "options/randomize_infohash",
            int(self.randomizeInfoHashCheckBox.isChecked()),
        )
        settings.setValue(
            "options/compute_md5", int(self.md5CheckBox.isChecked())
        )
        settings.setValue("geometry/size", self.MainWindow.size())
        settings.setValue("geometry/position", self.MainWindow.pos())
        if self.last_input_dir:
            settings.setValue("history/last_input_dir", self.last_input_dir)
        if self.last_output_dir:
            settings.setValue("history/last_output_dir", self.last_output_dir)

    def _statusBarMsg(self, msg):
        self.MainWindow.statusBar().showMessage(msg)

    def _showError(self, msg):
        errdlg = QtWidgets.QErrorMessage()
        errdlg.setWindowTitle("Error")
        errdlg.showMessage(msg)
        errdlg.exec_()

    def showAboutDialog(self):
        qdlg = QtWidgets.QDialog()
        ad = Ui_AboutDialog()
        ad.setupUi(qdlg)
        ad.programVersionLabel.setText(f"version {__version__}")
        ad.dtVersionLabel.setText(f"(torf {torf.__version__})")
        qdlg.exec_()

    def inputModeToggle(self):
        if self.fileRadioButton.isChecked():
            self.inputMode = "file"
            self.batchModeCheckBox.setEnabled(False)
            self.batchModeCheckBox.hide()
            self.pieceSizeComboBox.setEnabled(True)
            if self.torrent:
                self.pieceCountLabel.show()
        else:
            self.inputMode = "directory"
            self.batchModeCheckBox.setEnabled(True)
            self.batchModeCheckBox.show()
            # If batch mode is enabled, disable piece size selection
            if self.batchModeCheckBox.isChecked():
                self.pieceSizeComboBox.setCurrentIndex(0)
                self.pieceSizeComboBox.setEnabled(False)
                self.pieceCountLabel.hide()
        self.inputEdit.setText("")

    def browseInput(self):
        qfd = QtWidgets.QFileDialog(self.MainWindow)
        if self.last_input_dir and os.path.exists(self.last_input_dir):
            qfd.setDirectory(self.last_input_dir)
        if self.inputMode == "file":
            qfd.setWindowTitle("Select file")
            qfd.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        else:
            qfd.setWindowTitle("Select directory")
            qfd.setFileMode(QtWidgets.QFileDialog.Directory)
        if qfd.exec_():
            fn = qfd.selectedFiles()[0]
            self.inputEdit.setText(fn)
            self.last_input_dir = os.path.split(fn)[0]
            self.initializeTorrent()

    def injectInputPath(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                self.fileRadioButton.setChecked(True)
                self.inputMode = "file"
                self.batchModeCheckBox.setCheckState(QtCore.Qt.Unchecked)
                self.batchModeCheckBox.setEnabled(False)
                self.batchModeCheckBox.hide()
            else:
                self.directoryRadioButton.setChecked(True)
                self.inputMode = "directory"
                self.batchModeCheckBox.setEnabled(True)
                self.batchModeCheckBox.show()
            self.inputEdit.setText(path)
            self.last_input_dir = os.path.split(path)[0]
            self.initializeTorrent()

    def inputDragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile():
                event.accept()
                return
        event.ignore()

    def inputDropEvent(self, event):
        path = event.mimeData().urls()[0].toLocalFile()
        self.injectInputPath(path)

    def pasteInput(self):
        mimeData = self.clipboard().mimeData()
        if mimeData.hasText():
            path = mimeData.text().strip("'\"")
            self.injectInputPath(path)

    def batchModeChanged(self, state):
        if state == QtCore.Qt.Checked:
            self.pieceSizeComboBox.setCurrentIndex(0)
            self.pieceSizeComboBox.setEnabled(False)
            self.pieceCountLabel.hide()
        else:
            self.pieceSizeComboBox.setEnabled(True)
            if self.torrent:
                self.pieceCountLabel.show()

    def initializeTorrent(self):
        self.torrent = torf.Torrent(self.inputEdit.text())
        try:
            t_info = self.get_info(self.torrent)
        except Exception as e:
            self.torrent = None
            self._showError(str(e))
            return
        ptail = os.path.split(self.torrent.path)[1]
        if self.inputMode == "file":
            self._statusBarMsg(
                f"{ptail}: {humanfriendly.format_size(t_info[0], binary=True)}"
            )
        else:
            self._statusBarMsg(
                "{}: {} files, {}".format(
                    ptail,
                    t_info[1],
                    humanfriendly.format_size(t_info[0], binary=True),
                )
            )
        self.pieceSizeComboBox.setCurrentIndex(0)
        self.updatePieceCountLabel(t_info[3], t_info[2])
        self.pieceCountLabel.show()
        self.createButton.setEnabled(True)

    def commentEdited(self, comment):
        if getattr(self, "torrent", None):
            self.torrent.comment = comment

    def sourceEdited(self, source):
        if getattr(self, "torrent", None):
            self.torrent.source = source

    def pieceSizeChanged(self, index):
        if getattr(self, "torrent", None):
            # If piece size is greater than piece_size_max_default (16 MiB),
            # set piece_size_max to the selected piece size
            if (
                PIECE_SIZES[index] is not None
                and PIECE_SIZES[index] > 16777216
            ):
                self.torrent.piece_size_max = PIECE_SIZES[index]
            self.torrent.piece_size = PIECE_SIZES[index]
            t_info = self.get_info(self.torrent)
            self.updatePieceCountLabel(t_info[3], t_info[2])

    def updatePieceCountLabel(self, ps, pc):
        ps = humanfriendly.format_size(ps, binary=True)
        self.pieceCountLabel.setText(f"{pc} pieces @ {ps} each")

    def privateTorrentChanged(self, state):
        if getattr(self, "torrent", None):
            self.torrent.private = state == QtCore.Qt.Checked

    def randomizeInfohashChanged(self, state):
        if getattr(self, "torrent", None):
            self.torrent.randomize_infohash = state == QtCore.Qt.Checked

    def md5Changed(self, state):
        if getattr(self, "torrent", None):
            self.torrent.include_md5 = state == QtCore.Qt.Checked

    def createButtonClicked(self):
        self.torrent.exclude_globs = (
            self.excludeEdit.toPlainText().strip().splitlines()
        )
        # Validate trackers and web seed URLs
        trackers = self.trackerEdit.toPlainText().strip().split()
        web_seeds = self.webSeedEdit.toPlainText().strip().split()
        try:
            self.torrent.trackers = trackers
            self.torrent.webseeds = web_seeds
        except Exception as e:
            self._showError(str(e))
            return
        self.torrent.private = self.privateTorrentCheckBox.isChecked()
        self.torrent.randomize_infohash = (
            self.randomizeInfoHashCheckBox.isChecked()
        )
        self.torrent.comment = self.commentEdit.text() or None
        self.torrent.source = self.sourceEdit.text() or None
        self.torrent.include_md5 = self.md5CheckBox.isChecked()
        if (
            self.inputMode == "directory"
            and self.batchModeCheckBox.isChecked()
        ):
            self.createTorrentBatch()
        else:
            self.createTorrent()

    def createTorrent(self):
        if os.path.isfile(self.inputEdit.text()):
            save_fn = (
                os.path.splitext(os.path.split(self.inputEdit.text())[1])[0]
                + ".torrent"
            )
        else:
            save_fn = self.inputEdit.text().split(os.sep)[-1] + ".torrent"
        if self.last_output_dir and os.path.exists(self.last_output_dir):
            save_fn = os.path.join(self.last_output_dir, save_fn)
        fn = QtWidgets.QFileDialog.getSaveFileName(
            self.MainWindow,
            "Save torrent",
            save_fn,
            filter=("Torrent file (*.torrent)"),
        )[0]
        if fn:
            self.last_output_dir = os.path.split(fn)[0]
            self.creation_thread = CreateTorrentQThread(self.torrent, fn)
            self.creation_thread.started.connect(self.creation_started)
            self.creation_thread.progress_update.connect(self._progress_update)
            self.creation_thread.finished.connect(self.creation_finished)
            self.creation_thread.onError.connect(self._showError)
            self.creation_thread.start()

    def createTorrentBatch(self):
        save_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self.MainWindow, "Select output directory", self.last_output_dir
        )
        if save_dir:
            self.last_output_dir = save_dir
            trackers = self.trackerEdit.toPlainText().strip().split()
            web_seeds = self.webSeedEdit.toPlainText().strip().split()
            self.creation_thread = CreateTorrentBatchQThread(
                path=self.inputEdit.text(),
                exclude=self.excludeEdit.toPlainText().strip().splitlines(),
                save_dir=save_dir,
                trackers=trackers,
                web_seeds=web_seeds,
                private=self.privateTorrentCheckBox.isChecked(),
                source=self.sourceEdit.text(),
                comment=self.commentEdit.text(),
                randomize_infohash=self.randomizeInfoHashCheckBox.isChecked(),
                include_md5=self.md5CheckBox.isChecked(),
            )
            self.creation_thread.started.connect(self.creation_started)
            self.creation_thread.progress_update.connect(
                self._progress_update_batch
            )
            self.creation_thread.finished.connect(self.creation_finished)
            self.creation_thread.onError.connect(self._showError)
            self.creation_thread.start()

    def cancel_creation(self):
        self.creation_thread.terminate()

    def _progress_update(self, fn, pc, pt):
        fn = os.path.split(fn)[1]
        msg = f"{fn} ({pc}/{pt})"
        self.updateProgress(msg, int(round(100 * pc / pt)))

    def _progress_update_batch(self, fn, tc, tt):
        msg = f"({tc}/{tt}) {fn}"
        self.updateProgress(msg, int(round(100 * tc / tt)))

    def updateProgress(self, statusMsg, pv):
        self._statusBarMsg(statusMsg)
        self.progressBar.setValue(pv)

    def creation_started(self):
        self.inputGroupBox.setEnabled(False)
        self.seedingGroupBox.setEnabled(False)
        self.optionGroupBox.setEnabled(False)
        self.progressBar.show()
        self.createButton.hide()
        self.cancelButton.show()
        self.resetButton.setEnabled(False)

    def creation_finished(self):
        self.inputGroupBox.setEnabled(True)
        self.seedingGroupBox.setEnabled(True)
        self.optionGroupBox.setEnabled(True)
        self.progressBar.hide()
        self.createButton.show()
        self.cancelButton.hide()
        self.resetButton.setEnabled(True)
        if self.creation_thread.success:
            self._statusBarMsg("Finished")
        else:
            self._statusBarMsg("Canceled")
        self.creation_thread = None

    def export_profile(self):
        fn = QtWidgets.QFileDialog.getSaveFileName(
            self.MainWindow,
            "Save profile",
            self.last_output_dir,
            filter=("JSON configuration file (*.json)"),
        )[0]
        if fn:
            exclude = self.excludeEdit.toPlainText().strip().splitlines()
            trackers = self.trackerEdit.toPlainText().strip().split()
            web_seeds = self.webSeedEdit.toPlainText().strip().split()
            private = self.privateTorrentCheckBox.isChecked()
            randomize_infohash = self.randomizeInfoHashCheckBox.isChecked()
            compute_md5 = self.md5CheckBox.isChecked()
            source = self.sourceEdit.text()
            data = {
                "exclude": exclude,
                "trackers": trackers,
                "web_seeds": web_seeds,
                "private": private,
                "compute_md5": compute_md5,
                "randomize_infohash": randomize_infohash,
                "source": source,
            }
            with open(fn, "w") as f:
                json.dump(data, f, indent=4, sort_keys=True)
            self._statusBarMsg("Profile saved to " + fn)

    def import_profile(self):
        fn = QtWidgets.QFileDialog.getOpenFileName(
            self.MainWindow,
            "Open profile",
            self.last_input_dir,
            filter=("JSON configuration file (*.json)"),
        )[0]
        if fn:
            with open(fn) as f:
                data = json.load(f)
            exclude = data.get("exclude", [])
            trackers = data.get("trackers", [])
            web_seeds = data.get("web_seeds", [])
            private = data.get("private", False)
            randomize_infohash = data.get("randomize_infohash", False)
            compute_md5 = data.get("compute_md5", False)
            source = data.get("source", "")
            try:
                self.excludeEdit.setPlainText(os.linesep.join(exclude))
                self.trackerEdit.setPlainText(os.linesep.join(trackers))
                self.webSeedEdit.setPlainText(os.linesep.join(web_seeds))
                self.privateTorrentCheckBox.setChecked(private)
                self.randomizeInfoHashCheckBox.setChecked(randomize_infohash)
                self.md5CheckBox.setChecked(compute_md5)
                self.sourceEdit.setText(source)
            except Exception as e:
                self._showError(str(e))
                return
            self._statusBarMsg(f"Profile {os.path.split(fn)[1]} loaded")

    def reset(self):
        self._statusBarMsg("")
        self.createButton.setEnabled(False)
        self.fileRadioButton.setChecked(True)
        self.batchModeCheckBox.setChecked(False)
        self.inputEdit.setText(None)
        self.excludeEdit.setPlainText(None)
        self.trackerEdit.setPlainText(None)
        self.webSeedEdit.setPlainText(None)
        self.pieceSizeComboBox.setCurrentIndex(0)
        self.pieceCountLabel.hide()
        self.commentEdit.setText(None)
        self.privateTorrentCheckBox.setChecked(False)
        self.randomizeInfoHashCheckBox.setChecked(False)
        self.md5CheckBox.setChecked(False)
        self.sourceEdit.setText(None)
        self.torrent = None
        self._statusBarMsg("Ready")

    def get_info(self, torrent):
        t_info = []
        t_info.append(torrent.size)
        t_info.append(len(torrent.files))
        t_info.append(torrent.pieces)
        t_info.append(torrent.piece_size)
        return t_info


def main():
    try:
        qdarktheme.enable_hi_dpi()

        app = QApplication(sys.argv + ["-platform", "windows:darkmode=2"])

        qdarktheme.setup_theme("auto")

        # Hack for https://github.com/5yutan5/PyQtDarkTheme/issues/229
        qpalette = qdarktheme.load_palette("auto")
        theme = _style_loader._detect_system_theme("light")

        if sys.platform == "win32" and theme == "dark":
            qpalette.setColor(QPalette.WindowText, QColorConstants.White)
            QApplication.instance().setPalette(qpalette)

        MainWindow = QtWidgets.QMainWindow()
        ui = TorfGUI()
        ui.setupUi(MainWindow)

        MainWindow.setWindowTitle(PROGRAM_NAME_VERSION)

        ui.loadSettings()
        ui.clipboard = app.clipboard
        app.aboutToQuit.connect(lambda: ui.saveSettings())
        MainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("An error occurred:", str(e))


if __name__ == "__main__":
    main()
