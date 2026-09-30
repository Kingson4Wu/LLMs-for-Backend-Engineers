"""Independent EPUB3 exporter. Pandoc and rsvg-convert are the only dependencies."""
import json
import subprocess
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from publication import parse_args, prepare, finish, write_manifest
from watermark import append_provenance, provenance_line


ACCESSIBILITY_SUMMARIES = {
    "zh-Hans": (
        "本版本提供可重排的文本内容、结构化目录与导航、图中提供的替代文本，"
        "并记录默认阅读顺序。该说明不宣称符合 EPUB Accessibility 或 WCAG；"
        "仍应在具体阅读器和辅助技术中评估。"
    ),
    "en": (
        "This reflowable edition provides textual content, structural navigation and a table of contents, "
        "alternative text supplied with figures, and metadata for the default reading order. It does not "
        "claim EPUB Accessibility or WCAG conformance; assess it in specific reading systems and assistive technology."
    ),
}

OPF_NAMESPACE = "http://www.idpf.org/2007/opf"
ACCESSIBILITY_PROPERTIES = {
    "schema:accessMode": ["textual"],
    "schema:accessibilityFeature": [
        "alternativeText",
        "readingOrder",
        "structuralNavigation",
        "tableOfContents",
    ],
    "schema:accessibilityHazard": ["none"],
}
SUMMARY_PROPERTY = "schema:accessibilitySummary"


def ensure_accessibility_metadata(epub: Path, summary: str) -> bool:
    """Normalize EPUB accessibility OPF fields that older Pandoc releases omit.

    Pandoc has varied in how it maps ``accessibilitySummary`` metadata across
    releases. Keep its ordinary metadata path, then make the EPUB3 OPF contract
    exact without changing any other package member.
    """
    with zipfile.ZipFile(epub) as archive:
        members = [(entry, archive.read(entry.filename)) for entry in archive.infolist()]
    opf_name = next((entry.filename for entry, _ in members if entry.filename.endswith(".opf")), None)
    if opf_name is None:
        raise ValueError(f"EPUB has no OPF package document: {epub}")
    original = next(data for entry, data in members if entry.filename == opf_name)
    root = ET.fromstring(original)
    metadata = root.find(f"{{{OPF_NAMESPACE}}}metadata")
    if metadata is None:
        raise ValueError(f"EPUB OPF has no metadata element: {epub}")
    desired = {**ACCESSIBILITY_PROPERTIES, SUMMARY_PROPERTY: [summary]}
    existing = {
        property_name: [
            (node.text or "") for node in metadata.findall(f"{{{OPF_NAMESPACE}}}meta")
            if node.get("property") == property_name
        ]
        for property_name in desired
    }
    if existing == desired:
        return False
    for node in list(metadata):
        if node.tag == f"{{{OPF_NAMESPACE}}}meta" and node.get("property") in desired:
            metadata.remove(node)
    for property_name, values in desired.items():
        for value in values:
            node = ET.SubElement(metadata, f"{{{OPF_NAMESPACE}}}meta", {"property": property_name})
            node.text = value
    ET.register_namespace("", OPF_NAMESPACE)
    updated = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with tempfile.NamedTemporaryFile(dir=epub.parent, suffix=".epub", delete=False) as temporary:
        temp_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temp_path, "w") as archive:
            for entry, data in members:
                archive.writestr(entry, updated if entry.filename == opf_name else data)
        temp_path.replace(epub)
    finally:
        temp_path.unlink(missing_ok=True)
    return True


def main():
    args = parse_args('Export EPUB3 with internal navigation and MathML.')
    book, source, meta, work, ast = prepare(args, 'epub')
    document = json.loads(ast.read_text(encoding='utf-8'))
    append_provenance(document, meta['language'])
    ast.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
    summary = ACCESSIBILITY_SUMMARIES[meta["language"]]
    extra = [
        '-t', 'epub3', '--mathml', '--css', str(book / 'styles/publication-epub.css'),
        '-M', f'rights={provenance_line(meta["language"])}',
        '-M', f'accessibilitySummary={summary}',
    ]
    if meta.get('cover_image'):
        cover = source / meta['cover_image']
        if not cover.exists():
            cover = book / meta['cover_image']
        if cover.suffix == '.svg':
            png = work / 'cover.png'
            subprocess.run(['rsvg-convert','-w','1600','-o',str(png),str(cover)],check=True)
            cover = png
        extra += ['--epub-cover-image',str(cover)]
    output = finish(book,meta,'epub',args,ast,extra)
    if ensure_accessibility_metadata(output, summary):
        provenance = json.loads((ast.parent / 'provenance.json').read_text(encoding='utf-8'))
        write_manifest(book, args.locale, output, provenance)

if __name__ == '__main__':
    main()
