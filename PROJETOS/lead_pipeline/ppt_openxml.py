from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable
from xml.etree import ElementTree as ET
import zipfile

from .normalization import strip_accents


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P_NS, "a": A_NS}
SLIDE_NAME_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")


@dataclass(frozen=True)
class TextShape:
    text: str
    normalized_text: str
    x: int
    y: int
    width: int
    height: int
    shape_name: str

    @property
    def center_x(self) -> float:
        return self.x + (self.width / 2)

    @property
    def center_y(self) -> float:
        return self.y + (self.height / 2)


@dataclass(frozen=True)
class ExtractedSlide:
    slide_index: int
    shapes: list[TextShape]
    combined_text: str
    normalized_text: str


def normalize_ppt_text(value: str) -> str:
    text = strip_accents(str(value or ""))
    text = text.lower()
    text = (
        text.replace("’", "'")
        .replace("´", "'")
        .replace("`", "'")
        .replace("–", "-")
        .replace("—", "-")
    )
    text = re.sub(r"[^a-z0-9+%$]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_presentation(ppt_path: Path) -> list[ExtractedSlide]:
    slides: list[ExtractedSlide] = []
    with zipfile.ZipFile(ppt_path) as ppt_zip:
        slide_names = sorted(
            (
                (int(match.group(1)), member_name)
                for member_name in ppt_zip.namelist()
                if (match := SLIDE_NAME_RE.match(member_name))
            ),
            key=lambda item: item[0],
        )

        for slide_number, member_name in slide_names:
            root = ET.fromstring(ppt_zip.read(member_name))
            shapes = list(_iter_text_shapes(root))
            combined_text = "\n".join(shape.text for shape in shapes if shape.text).strip()
            slides.append(
                ExtractedSlide(
                    slide_index=slide_number,
                    shapes=shapes,
                    combined_text=combined_text,
                    normalized_text=normalize_ppt_text(combined_text),
                )
            )

    return slides


def _iter_text_shapes(root: ET.Element) -> Iterable[TextShape]:
    shape_tree = root.find("./p:cSld/p:spTree", NS)
    if shape_tree is None:
        return []
    return list(_walk_shape_nodes(shape_tree))


def _walk_shape_nodes(node: ET.Element) -> Iterable[TextShape]:
    for child in node:
        if child.tag == f"{{{P_NS}}}sp":
            text_shape = _parse_shape(child)
            if text_shape is not None:
                yield text_shape
        elif child.tag == f"{{{P_NS}}}grpSp":
            yield from _walk_shape_nodes(child)


def _parse_shape(node: ET.Element) -> TextShape | None:
    text = _shape_text(node)
    if not text:
        return None

    shape_name = _shape_name(node)
    x, y, width, height = _shape_bounds(node)
    return TextShape(
        text=text,
        normalized_text=normalize_ppt_text(text),
        x=x,
        y=y,
        width=width,
        height=height,
        shape_name=shape_name,
    )


def _shape_text(node: ET.Element) -> str:
    text_nodes = [item.text.strip() for item in node.findall(".//a:t", NS) if item.text and item.text.strip()]
    return " ".join(text_nodes).strip()


def _shape_name(node: ET.Element) -> str:
    c_nv_pr = node.find("./p:nvSpPr/p:cNvPr", NS)
    if c_nv_pr is None:
        return ""
    return c_nv_pr.attrib.get("name", "")


def _shape_bounds(node: ET.Element) -> tuple[int, int, int, int]:
    xfrm = node.find("./p:spPr/a:xfrm", NS)
    if xfrm is None:
        return 0, 0, 0, 0
    off = xfrm.find("./a:off", NS)
    ext = xfrm.find("./a:ext", NS)
    if off is None or ext is None:
        return 0, 0, 0, 0
    return (
        int(off.attrib.get("x", "0")),
        int(off.attrib.get("y", "0")),
        int(ext.attrib.get("cx", "0")),
        int(ext.attrib.get("cy", "0")),
    )
