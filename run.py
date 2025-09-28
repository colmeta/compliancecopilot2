# ==============================================================================
# app.py
# Pearl AI - "CLARITY" Engine v7.0 (Asynchronous Production Edition)
# This is your main web server file.
# ==============================================================================

import os
import base64
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from tasks import run_clarity_analysis  # Import the background task

# --- Flask App Initialization ---
app = Flask(__name__)

# It's good practice to configure CORS more securely for production
# For now, allowing all is fine for development.
CORS(app)

# A secret key is needed for certain Flask features, good to have it.
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a-strong-default-secret-key')

# --- API Endpoints ---

@app.route('/', methods=['GET'])
def clarity_status_root():
    """Simple status endpoint to confirm the server is running."""
    return jsonify({
        "system": "Pearl AI CLARITY Intelligence Platform",
        "version": "7.0 - Asynchronous Edition",
        "status": "FULLY OPERATIONAL",
        "note": "Use the /analyze/start endpoint to submit a new job."
    }), 200


@app.route('/analyze/start', methods=['POST'])
def start_analysis_job():
    """
    Receives user files and a directive, creates a background job for analysis,
    and IMMEDIATELY returns a job ID to the user.
    """
    print("Received new analysis request at /analyze/start")

    directive_text = request.form.get('directive', '')
    knowledge_base_files = request.files.getlist('knowledgeBase')

    if not knowledge_base_files:
        print("Request failed: No files were provided.")
        return jsonify({"error": "No files were provided for analysis."}), 400

    # --- File Pre-processing ---
    # Because we're sending the job to a separate worker process (Celery),
    # we can't just pass the file objects. We must read their contents and serialize them.
    # Base64 encoding is a safe way to turn any file into a string.
    files_data = []
    try:
        for file in knowledge_base_files:
            file_content_bytes = file.read()
            file_content_base64 = base64.b64encode(file_content_bytes).decode('utf-8')
            files_data.append({
                'filename': file.filename,
                'content_type': file.content_type,
                'content_base64': file_content_base64 # The file, now as a string
            })
    except Exception as e:
        print(f"Error reading or encoding files: {e}")
        return jsonify({"error": f"Failed to process uploaded files: {e}"}), 500

    # --- Job Creation ---
    # This is the magic. '.delay()' sends the job to your Celery/Redis queue
    # and immediately continues without waiting for the result.
    print(f"Sending job to Celery worker. Directive: '{directive_text[:50]}...', Files: {len(files_data)}")
    task = run_clarity_analysis.delay(directive_text, files_data)
    
    # --- Instant Response ---
    # Respond to the user with the ID of the background job
    # and a URL they can use to check the job's status.
    status_url = url_for('get_analysis_job_status', job_id=task.id, _external=True)
    print(f"Job {task.id} created. Status URL: {status_url}")
    
    return jsonify({
        "message": "Analysis has been successfully started in the background.",
        "job_id": task.id,
        "status_check_url": status_url
    }), 202 # '202 Accepted' means "I've accepted your request and will process it."


@app.route('/analyze/status/<job_id>', methods=['GET'])
def get_analysis_job_status(job_id):
    """
    Checks the status of a background job. The frontend will call this URL
    repeatedly (e.g., every 5 seconds) to see if the job is done.
    """
    # Use the job_id from the URL to get the task result from Celery/Redis
    task = run_clarity_analysis.AsyncResult(job_id)

    if task.state == 'PENDING':
        # The job is waiting in the queue
        response = {'state': task.state, 'status': 'Job is queued...'}
    elif task.state == 'PROGRESS':
        # (Optional) A running task can report its progress
        response = {'state': task.state, 'status': 'Processing...', 'progress': task.info.get('progress', 0)}
    elif task.state == 'SUCCESS':
        # The job is complete!
        response = {
            'state': task.state,
            'status': 'Analysis Complete',
            'result': task.info.get('result') # This is the final JSON from your AI
        }
    else: # Handle failure
        response = {
            'state': task.state,
            'status': 'Job Failed',
            'error': str(task.info), # This will contain the error message
        }
    
    return jsonify(response)


# --- Application Runner ---
if __name__ == '__main__':
    # It's better to run with Gunicorn in production, but this is fine for local testing.
    print("Starting Pearl AI Flask Server...")
    app.run(host='0.0.0.0', port=8080, debug=True)
