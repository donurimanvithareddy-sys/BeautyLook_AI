import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    url_for
)

from PIL import Image, UnidentifiedImageError

from ai.face_detection import analyze_face


# ==========================================
# FLASK INITIALIZATION
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ==========================================
# UPLOAD FOLDER
# ==========================================

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "ai",
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==========================================
# BEAUTY STYLE DATABASE
# ==========================================

STYLE_DATABASE = {

    "Hairstyle": {

        "Oval": [
            {
                "name": "Soft Waves",
                "file": "wavy.jpg",
                "reason": (
                    "Soft waves create a graceful "
                    "and versatile appearance."
                )
            },
            {
                "name": "Open Hair",
                "file": "open_hair.jpg",
                "reason": (
                    "A simple, elegant option for "
                    "everyday and traditional looks."
                )
            },
            {
                "name": "Traditional Braid",
                "file": "traditional_braid.jpg",
                "reason": (
                    "A beautiful traditional style "
                    "for cultural occasions."
                )
            }
        ],

        "Round": [
            {
                "name": "Messy Braid",
                "file": "messy_braid.jpg",
                "reason": (
                    "A textured braid offers a soft "
                    "and stylish appearance."
                )
            },
            {
                "name": "Open Hair",
                "file": "open_hair.jpg",
                "reason": (
                    "Long open hair is a versatile "
                    "option to explore."
                )
            },
            {
                "name": "Rose Hairstyle",
                "file": "rose_hair.jpg",
                "reason": (
                    "A decorative hairstyle for "
                    "festive occasions."
                )
            }
        ],

        "Long": [
            {
                "name": "Curly Hairstyle",
                "file": "curly.jpg",
                "reason": (
                    "Curls add texture and volume "
                    "to your hairstyle."
                )
            },
            {
                "name": "Soft Waves",
                "file": "wavy.jpg",
                "reason": (
                    "Waves create a soft, balanced "
                    "look."
                )
            },
            {
                "name": "Bridal Bun",
                "file": "bridal_bun.jpg",
                "reason": (
                    "A classic updo for weddings "
                    "and special occasions."
                )
            }
        ]

    },

    "Makeup": {

        "Oval": [
            {
                "name": "Natural Makeup",
                "file": "natural_look.jpg",
                "reason": (
                    "A subtle makeup style for "
                    "everyday use."
                )
            },
            {
                "name": "Glossy Makeup",
                "file": "glossy_look.jpg",
                "reason": (
                    "A fresh, luminous makeup look."
                )
            },
            {
                "name": "Bridal Makeup",
                "file": "bridal_look.jpg",
                "reason": (
                    "A glamorous option for "
                    "weddings and celebrations."
                )
            }
        ],

        "Round": [
            {
                "name": "Natural Makeup",
                "file": "natural_look.jpg",
                "reason": (
                    "A light, natural makeup option."
                )
            },
            {
                "name": "Party Makeup",
                "file": "party_look.jpg",
                "reason": (
                    "A bold look for parties and events."
                )
            },
            {
                "name": "Glossy Makeup",
                "file": "glossy_look.jpg",
                "reason": (
                    "Adds a luminous finish."
                )
            }
        ],

        "Long": [
            {
                "name": "Natural Makeup",
                "file": "natural_look.jpg",
                "reason": (
                    "A simple style for daily wear."
                )
            },
            {
                "name": "Glossy Makeup",
                "file": "glossy_look.jpg",
                "reason": (
                    "A luminous look for special events."
                )
            },
            {
                "name": "Bridal Makeup",
                "file": "bridal_look.jpg",
                "reason": (
                    "A traditional and glamorous option."
                )
            }
        ]

    },

    "Saree": {

        "Oval": [
            {
                "name": "Nivi Draping",
                "file": "nivi_saree.jpg",
                "reason": (
                    "A classic draping style suitable "
                    "for many occasions."
                )
            },
            {
                "name": "Traditional Saree",
                "file": "traditional_saree.jpg",
                "reason": (
                    "A timeless traditional look."
                )
            },
            {
                "name": "Modern Saree",
                "file": "modern_saree.jpg",
                "reason": (
                    "A contemporary option for events."
                )
            }
        ],

        "Round": [
            {
                "name": "Nivi Draping",
                "file": "nivi_saree.jpg",
                "reason": (
                    "A versatile and classic draping style."
                )
            },
            {
                "name": "Bengali Draping",
                "file": "bengali_saree.jpg",
                "reason": (
                    "A traditional style for cultural events."
                )
            },
            {
                "name": "Modern Saree",
                "file": "modern_saree.jpg",
                "reason": (
                    "A contemporary draping option."
                )
            }
        ],

        "Long": [
            {
                "name": "Traditional Saree",
                "file": "traditional_saree.jpg",
                "reason": (
                    "A graceful traditional option."
                )
            },
            {
                "name": "Half Saree",
                "file": "half_saree.jpg",
                "reason": (
                    "A beautiful choice for festive occasions."
                )
            },
            {
                "name": "Bridal Saree",
                "file": "bridal_saree.jpg",
                "reason": (
                    "An elegant option for weddings."
                )
            }
        ]

    },

    "Mehendi": {

        "Oval": [
            {
                "name": "Floral Mehendi",
                "file": "minimal.jpg",
                "reason": (
                    "A delicate design for a subtle look."
                )
            },
            {
                "name": "Arabic Mehendi",
                "file": "arabic.jpg",
                "reason": (
                    "A decorative design with flowing patterns."
                )
            },
            {
                "name": "Mandala Mehendi",
                "file": "mandala.jpg",
                "reason": (
                    "A symmetrical design with detailed patterns."
                )
            }
        ],

        "Round": [
            {
                "name": "Arabic Mehendi",
                "file": "arabic2.jpg",
                "reason": (
                    "A flowing design with decorative details."
                )
            },
            {
                "name": "Mandala Mehendi",
                "file": "mandala2.jpg",
                "reason": (
                    "A detailed circular pattern."
                )
            },
            {
                "name": "Bridal Mehendi",
                "file": "bridal.jpg",
                "reason": (
                    "An intricate design for special occasions."
                )
            }
        ],

        "Long": [
            {
                "name": "Minimal Mehendi",
                "file": "minimal.jpg",
                "reason": (
                    "A simple design for a clean appearance."
                )
            },
            {
                "name": "Arabic Mehendi",
                "file": "arabic.jpg",
                "reason": (
                    "A decorative design with flowing patterns."
                )
            },
            {
                "name": "Bridal Mehendi",
                "file": "bridal2.jpg",
                "reason": (
                    "An elaborate design for weddings."
                )
            }
        ]

    }

}


