"""
Crucible Upload UI — Flask backend
"""
import logging
import queue
import threading
import tkinter as tk
from tkinter import filedialog

from flask import Flask, jsonify, render_template, request

import backend
from instrument_conf import DEFAULT_BROWSE_DIR

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(funcName)s: %(message)s")

app = Flask(__name__)

INSTRUMENTS = ["titanx", "themis", "team1", "spectre", "team05"] # you can add your instrument here
# Tkinter must run on the main thread. Flask runs in a background thread.
# We use two queues to hand off dialog requests/results between threads.
_tk_root = tk.Tk()
_tk_root.withdraw()
_tk_root.wm_attributes("-topmost", 1)

_browse_request: queue.Queue = queue.Queue()
_browse_result: queue.Queue = queue.Queue()


def _check_browse_queue():
    """Called repeatedly on the main thread via tkinter's event loop."""
    try:
        _browse_request.get_nowait()
        kwargs = {"master": _tk_root, "title": "Select session folder"}
        if DEFAULT_BROWSE_DIR:
            kwargs["initialdir"] = DEFAULT_BROWSE_DIR
        path = filedialog.askdirectory(**kwargs)
        _browse_result.put(path or "")
    except queue.Empty:
        pass
    _tk_root.after(50, _check_browse_queue)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/instruments")
def get_instruments():
    return jsonify(INSTRUMENTS)


@app.get("/api/browse")
def browse():
    # Signal the main thread to open the dialog, then wait for the result.
    _browse_request.put(True)
    path = _browse_result.get(timeout=60)
    return jsonify({"path": path})


@app.post("/api/user/lookup")
def user_lookup():
    email = (request.json or {}).get("email", "").strip()
    if not email:
        return jsonify({"error": "email required"}), 400
    try:
        result = backend.lookup_user_by_email(email)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if not result:
        return jsonify({"error": f"No user found for '{email}'"}), 404
    return jsonify(result)


@app.post("/api/sample/lookup")
def sample_lookup():
    data = request.json or {}
    sample_name = data.get("sample_name") or None
    sample_unique_id = data.get("sample_unique_id") or None
    project_id = data.get("project_id") or None
    if not sample_name and not sample_unique_id:
        return jsonify({"error": "sample_name or sample_unique_id required"}), 400
    try:
        result = backend.lookup_sample(
            sample_name=sample_name,
            sample_unique_id=sample_unique_id,
            project_id=project_id,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if not result:
        return jsonify({"error": "No sample found"}), 404
    return jsonify(result)


@app.post("/api/upload")
def do_upload():
    data = request.json or {}
    required = ["orcid", "project_id", "instrument_name", "session_folder_path"]
    missing = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    try:
        success = backend.upload(
            orcid=data["orcid"].strip(),
            project_id=data["project_id"].strip(),
            instrument_name=data["instrument_name"].strip(),
            sample_unique_id=data.get("sample_unique_id", "").strip(),
            session_folder_path=data["session_folder_path"].strip(),
            comments=data.get("comments", "").strip(),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if success is False:
        return jsonify({"error": "Upload failed — check server logs"}), 500
    return jsonify({"ok": True})


if __name__ == "__main__":
    # Flask runs in a daemon thread; tkinter mainloop holds the main thread.
    flask_thread = threading.Thread(
        target=lambda: app.run(debug=False, port=5000), daemon=True
    )
    flask_thread.start()
    _tk_root.after(50, _check_browse_queue)
    _tk_root.mainloop()
