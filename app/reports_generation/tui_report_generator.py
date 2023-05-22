import json
import os
import re
import socket
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
from stat import S_ISDIR, S_ISREG

import paramiko
import pyperclip
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import (Button, Header, Input, Label, ListItem, ListView,
                             Static, TabbedContent, TabPane, TextLog)

import csv_chart_generator


class Config:
    username = None
    host = None
    ssh_key_path = None
    toolkit_path = None
    remote_path = None
    local_path = None
    reports_path = None
    download_path = None
    copy_report_path = None
    data = None

    @staticmethod
    def load():
        if not os.path.exists("config.json"):
            with open("config.json", "w+"):
                pass
        with open("config.json") as f:
            try:
                Config.data = json.load(f)
            except json.decoder.JSONDecodeError:
                Config.data = {}
            Config.username = Config.data.get("username") or "ubuntu"
            Config.host = Config.data.get("host", "")
            Config.ssh_key_path = Config.data.get("ssh-key-path") or str(Path.home())
            Config.toolkit_path = str(
                Path(Config.data.get("toolkit-path") or Path(__file__).parent.parent.parent.absolute())
            )
            Config.remote_path = Config.data.get("remote-path") or "/home/ubuntu"
            Config.local_path = str(Path(Config.data.get("local-path") or Path(__file__).parent).absolute())
            Config.reports_path = str(Path(Config.data.get("reports-path") or Path(__file__).parent).absolute())
            Config.download_path = str(Path(Config.data.get("download-path") or Path(__file__).parent).absolute())
            Config.copy_report_path = Config.data.get("copy-report-path") and True

    @staticmethod
    def save():
        with open("config.json", "w") as f:
            Config.data["username"] = Config.username
            Config.data["host"] = Config.host
            Config.data["ssh-key-path"] = Config.ssh_key_path
            Config.data["toolkit-path"] = Config.toolkit_path
            Config.data["remote-path"] = Config.remote_path
            Config.data["local-path"] = Config.local_path
            Config.data["reports-path"] = Config.reports_path
            Config.data["download-path"] = Config.download_path
            Config.data["copy-report-path"] = Config.copy_report_path
            json.dump(Config.data, f, indent=2)


class RichLabel(Label):
    _text = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = str(self.renderable)

    def update(self, renderable: RenderableType = "") -> None:
        self.value = self.renderable

    @property
    def value(self):
        return str(self.renderable)

    @value.setter
    def value(self, value):
        self._text = value
        super().update(self._text)