# ==========================================
# IMAGE FOLDER MAPPING
# ==========================================

CATEGORY_FOLDERS = {
    "Hairstyle": "hairstyles",
    "Makeup": "makeup",
    "Saree": "saree",
    "Mehendi": "mehendi"
}


# ==========================================
# HOMEPAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# PHOTO UPLOAD AND FACE DETECTION
# ==========================================

@app.route("/detect-face", methods=["POST"])
def detect_face_route():

    if "photo" not in request.files:
        return jsonify({
            "success": False,
            "message": "Please upload a photo."
        }), 400

    photo = request.files["photo"]

    if not photo or photo.filename == "":
        return jsonify({
            "success": False,
            "message": "Please select a photo."
        }), 400

    try:
        # Validate and normalize the uploaded image.
        image = Image.open(photo.stream)

        if image.format not in ("JPEG", "PNG", "WEBP"):
            return jsonify({
                "success": False,
                "message": (
                    "Please upload a JPG, PNG, "
                    "or WEBP image."
                )
            }), 400

        image = image.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"

        image_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        image.save(
            image_path,
            format="JPEG",
            quality=90
        )

    except (UnidentifiedImageError, OSError, ValueError):
        return jsonify({
            "success": False,
            "message": "The uploaded file is not a valid image."
        }), 400

    try:
        result = analyze_face(image_path)

    except Exception as error:
        print("Face detection error:", error)

        return jsonify({
            "success": False,
            "message": "Face detection failed."
        }), 500

    if not result.get("detected"):
        return jsonify({
            "success": False,
            "detected": False,
            "message": result.get(
                "message",
                "No face detected."
            )
        }), 400

    return jsonify({
        "success": True,
        "detected": True,
        "message": "Face detected successfully.",
        "face_shape": result["face_shape"],
        "photo_url": url_for(
            "uploaded_photo",
            filename=filename
        )
    })


# ==========================================
# SERVE UPLOADED PHOTO
# ==========================================

@app.route("/uploads/<filename>")
def uploaded_photo(filename):

    # Only serve filenames matching our UUID format.
    if not filename.endswith(".jpg"):
        return jsonify({
            "error": "Invalid filename."
        }), 400

    if not (
        len(filename) == 36
        and filename[:-4].isalnum()
    ):
        return jsonify({
            "error": "Invalid filename."
        }), 400

    from flask import send_from_directory

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ==========================================
# STYLE RECOMMENDATIONS
# ==========================================

@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json(silent=True) or {}

    category = data.get("category", "")
    face_shape = data.get("face_shape", "Oval")

    if category not in CATEGORY_FOLDERS:
        return jsonify({
            "success": False,
            "message": "Please select a valid category."
        }), 400

    if face_shape not in ("Oval", "Round", "Long"):
        face_shape = "Oval"

    recommendations = STYLE_DATABASE[category].get(
        face_shape,
        STYLE_DATABASE[category]["Oval"]
    )

    folder = CATEGORY_FOLDERS[category]

    result = []

    for style in recommendations:

        result.append({
            "name": style["name"],
            "reason": style["reason"],
            "image": url_for(
                "static",
                filename=(
                    f"images/{folder}/{style['file']}"
                )
            )
        })

    return jsonify({
        "success": True,
        "category": category,
        "face_shape": face_shape,
        "recommendations": result
    })


# ==========================================
# APPLICATION START
# ==========================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )