from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    jsonify,
    request,
    send_file,
    send_from_directory,
    session
)
from flask_cors import CORS
from werkzeug.utils import secure_filename

try:
    from .auth import (
        create_user,
        authenticate_user,
        get_all_users,
        deactivate_user,
        activate_user
    )
    from .database import (
        initialize_database,
        create_scan,
        save_violation,
        get_all_scans,
        get_scan,
        get_scan_violations,
        get_scan_reports
    )
    from .ocr import (
        extract_text,
        extract_text_data,
        calculate_readability
    )
    from .compliance import check_compliance
    from .reports import generate_pdf_report, generate_word_report
except ImportError:
    from auth import (
        create_user,
        authenticate_user,
        get_all_users,
        deactivate_user,
        activate_user
    )
    from database import (
        initialize_database,
        create_scan,
        save_violation,
        get_all_scans,
        get_scan,
        get_scan_violations,
        get_scan_reports
    )
    from ocr import (
        extract_text,
        extract_text_data,
        calculate_readability
    )
    from compliance import check_compliance
    from reports import generate_pdf_report, generate_word_report


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"

CORS(
    app,
    supports_credentials=True
)

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


initialize_database()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def generate_scan_id():
    return f"SCAN-{uuid4().hex[:10].upper()}"


def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return {
        "id": user_id,
        "username": session.get("username"),
        "role": session.get("role")
    }


def login_required():
    if not session.get("user_id"):
        return False

    return True


def admin_required():
    return (
        session.get("user_id")
        and session.get("role") == "admin"
    )


@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/<path:filename>")
def frontend_file(filename):
    return send_from_directory(
        FRONTEND_DIR,
        filename
    )


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "message": "SIH26034 backend is running"
    })


@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is required"
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password are required"
        }), 400

    user = authenticate_user(
        username,
        password
    )

    if not user:
        return jsonify({
            "success": False,
            "error": "Invalid username or password"
        }), 401

    session.clear()

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]

    return jsonify({
        "success": True,
        "user": user
    })


@app.route("/api/auth/signup", methods=["POST"])
def signup():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is required"
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "error": "Password must be at least 8 characters"
        }), 400

    result = create_user(username, password, "admin")

    if not result["success"]:
        return jsonify(result), 409

    user = authenticate_user(username, password)

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]

    return jsonify({
        "success": True,
        "user": user
    }), 201


@app.route("/api/auth/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


@app.route("/api/auth/me", methods=["GET"])
def me():

    user = current_user()

    if not user:
        return jsonify({
            "success": False,
            "error": "Not authenticated"
        }), 401

    return jsonify({
        "success": True,
        "user": user
    })


@app.route("/api/admin/users", methods=["GET"])
def admin_users():

    if not admin_required():
        return jsonify({
            "success": False,
            "error": "Admin access required"
        }), 403

    return jsonify({
        "success": True,
        "users": get_all_users()
    })


@app.route("/api/admin/users", methods=["POST"])
def admin_create_user():

    if not admin_required():
        return jsonify({
            "success": False,
            "error": "Admin access required"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is required"
        }), 400

    username = data.get(
        "username",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )

    role = data.get(
        "role",
        "inspector"
    )

    allowed_roles = {
        "admin",
        "inspector"
    }

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password are required"
        }), 400

    if role not in allowed_roles:
        return jsonify({
            "success": False,
            "error": "Invalid role"
        }), 400

    result = create_user(
        username,
        password,
        role
    )

    if not result["success"]:
        return jsonify(result), 409

    return jsonify(result), 201


@app.route(
    "/api/admin/users/<int:user_id>/activate",
    methods=["POST"]
)
def admin_activate_user(user_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "error": "Admin access required"
        }), 403

    success = activate_user(user_id)

    if not success:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "User activated"
    })


@app.route(
    "/api/admin/users/<int:user_id>/deactivate",
    methods=["POST"]
)
def admin_deactivate_user(user_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "error": "Admin access required"
        }), 403

    success = deactivate_user(user_id)

    if not success:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "User deactivated"
    })