class Configuration(Static):
    class Set(Message):
        def __init__(self, button_id):
            self.button_id = button_id
            super().__init__()

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Horizontal(
                Label("username: ", classes="config-label"),
                Input(Config.username, id="username-input", classes="config-input"),
                Button("Paste from clipboard", id="set-username-btn", classes="right-side-btn"),
                classes="config-field",
            ),
            Horizontal(
                Label("Host: ", classes="config-label"),
                Input(Config.host, id="host-input", classes="config-input"),
                Button("Paste from clipboard", id="set-host-btn", classes="right-side-btn"),
                classes="config-field",
            ),
            Horizontal(
                Label("SSH key path: ", classes="config-label"),
                Input(Config.ssh_key_path, id="ssh-key-path-input", classes="config-input"),
                Button("Set from local", id="set-key-btn", classes="right-side-btn"),
                classes="config-field",
            ),
            Horizontal(
                Label("Toolkit path: ", classes="config-label"),
                Input(Config.toolkit_path, id="toolkit-path-input", classes="config-input"),
                Button("Set from local", id="set-toolkit-btn", classes="right-side-btn"),
                classes="config-field",
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        self.post_message(Configuration.Set(event.button.id))


class ReportComponent(Static):
    last_report_path = None

    def generate_report(self, report):
        try:
            sys.argv.insert(1, str(report))
            csv_chart_generator.main()
            report_path = max(
                (Path(Config.toolkit_path).absolute() / "app" / "results" / "reports").glob("*"),
                key=lambda x: x.stat().st_ctime,
            )
            self.last_report_path = str(report_path)
            Logger.info(f"Report generated to {report_path}")
        except FileNotFoundError as err:
            Logger.error(str(err))
            Logger.error("Check if toolkit path is correct")
        except Exception as err:
            Logger.error(str(err))
        finally:
            sys.argv.pop(1)

    def set_runs_in_yml(self, yml_file, run_1_path, run_2_path, run_3_path=None):
        lines = []
        path_indexes = []
        value_indexes = []
        Logger.warning(f"set: {yml_file}")
        with open(yml_file, "r") as f:
            lines = f.readlines()
            for i, l in enumerate(lines):
                if "fullPath: " in l:
                    path_indexes.append(i)
                    value_indexes.append(l.index(":") + 1)
                if "title: " in l and " (TUI Tool)" not in l:
                    index = l.rindex('"')
                    lines[i] = f"{l[:index]} (TUI Tool){l[index:]}"
        if len(path_indexes) < 2:
            Logger.info("No 'fullPath:' entries found in yml file. Please check .yml file if it is correct.")
        with open(yml_file, "w") as f:
            for i, l in enumerate(lines):
                if i == path_indexes[0]:
                    f.write(f"{l[:value_indexes[0]]} '{run_1_path}'\n")
                elif i == path_indexes[1]:
                    f.write(f"{l[:value_indexes[1]]} '{run_2_path}'\n")
                elif len(path_indexes) > 2 and i == path_indexes[2]:
                    f.write(f"{l[:value_indexes[2]]} '{run_3_path}'\n")
                else:
                    f.write(l)


class PerformanceReportComponent(ReportComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_1_label = RichLabel("not set", id="perf-1-path-label")
        self.path_2_label = RichLabel("not set", id="perf-2-path-label")
        self.copy_button = Button("Copy report path", id="copy-perf-report-btn", classes="center")
        self.copy_button.styles.display = "none"

    def compose(self) -> ComposeResult:
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run without app:"),
                    self.path_1_label,
                ),
                Button("Choose report path", id="perf-1-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run with app:"),
                    self.path_2_label,
                ),
                Button("Choose report path", id="perf-2-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Button("Generate report", id="generate-perf-report-btn", classes="center")
        yield self.copy_button

    def on_button_pressed(self, event):
        if event.button.id == "perf-1-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report without app",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_1_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "perf-2-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report with app",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_2_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "generate-perf-report-btn":
            self.set_runs_in_yml(
                Path(Config.toolkit_path) / "app" / "reports_generation" / "performance_profile.yml",
                self.path_1_label.value,
                self.path_2_label.value,
            )
            self.generate_report(Path(Config.toolkit_path) / "app" / "reports_generation" / "performance_profile.yml")
            self.copy_button.styles.display = "block"
        elif event.button.id == "copy-perf-report-btn":
            pyperclip.copy(self.last_report_path)


class ScaleReportComponent(ReportComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_1_label = RichLabel("not set", id="scale-1-path-label")
        self.path_2_label = RichLabel("not set", id="scale-2-path-label")
        self.path_3_label = RichLabel("not set", id="scale-3-path-label")
        self.copy_button = Button("Copy report path", id="copy-scale-report-btn", classes="center hidden")

    def compose(self) -> ComposeResult:
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run with 1 node:"),
                    self.path_1_label,
                ),
                Button("Choose report path", id="scale-1-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run with 2 nodes:"),
                    self.path_2_label,
                ),
                Button("Choose report path", id="scale-2-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run with 4 nodes:"),
                    self.path_3_label,
                ),
                Button("Choose report path", id="scale-3-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Button("Generate report", id="generate-scale-report-btn", classes="center")
        yield self.copy_button

    def on_button_pressed(self, event):
        if event.button.id == "scale-1-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report with 1 node",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_1_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "scale-2-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report with 2 nodes",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_2_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "scale-3-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report with 4 nodes",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_3_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "generate-scale-report-btn":
            self.set_runs_in_yml(
                Path(Config.toolkit_path) / "app" / "reports_generation" / "scale_profile.yml",
                self.path_1_label.value,
                self.path_2_label.value,
                self.path_3_label.value,
            )
            self.generate_report(Path(Config.toolkit_path) / "app" / "reports_generation" / "scale_profile.yml")
            self.copy_button.styles.display = "block"
        elif event.button.id == "copy-scale-report-btn":
            pyperclip.copy(self.last_report_path)


class BambooReportComponent(ReportComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_1_label = RichLabel("not set", id="bamboo-1-path-label")
        self.path_2_label = RichLabel("not set", id="bamboo-2-path-label")
        self.path_3_label = RichLabel("not set", id="bamboo-3-path-label")
        self.copy_button = Button("Copy report path", id="copy-bamboo-report-btn", classes="center hidden")

    def compose(self) -> ComposeResult:
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run without app:"),
                    self.path_1_label,
                ),
                Button("Choose report path", id="bamboo-1-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run with app:"),
                    self.path_2_label,
                ),
                Button("Choose report path", id="bamboo-2-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Container(
            Horizontal(
                Vertical(
                    Label("Run with app and custom actions:"),
                    self.path_3_label,
                ),
                Button("Choose report path", id="bamboo-3-set", classes="right-side-btn"),
            ),
            classes="run-config",
        )
        yield Button("Generate report", id="generate-bamboo-report-btn", classes="center")
        yield self.copy_button

    def on_button_pressed(self, event):
        if event.button.id == "bamboo-1-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report without app",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_1_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "bamboo-2-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report with app",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_2_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "bamboo-3-set":
            self.add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=Config.reports_path,
                    title="Choose path for report with app and custom actions",
                    caller=self,
                    id="lfb",
                    field_to_set=self.path_3_label,
                    only_dirs=True,
                ),
                before=self,
            )
        elif event.button.id == "generate-bamboo-report-btn":
            self.set_runs_in_yml(
                Path(Config.toolkit_path) / "app" / "reports_generation" / "bamboo_profile.yml",
                self.path_1_label.value,
                self.path_2_label.value,
                self.path_3_label.value,
            )
            self.generate_report(Path(Config.toolkit_path) / "app" / "reports_generation" / "bamboo_profile.yml")
            self.copy_button.styles.display = "block"
        elif event.button.id == "copy-bamboo-report-btn":
            pyperclip.copy(self.last_report_path)


