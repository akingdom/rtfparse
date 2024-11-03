#!/usr/bin/env python

import io
import logging
from rtfparse import entities
from rtfparse.renderers import Renderer

# Setup logging
logger = logging.getLogger(__name__)

class MarkdownRenderer(Renderer):
    def __init__(self) -> None:
        super().__init__()
        self.ignore_rtf = False
        self.render_word_func = {
            "par": self.newline,
            "line": self.newline,
            "tab": self.tab,
            "b": self.bold,
            "i": self.italic,
            "ul": self.underline,
            "link": self.hyperlink
        }
        self.ignore_groups = {
            "fonttbl",
            "colortbl",
            "generator",
            "formatConverter",
            "pntext",
            "pntxta",
            "pntxtb"
        }

    def ignore_rtf_toggle(self, cw: entities.Control_Word) -> str:
        if cw.parameter == "" or cw.parameter == 1:
            self.ignore_rtf = True
        elif cw.parameter == 0:
            self.ignore_rtf = False
        return ""

    def newline(self, cw: entities.Control_Word) -> str:
        return "\n\n" if not self.ignore_rtf else ""

    def tab(self, cw: entities.Control_Word) -> str:
        return "\t" if not self.ignore_rtf else ""

    def bold(self, cw: entities.Control_Word) -> str:
        return "**"  # Markdown bold syntax

    def italic(self, cw: entities.Control_Word) -> str:
        return "_"  # Markdown italic syntax

    def underline(self, cw: entities.Control_Word) -> str:
        # Markdown has no direct underline, so this can be customized
        return ""  # Skip underline or use <u>text</u> in HTML-style Markdown

    def hyperlink(self, cw: entities.Control_Word) -> str:
        # Return hyperlink format, if any link text is found it would be handled in a separate text render
        return "["

    def render_symbol(self, item: entities.Control_Symbol, file: io.TextIOWrapper) -> None:
        if not self.ignore_rtf:
            if item.text == "~":  # Non-breaking space
                file.write("\u00a0")
            elif item.text == "_":  # Non-breaking hyphen
                file.write("\u2011")
            else:
                file.write(item.text)

    def render(self, parsed: entities.Group, file: io.TextIOWrapper) -> None:
        for item in parsed.structure:
            if isinstance(item, entities.Group):
                if item.name not in self.ignore_groups:
                    self.render(item, file)
            elif isinstance(item, entities.Control_Word):
                try:
                    file.write(self.render_word_func[item.control_name](item))
                except KeyError:
                    pass
            elif isinstance(item, entities.Control_Symbol):
                self.render_symbol(item, file)
            elif isinstance(item, entities.Plain_Text):
                if not self.ignore_rtf:
                    file.write(item.text)
            else:
                pass

if __name__ == "__main__":
    pass