@app.route("/scan", methods=["POST"])
def scan():

    if not login_required():
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    images = request.files.getlist("images")

    if not images:
        images = request.files.getlist("image")

    if not images:
        return jsonify({
            "success": False,
            "error": "No image uploaded"
        }), 400

    if len(images) > 3:
        return jsonify({
            "success": False,
            "error": "You can upload up to 3 images"
        }), 400

    if any(not image.filename for image in images):
        return jsonify({
            "success": False,
            "error": "No image selected"
        }), 400

    if any(not allowed_file(image.filename) for image in images):
        return jsonify({
            "success": False,
            "error": (
                "Only JPG, JPEG, PNG and WEBP "
                "images are allowed"
            )
        }), 400

    product_name = request.form.get(
        "product_name",
        ""
    )

    product_type = request.form.get(
        "product_type",
        ""
    )

    package_type = request.form.get(
        "package_type",
        ""
    )

    notes = request.form.get(
        "notes",
        ""
    )

    scan_id = generate_scan_id()

    saved_paths = []

    try:
        for index, image in enumerate(images, start=1):
            original_filename = secure_filename(image.filename)
            extension = Path(original_filename).suffix.lower()
            filename = f"{scan_id}-{index}{extension}"
            image_path = UPLOAD_DIR / filename
            image.save(image_path)
            saved_paths.append(image_path)

        extracted_texts = []
        text_data = []
        readability_results = []

        for image_path in saved_paths:
            extracted_texts.append(extract_text(str(image_path)))
            text_data.extend(extract_text_data(str(image_path)))
            readability_results.append(
                calculate_readability(str(image_path))
            )

        extracted_text = "\n\n".join(
            text for text in extracted_texts if text
        )

        confidence_values = [
            result["average_confidence"]
            for result in readability_results
        ]
        average_confidence = round(
            sum(confidence_values) / len(confidence_values),
            2
        )

        if average_confidence >= 80:
            readability_status = "GOOD"
        elif average_confidence >= 60:
            readability_status = "MODERATE"
        else:
            readability_status = "POOR"

        if not any(text_data):
            readability_status = "UNREADABLE"
            average_confidence = 0

        readability = {
            "status": readability_status,
            "average_confidence": average_confidence
        }

        compliance = check_compliance(
            extracted_text,
            readability
        )

        scan_data = {
            "scan_id": scan_id,
            "product_name": product_name,
            "product_type": product_type,
            "package_type": package_type,
            "image_path": "\n".join(
                str(path) for path in saved_paths
            ),
            "extracted_text": extracted_text,
            "overall_status": compliance[
                "overall_status"
            ],
            "compliance_score": compliance[
                "score"
            ],
            "readability_status": readability[
                "status"
            ],
            "readability_confidence": readability[
                "average_confidence"
            ],
            "inspector_id": session.get(
                "user_id"
            ),
            "notes": notes
        }

        database_scan_id = create_scan(
            scan_data
        )

        for result in compliance["results"]:

            if result["status"] in (
                "FAIL",
                "MANUAL REVIEW"
            ):

                save_violation(
                    database_scan_id,
                    result
                )

        return jsonify({
            "success": True,
            "scan_id": scan_id,
            "filename": saved_paths[0].name,
            "filenames": [path.name for path in saved_paths],
            "product_name": product_name,
            "product_type": product_type,
            "package_type": package_type,
            "extracted_text": extracted_text,
            "text_data": text_data,
            "readability": readability,
            "compliance": compliance
        })

    except Exception as error:

        for image_path in saved_paths:
            if image_path.exists():
                image_path.unlink()

        status_code = 503 if "Tesseract OCR" in str(error) else 500

        return jsonify({
            "success": False,
            "error": str(error)
        }), status_code


@app.route("/api/scans", methods=["GET"])
def scans():

    if not login_required():
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    return jsonify({
        "success": True,
        "scans": get_all_scans()
    })


@app.route(
    "/api/scans/<scan_id>",
    methods=["GET"]
)
def scan_details(scan_id):

    if not login_required():
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    scan_data = get_scan(scan_id)

    if not scan_data:
        return jsonify({
            "success": False,
            "error": "Scan not found"
        }), 404

    violations = get_scan_violations(
        scan_id
    )

    reports = get_scan_reports(
        scan_id
    )

    return jsonify({
        "success": True,
        "scan": scan_data,
        "violations": violations,
        "reports": reports
    })


@app.route(
    "/api/reports/pdf",
    methods=["POST"]
)
def create_pdf_report():

    if not login_required():
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Report data is required"
        }), 400

    try:

        file_path = generate_pdf_report(
            data
        )

        return send_file(
            file_path,
            as_attachment=True,
            download_name=Path(
                file_path
            ).name,
            mimetype="application/pdf"
        )

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route(
    "/api/reports/word",
    methods=["POST"]
)
def create_word_report():

    if not login_required():
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Report data is required"
        }), 400

    try:

        file_path = generate_word_report(
            data
        )

        return send_file(
            file_path,
            as_attachment=True,
            download_name=Path(
                file_path
            ).name,
            mimetype=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


if __name__ == "__main__":
     app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )