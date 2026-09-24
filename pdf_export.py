"""Export the crop management flowchart as a PDF.

The PDF is vector: nodes, arrows and text are drawn as shapes and text, not as a screenshot, so it
stays sharp at any zoom and the text can be searched and copied. The page is sized to the
flowchart rather than to A4, because a management plan is usually far wider than a page and
shrinking it to fit would make the node text unreadable. Zoom in a PDF viewer, or choose "fit to
page" when printing.
"""
from PyQt5.QtCore import QRectF, QSizeF, QMarginsF, Qt
from PyQt5.QtGui import QPdfWriter, QPageSize, QPageLayout, QPainter, QFont, QBrush, QColor

MARGIN = 36          # points, around the whole page
HEADER_GAP = 18      # points, between the header and the flowchart
MAX_PAGE = 14400     # points; the PDF format's largest page side (200 inches)


def export_flowchart_pdf(scene, filename, header_lines=None):
    """Write the scene to `filename` as a single-page PDF.

    header_lines: text printed above the flowchart -- crop name first, in bold, then any details.
    Returns the scale applied to the flowchart: 1.0 unless it exceeded the largest page a PDF
    allows, in which case it is shrunk to fit.
    """
    header_lines = [l for l in (header_lines or []) if l]

    # Only what is drawn, not the empty canvas around it.
    source = scene.itemsBoundingRect()
    if source.isEmpty():
        raise ValueError("The flowchart is empty; there is nothing to export.")
    source.adjust(-10, -10, 10, 10)   # room for arrow heads and selection outlines at the edge

    title_font = QFont()
    title_font.setPointSize(16)
    title_font.setBold(True)
    body_font = QFont()
    body_font.setPointSize(10)
    header_height = 0
    if header_lines:
        header_height = 24 + 15 * (len(header_lines) - 1) + HEADER_GAP

    # Shrink only if the chart would exceed the largest page the PDF format allows.
    scale = min(1.0,
                (MAX_PAGE - 2 * MARGIN) / source.width(),
                (MAX_PAGE - 2 * MARGIN - header_height) / source.height())
    width = max(source.width() * scale, 300) + 2 * MARGIN
    height = source.height() * scale + header_height + 2 * MARGIN

    writer = QPdfWriter(filename)
    # 72 dpi makes one device unit one point, so the scene's pixels map 1:1 onto the page.
    writer.setResolution(72)
    writer.setPageSize(QPageSize(QSizeF(width, height), QPageSize.Point, "", QPageSize.ExactMatch))
    writer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Point)
    writer.setTitle(header_lines[0] if header_lines else "Crop management plan")
    writer.setCreator("CMP Editor")

    # The canvas is grey on screen and the selected node is highlighted; neither belongs on paper.
    old_brush = scene.backgroundBrush()
    selected = scene.selectedItems()
    scene.clearSelection()
    scene.setBackgroundBrush(QBrush(QColor("white")))
    painter = QPainter()
    try:
        if not painter.begin(writer):
            raise IOError(f"Could not write {filename}. Is it open in another program?")
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.fillRect(QRectF(0, 0, width, height), Qt.white)

        y = MARGIN
        for i, line in enumerate(header_lines):
            painter.setFont(title_font if i == 0 else body_font)
            painter.setPen(QColor("black") if i == 0 else QColor("#404040"))
            line_height = 24 if i == 0 else 15
            painter.drawText(QRectF(MARGIN, y, width - 2 * MARGIN, line_height),
                             Qt.AlignLeft | Qt.AlignVCenter, line)
            y += line_height
        if header_lines:
            y += HEADER_GAP

        target = QRectF(MARGIN, y, source.width() * scale, source.height() * scale)
        scene.render(painter, target, source, Qt.KeepAspectRatio)
    finally:
        if painter.isActive():
            painter.end()
        scene.setBackgroundBrush(old_brush)
        for item in selected:
            item.setSelected(True)
    return scale