class Logger:
    text_log = None

    def __init__(self, text_log=None):
        if not Logger.text_log:
            Logger.text_log = text_log

    @classmethod
    def info(cls, msg):
        t = Text(str(msg), style=Style(color="white"))
        cls.text_log.write(t)

    @classmethod
    def warning(cls, msg):
        t = Text(str(msg), style=Style(color="yellow"))
        cls.text_log.write(t)

    @classmethod
    def error(cls, msg):
        t = Text(str(msg), style=Style(color="red"))
        cls.text_log.write(t)


class FileBrowser(Static):
    BINDINGS = [Binding("enter", "open", "Open path", show=False)]
    list_view: ListView = None
    path_label = None
    last_click = None
    list_view_id = None

    class Enter(Message):
        def __init__(self, path, list_view, path_label):
            self.path = path
            self.list_view = list_view
            self.path_label = path_label
            super().__init__()

    class GoTo(Message):
        def __init__(self, character, list_view):
            self.character = character
            self.list_view = list_view
            super().__init__()

    def fill_list(self, entries):
        self.list_view.clear()
        self.list_view.append(
            ListItem(RichLabel(".."), name=f"d:{Path(self.path_label.value).parent.as_posix()}", classes="item-dir")
        )
        if entries:
            for entry in sorted(entries, key=str.casefold):
                path = Path(entry[2:]).name
                if entry.startswith("d"):
                    self.list_view.append(ListItem(RichLabel(str(path)), name=entry, classes="item-dir"))
                else:
                    self.list_view.append(ListItem(RichLabel(str(path)), name=entry))

    def get_entries(self, path):
        raise NotImplementedError()

    def center_list(self, item_name):
        for i, item in enumerate(self.list_view.children):
            if Path(item.name[2:]).name == item_name:
                self.list_view.index = i
                self.list_view.scroll_to(0, i - self.list_view.size.height / 2)
                break

    def open_path(self):
        if self.list_view.highlighted_child.name.startswith("d"):
            name_to_center = Path(self.path_label.value).name if self.list_view.index == 0 else ".."
            path_to_open = self.list_view.highlighted_child.name[2:]
            Logger.info(name_to_center)
            self.path_label.value = path_to_open
            self.fill_list(self.get_entries(path_to_open))
            self.center_list(name_to_center)

    def on_key(self, event):
        if event.key == "enter":
            if self.list_view.highlighted_child.name.startswith("d"):
                self.open_path()
        elif event.key == "backspace":
            self.open_path()
        else:
            if event.character and re.match(r"[A-Za-z\d\-._+]", event.character):
                for i, item in enumerate(self.list_view.children):
                    if item.children[0].value.lower().startswith(event.character) and i > self.list_view.index:
                        self.list_view.index = i
                        return
                for i, item in enumerate(self.list_view.children):
                    if item.children[0].value.lower().startswith(event.character):
                        self.list_view.index = i
                        return

    def on_mouse_up(self, event) -> None:
        if self.list_view.highlighted_child.name.startswith("f"):
            return
        if event.button == 1:
            now = datetime.now()
            if self.last_click and now - self.last_click < timedelta(milliseconds=500):
                self.list_view.highlighted_child.styles.color = "lightgrey"
                self.open_path()
                self.last_click = None
            else:
                self.last_click = now

    def set_height(self):
        raise NotImplementedError()

    def on_mount(self, event):
        self.list_view.styles.background = "#35393f"
        self.set_height()

    def on_resize(self, event):
        self.set_height()


class RemoteFileBrowser(FileBrowser):
    class Choice(Message):
        def __init__(self, choice, caller):
            self.choice = choice
            self.caller = caller
            super().__init__()

    list_view_id = "#remote"
    title = "Remote file explorer"

    def __init__(self, *args, **kwargs):
        self.title_label = Label(self.title, classes="center")
        self.list_view = ListView(ListItem(RichLabel(".."), name=".."), id=self.list_view_id[1:])
        self.path_label = RichLabel(Config.remote_path, id="remote-path-label", classes="file-list-label")
        self.download_btn = Button("Download", id="download-btn", classes="file-button")
        self.stop_btn = Button("Stop", id="stop-btn", classes="file-button hidden")
        self.ssh_client = RemoteSsh()
        self.fill_list(self.get_entries(Config.remote_path))
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Vertical(
            self.title_label,
            self.path_label,
            self.list_view,
            self.download_btn,
            self.stop_btn,
            Container(classes="filler"),
            id="remote-file-list",
        )

    def get_entries(self, path):
        try:
            return list_results(self.ssh_client.sftp_client, path)
        except FileNotFoundError as err:
            Logger.warning(f"{err} - {self.path_label.value}")
            self.path_label.value = f"/home/{Config.username}"
            try:
                return list_results(self.ssh_client.sftp_client, self.path_label.value)
            except FileNotFoundError as err:
                Logger.warning(f"{err} - {self.path_label.value}")
                self.path_label.value = "/"
                return list_results(self.ssh_client.sftp_client, self.path_label.value)

    def open_path(self):
        super().open_path()
        Config.remote_path = self.path_label.value
        Config.save()

    def set_height(self):
        self.list_view.styles.height = self.parent.size.height - 14 if self.parent.size.height > 19 else 5


