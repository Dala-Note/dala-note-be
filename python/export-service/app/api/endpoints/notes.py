from flask import Blueprint, request, jsonify
from ...core.database import db
from ...models.note import Note

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('', methods=['GET'])
def get_notes():
    try:
        notes = Note.query.order_by(Note.updated_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [note.to_dict() for note in notes],
            'count': len(notes)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        return jsonify({
            'success': True,
            'data': note.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404 if '404' in str(e) else 500


@notes_bp.route('', methods=['POST'])
def create_note():
    try:
        data = request.get_json()

        if not data or not data.get('title') or not data.get('content'):
            return jsonify({
                'success': False,
                'error': 'Title and content are required'
            }), 400

        note = Note(
            title=data['title'],
            content=data['content']
        )

        db.session.add(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': note.to_dict(),
            'message': 'Note created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']

        db.session.commit()

        return jsonify({
            'success': True,
            'data': note.to_dict(),
            'message': 'Note updated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404 if '404' in str(e) else 500


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404 if '404' in str(e) else 500

