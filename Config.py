from collections import namedtuple
from xml.etree import ElementTree
from typing import *
import os
shortcuts = namedtuple("shortcuts", "label_text, icon_path, command")


class Storage:
    def __init__(self, script_path: str):
        self.root_dir = os.path.dirname(script_path)
        self.config_dir = os.path.expanduser(os.path.normpath("~/.desktop_shortcuts"))
        self.default_file = os.path.join(self.root_dir, os.path.normpath("Data/default.xml"))
        self.config_path = os.path.join(self.config_dir, "userconfig.xml")
        self.encoding = "utf-8"
        self.element_tree: Optional[ElementTree.ElementTree] = None

    def get_default_data(self) -> Optional[str]:
        try:
            with open(self.default_file, "r", encoding=self.encoding) as file:
                data = file.read()
        except OSError:
            return None
        else:
            return data

    def init_files(self) -> bool:
        """Attempts to create the missing configuration files with default data. A bool is returned to indicate if the
        attempt was successful."""
        default_data = self.get_default_data()
        if default_data is None:
            return False
        try:
            if not os.path.isdir(self.config_dir):
                os.mkdir(self.config_dir)
            with open(self.config_path, "w", encoding=self.encoding) as file:
                file.write(default_data)
        except (OSError, NotImplementedError):
            return False
        else:
            return True

    def init_xml_data(self) -> bool:
        if not os.path.isfile(self.config_path) and not self.init_files():
            return False  # Config files are missing, and the attempt to create them failed.
        try:
            self.element_tree = ElementTree.parse(self.config_path)
        except (OSError, ElementTree.ParseError):
            return False
        else:
            return True

    def get_setting(self, name: str) -> str:
        return self.element_tree.find("./settings/{}".format(name)).text

    def get_shortcut_data(self) -> Tuple[shortcuts, ...]:
        return tuple(shortcuts(label_text=s.attrib["label_text"], icon_path=s.attrib["icon_path"], command=s.text)
                     for s in self.element_tree.find("./shortcuts"))