class LocalFileBrowser(FileBrowser):
    class Choice(Message):
        def __init__(self, choice, caller):
            self.choice = choice
            self.caller = caller
            super().__init__()

    class UpdateConfig(Message):
        def __init__(self, config_name):
            self.config_name = config_name
            super().__init__()

    list_view_id = "#local"
    title = "Local file explorer"

    def __init__(self, path, title, caller, field_to_set, only_dirs=False, *args, **kwargs):
        self.title_label = Label(title, classes="center")
        self.list_view = ListView(ListItem(RichLabel(".."), name=".."), id=self.list_view_id[1:])
        if Path(path).is_file():
            path = Path(path).parent
        self.path_label = RichLabel(path, id="local-path-label", classes="file-list-label")
        self.confirm_btn = Button("Confirm", id="confirm-btn", classes="file-button")
        self.cancel_btn = Button("Cancel", id="cancel-btn", classes="file-button")
        self.caller = caller
        self.field_to_set = field_to_set
        self.only_dirs = only_dirs
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.fill_list(sorted(list_local_dir(self.path_label.value), key=str.casefold))
        yield Vertical(
            self.title_label,
            self.path_label,
            self.list_view,
            Horizontal(self.confirm_btn, self.cancel_btn),
            id="local-file-list",
        )

    def open_path(self):
        super().open_path()
        Config.local_path = self.path_label.value
        Config.save()

    def get_entries(self, path):
        return list_local_dir(path)

    def on_button_pressed(self, event):
        selection = self.list_view.highlighted_child.name[2:]
        if self.list_view.index == 0:
            selection = self.path_label.value
        type_ = self.list_view.highlighted_child.name[0]
        if event.button.id != "cancel-btn":
            if self.only_dirs and type_ == "d":
                self.field_to_set.value = selection
                if self.field_to_set.id == "#toolkit-path-input":
                    Config.toolkit_path = selection
                if isinstance(self.caller, ReportComponent):
                    Config.reports_path = self.path_label.value
                if isinstance(self.caller, DownloadComponent):
                    Config.download_path = self.path_label.value
            if not self.only_dirs:
                self.field_to_set.value = selection
                if self.field_to_set.id == "#ssh-key-path-input":
                    Config.ssh_key_path = selection
        Config.save()
        self.caller.remove_class("hidden")
        self.remove()

    def set_height(self):
        self.list_view.styles.height = self.parent.size.height - 7 if self.parent.size.height > 12 else 5


class DownloadComponent(Static):
    class Download(Message):
        def __init__(self, source, dest, stop=False):
            self.source = source
            self.dest = dest
            self.stop = stop
            super().__init__()

    def __init__(self, *args, **kwargs):
        self.connect_btn = Button("Connect", id="connect-btn", classes="center")
        self.disconnect_btn = Button("Disconnect", id="disconnect-btn", classes="center hidden")
        self.filler = Container(classes="filler")
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        path_label = RichLabel(Config.download_path, id="download-path-label", classes="config-label")
        path_label.styles.width = "1fr"
        path_label.styles.content_align_horizontal = "left"
        download_path = Horizontal(
            Label("Download path: ", classes="path-label config-label"),
            path_label,
            Button("Change download path", id="change-download-btn"),
        )
        download_path.styles.height = 3
        download_path.styles.margin = (0, 0, 1, 0)
        yield Vertical(
            download_path,
            self.connect_btn,
            self.disconnect_btn,
            self.filler,
        )

    def on_button_pressed(self, event):
        try:
            if event.button.id == "connect-btn":
                self.connect_btn.add_class("hidden")
                self.disconnect_btn.remove_class("hidden")
                self.remote_file_browser = RemoteFileBrowser(id="rfb")
                self.mount(self.remote_file_browser, after=self.disconnect_btn)
            elif event.button.id == "disconnect-btn":
                self.remote_file_browser.ssh_client.disconnect()
                self.disconnect_btn.add_class("hidden")
                self.connect_btn.remove_class("hidden")
                self.remote_file_browser.remove()
            elif event.button.id == "change-download-btn":
                self.add_class("hidden")
                self.mount(
                    LocalFileBrowser(
                        path=Config.download_path,
                        title="Download path",
                        caller=self,
                        field_to_set=self.query_one("#download-path-label"),
                        only_dirs=True,
                    ),
                    after=self,
                )
            elif event.button.id == "download-btn":
                self.post_message(
                    self.Download(
                        self.query_one("#remote").highlighted_child.name[2:],
                        self.query_one("#download-path-label").value,
                    )
                )
            elif event.button.id == "stop-btn":
                self.post_message(self.Download("", "", stop=True))
        except Exception as err:
            Logger.error(err)
            self.disconnect_btn.add_class("hidden")
            self.connect_btn.remove_class("hidden")


class ChartGenerator(App):
    CSS_PATH = "styles.css"
    TITLE = "Report generator"
    SUB_TITLE = "TUI tool for easier report generation"

    config_file = "config.json"

    def __init__(self, *args, **kwargs):
        self.logger = Logger(TextLog(id="logger"))
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="configuration-tab"):
            with TabPane("Configuration", id="configuration-tab"):
                yield Configuration(id="main-configuration", classes="config")
            with TabPane("Download reports", id="download-tab"):
                yield DownloadComponent(id="download-component")
            with TabPane("Generate report", id="generate-report-tab"):
                with TabbedContent(initial="performance-tab"):
                    with TabPane("Performance report", id="performance-tab"):
                        yield PerformanceReportComponent(id="perf-component")
                    with TabPane("Scale report", id="scale-tab"):
                        yield ScaleReportComponent(id="scale-component")
                    with TabPane("Bamboo report", id="bamboo-tab"):
                        yield BambooReportComponent(id="bamboo-component")
        yield Horizontal(
            Button("Previous step", id="prev-tab-btn", classes="nav-button"),
            Button("Next step", id="next-tab-btn", classes="nav-button"),
            classes="nav-buttons",
        )
        yield self.logger.text_log
        self.logger.text_log.max_lines = 100
        self.logger.text_log.wrap = True

    def on_configuration_set(self, message):
        if message.button_id == "set-username-btn":
            self.query_one("#username-input").value = pyperclip.paste()
        if message.button_id == "set-host-btn":
            self.query_one("#host-input").value = pyperclip.paste()
        elif message.button_id == "set-key-btn":
            self.query_one("#main-configuration").add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=str(Path(self.query_one("#ssh-key-path-input").value).parent),
                    title="Choose ssh key",
                    caller=self.query_one("#main-configuration"),
                    id="lfb",
                    field_to_set=self.query_one("#ssh-key-path-input"),
                ),
                before=self.query_one("#main-configuration"),
            )
        elif message.button_id == "set-toolkit-btn":
            self.query_one("#main-configuration").add_class("hidden")
            self.mount(
                LocalFileBrowser(
                    path=str(Path(self.query_one("#toolkit-path-input").value)),
                    title="Choose toolkit path",
                    caller=self.query_one("#main-configuration"),
                    id="lfb",
                    field_to_set=self.query_one("#toolkit-path-input"),
                    only_dirs=True,
                ),
                before=self.query_one("#main-configuration"),
            )

    def on_button_pressed(self, event):
        if event.button.id == "next-tab-btn":
            tabbed_content: TabbedContent = self.get_child_by_type(TabbedContent)
            if tabbed_content.active == "configuration-tab":
                tabbed_content.active = "download-tab"
            elif tabbed_content.active == "download-tab":
                tabbed_content.active = "generate-report-tab"
            elif tabbed_content.active == "generate-report-tab":
                tabbed_content.active = "configuration-tab"
        elif event.button.id == "prev-tab-btn":
            tabbed_content: TabbedContent = self.get_child_by_type(TabbedContent)
            if tabbed_content.active == "configuration-tab":
                tabbed_content.active = "generate-report-tab"
            elif tabbed_content.active == "download-tab":
                tabbed_content.active = "configuration-tab"
            elif tabbed_content.active == "generate-report-tab":
                tabbed_content.active = "download-tab"

    def on_download_component_download(self, message):
        if message.stop:
            self.stop_event.set()
            self.download_thread.join()
            self.query_one("#stop-btn").add_class("hidden")
            self.query_one("#download-btn").remove_class("hidden")
            return
        remote_dir = message.source
        local_dir = str(Path(message.dest) / Path(message.source).name)
        try:
            os.mkdir(local_dir)
        except OSError as err:
            self.logger.warning(err)
        except Exception as err:
            self.logger.error(err)
        self.stop_event = threading.Event()
        self.download_thread = threading.Thread(target=self.download_dir, args=(remote_dir, local_dir))
        self.download_thread.start()
        self.query_one("#download-btn").add_class("hidden")
        self.query_one("#stop-btn").remove_class("hidden")

    # def on_file_browser_enter(self, message):
    #     if message.path.startswith("f"):
    #         return
    #     path = Path(message.path_label.value)
    #     message.path_label.value = path.parent.as_posix() if message.path == ".." else message.path
    #     self.fill_remote_list() if message.list_view.id == "#remote" else self.fill_local_list(
    #         message.list_view, message.path_label
    #     )
    #     for i, item in enumerate(message.list_view.children):
    #         if Path(item.name[2:]).name == path.name:
    #             message.list_view.index = i
    #             message.list_view.scroll_to(0, i - message.list_view.size.height / 2)

    def on_input_changed(self, message):
        if message.input.id == "username-input":
            Config.username = message.value
        if message.input.id == "host-input":
            Config.host = message.value
        if message.input.id == "ssh-key-path-input":
            Config.ssh_key_path = message.value
        if message.input.id == "toolkit-path-input":
            Config.toolkit_path = message.value
        Config.save()

    def download_dir(self, sftp, remotedir, localdir, call_depth=0):
        self.logger.info(f"Start downloading {remotedir}")
        for entry in sftp.listdir_attr(remotedir):
            if self.stop_event.is_set():
                self.logger.info("Downloading stopped")
                break
            remotepath = remotedir + "/" + entry.filename
            localpath = os.path.join(localdir, entry.filename)
            mode = entry.st_mode
            if S_ISDIR(mode):
                try:
                    self.logger.info(f"mkdir {localpath}")
                    os.mkdir(localpath)
                except OSError as err:
                    self.logger.error(str(err))
                except Exception as err:
                    self.logger.error(str(err))
                self.download_dir(remotepath, localpath, call_depth + 1)
            elif S_ISREG(mode):
                self.logger.info(f"Downloading file {remotepath} to {localpath}")
                try:
                    sftp.get(remotepath, localpath)
                except Exception as err:
                    self.logger.error(str(err))
        if call_depth == 0 and not self.stop_event.is_set():
            self.logger.info("FINISHED")
            self.query_one("#stop-btn").add_class("hidden")
            self.query_one("#download-btn").remove_class("hidden")


class RemoteSsh:
    host = None
    ssh_key = None
    ssh_client = None
    sftp_client = None

    def __init__(self):
            self.host = Config.host
            self.ssh_key = Config.ssh_key_path
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=Config.host,
                username=Config.username,
                key_filename=Config.ssh_key_path,
            )
            self.sftp_client = self.ssh_client.open_sftp()
            self.connected = True

    def disconnect(self):
        self.ssh_client.close()


def list_local_dir(local_path):
    entries = []
    path = Path(local_path)
    for sub_path in path.glob("*"):
        if os.path.isdir(path / sub_path):
            entries.append(f"d:{path / sub_path}")
        else:
            entries.append(f"f:{path / sub_path}")
    return entries


def list_results(sftp, remote_path):
    files = []
    for entry in sftp.listdir_attr(remote_path):
        entry_path = (Path(remote_path) / entry.filename).as_posix()
        if S_ISDIR(entry.st_mode):
            files.append(f"d:{entry_path}")
        else:
            files.append(f"f:{entry_path}")
    return sorted(files)


def download_files(sftp, remote_path):
    files = []
    dir_ = remote_path.split("/")[-1]
    os.mkdir(remote_path.split("/")[-1])
    for entry in sftp.listdir_attr(remote_path):
        entry_path = os.path.join(remote_path, entry.filename)
        if entry.st_mode & 0o170000 != 0o040000:  # Check if the entry is a directory
            files.append(entry_path)
            sftp.get(entry_path, f"{dir_}/{entry_path.split('/')[-1]}")


if __name__ == "__main__":
    Config.load()
    app = ChartGenerator()
    app.run()
