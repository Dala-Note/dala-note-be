from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from ..core.config import Config


class ExportService:

    def __init__(self):
        self.export_dir = Config.EXPORT_DIR

    def export_note_to_pdf(self, note, filename=None):

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_title = "".join(c for c in note.title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            filename = f"note_{note.id}_{safe_title}_{timestamp}.pdf"

        filepath = self.export_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for the 'Flowable' objects
        story = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=30,
            alignment=TA_CENTER
        )

        content_style = ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontSize=12,
            leading=18,
            textColor='#34495e',
            alignment=TA_LEFT,
            spaceAfter=12
        )

        meta_style = ParagraphStyle(
            'CustomMeta',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#7f8c8d',
            alignment=TA_LEFT
        )

        # Add title
        story.append(Paragraph(note.title, title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Add metadata
        created_str = note.created_at.strftime('%B %d, %Y at %I:%M %p') if note.created_at else 'Unknown'
        updated_str = note.updated_at.strftime('%B %d, %Y at %I:%M %p') if note.updated_at else 'Unknown'

        story.append(Paragraph(f"<b>Created:</b> {created_str}", meta_style))
        story.append(Paragraph(f"<b>Last Updated:</b> {updated_str}", meta_style))
        story.append(Spacer(1, 0.3 * inch))

        # Add content (split by newlines and create paragraphs)
        content_lines = note.content.split('\n')
        for line in content_lines:
            if line.strip():
                story.append(Paragraph(line, content_style))
            else:
                story.append(Spacer(1, 0.1 * inch))

        # Build PDF
        doc.build(story)

        return filepath

    def export_multiple_notes_to_pdf(self, notes, filename=None):

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"notes_export_{timestamp}.pdf"

        filepath = self.export_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        story = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=30,
            alignment=TA_CENTER
        )

        note_title_style = ParagraphStyle(
            'NoteTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor='#34495e',
            spaceAfter=15,
            spaceBefore=20
        )

        content_style = ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontSize=12,
            leading=18,
            textColor='#34495e',
            alignment=TA_LEFT,
            spaceAfter=12
        )

        meta_style = ParagraphStyle(
            'CustomMeta',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#7f8c8d',
            alignment=TA_LEFT
        )

        # Add main title
        story.append(Paragraph("Notes Export", title_style))
        story.append(Spacer(1, 0.3 * inch))

        # Add each note
        for idx, note in enumerate(notes, 1):
            # Add note title
            story.append(Paragraph(f"{idx}. {note.title}", note_title_style))

            # Add metadata
            created_str = note.created_at.strftime('%B %d, %Y at %I:%M %p') if note.created_at else 'Unknown'
            story.append(Paragraph(f"<b>Created:</b> {created_str}", meta_style))
            story.append(Spacer(1, 0.1 * inch))

            # Add content
            content_lines = note.content.split('\n')
            for line in content_lines:
                if line.strip():
                    story.append(Paragraph(line, content_style))
                else:
                    story.append(Spacer(1, 0.1 * inch))

            # Add page break between notes (except for the last one)
            if idx < len(notes):
                story.append(PageBreak())

        # Build PDF
        doc.build(story)

        return filepath

