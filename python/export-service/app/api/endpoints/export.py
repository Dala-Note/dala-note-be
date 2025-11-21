from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
from ...core.database import db
from ...models.note import Note
from ...services.export_service import ExportService

export_bp = Blueprint('export', __name__)
export_service = ExportService()


@export_bp.route('/note/<int:note_id>', methods=['POST'])
def export_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)

        # Get optional filename from request (silent=True handles empty body)
        data = request.get_json(silent=True) or {}
        filename = data.get('filename')

        # Generate PDF
        pdf_path = export_service.export_note_to_pdf(note, filename)

        return send_file(
            str(pdf_path),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_path.name
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404 if '404' in str(e) else 500


@export_bp.route('/notes', methods=['POST'])
def export_notes():
    try:
        data = request.get_json(silent=True) or {}
        note_ids = data.get('note_ids', [])
        filename = data.get('filename')

        if not note_ids:
            return jsonify({
                'success': False,
                'error': 'note_ids array is required'
            }), 400

        # Fetch notes
        notes = Note.query.filter(Note.id.in_(note_ids)).all()

        if not notes:
            return jsonify({
                'success': False,
                'error': 'No notes found with the provided IDs'
            }), 404

        # Generate PDF
        pdf_path = export_service.export_multiple_notes_to_pdf(notes, filename)

        return send_file(
            str(pdf_path),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_path.name
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@export_bp.route('/all', methods=['POST'])
def export_all_notes():
    try:
        notes = Note.query.order_by(Note.created_at.desc()).all()

        if not notes:
            return jsonify({
                'success': False,
                'error': 'No notes available to export'
            }), 404

        # Get optional filename from request (silent=True handles empty body)
        data = request.get_json(silent=True) or {}
        filename = data.get('filename')

        # Generate PDF
        pdf_path = export_service.export_multiple_notes_to_pdf(notes, filename)

        return send_file(
            str(pdf_path),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_path.name
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

