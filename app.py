from flask import render_template, request, session, Blueprint, send_from_directory, jsonify
from captions import captionize
from subprocess import call
from uuid import uuid4
from json import dumps

app = Blueprint("app", __name__)

@app.route("/", methods=["GET"])
def index():
    # Give the user a session id if they don't have one already
    if not "id" in session:
        session["id"] = str(uuid4())
    return render_template("index.html")

@app.route("/file", methods=["POST"])
def file():
    # Upload the analyzed video to the server and return its name
    return jsonify(url=upload(request.files["vid"], request.files["srt"], request.form["extension"]))

@app.route("/uploads/<user>/<filename>", methods=["GET"])
def send_file(user, filename):
    return send_from_directory("uploads/" + user, filename)

def upload(vid, srt, extension):
    if vid:
        # Ensure the user has a file directory
        call(["php", "files.php", dumps({"task" : "create", "user" : session["id"]})])

        # Generate random file names
        vid_path = "uploads/" + session["id"] + "/" + str(uuid4()) + "." + extension
        out_path = "uploads/" + session["id"] + "/" + str(uuid4()) + ".mp4"
        srt_path = "uploads/" + session["id"] + "/" + str(uuid4()) + ".srt"

        # Write the input files
        with open(vid_path, "wb") as f:
            f.write(vid.read())
        with open(srt_path, "wb") as f:
            f.write(srt.read())

        call(["php", "files.php", dumps({"task" : "check", "user" : session["id"]})])

        # Add the captions
        captionize(vid_path, srt_path, out_path)

        # Remove the input files
        call(["php", "files.php", dumps({"task" : "remove", "files" : [vid_path, srt_path], "user" : session["id"]})])

        # Return location of file
        return out_path
