"use strict";


// ==========================================
// GLOBAL STATE
// ==========================================

let selectedPhoto = null;
let uploadedPhotoUrl = null;
let detectedFaceShape = null;
let cameraStream = null;
let selectedCategory = "Hairstyle";


// ==========================================
// ELEMENTS
// ==========================================

const photoInput = document.getElementById("photoInput");
const photoPreview = document.getElementById("photoPreview");
const previewPanel = document.getElementById("previewPanel");

const analyzeButton = document.getElementById("analyzeButton");

const analysisPlaceholder =
    document.getElementById("analysisPlaceholder");

const analysisResult =
    document.getElementById("analysisResult");

const faceShapeResult =
    document.getElementById("faceShapeResult");

const analysisMessage =
    document.getElementById("analysisMessage");

const statusMessage =
    document.getElementById("statusMessage");

const recommendationGrid =
    document.getElementById("recommendationGrid");

const recommendationHeading =
    document.getElementById("recommendationHeading");

const recommendationDescription =
    document.getElementById("recommendationDescription");

const cameraPanel =
    document.getElementById("cameraPanel");

const cameraVideo =
    document.getElementById("cameraVideo");

const cameraCanvas =
    document.getElementById("cameraCanvas");


// ==========================================
// STATUS MESSAGE
// ==========================================

function setStatus(message) {
    statusMessage.textContent = message;
}


// ==========================================
// PHOTO SELECTION
// ==========================================

photoInput.addEventListener("change", function () {

    const file = photoInput.files[0];

    if (!file) {
        return;
    }

    if (!file.type.startsWith("image/")) {

        setStatus("Please select a valid image.");

        photoInput.value = "";

        return;
    }

    if (file.size > 10 * 1024 * 1024) {

        setStatus(
            "The image is too large. Maximum size is 10 MB."
        );

        photoInput.value = "";

        return;
    }

    selectedPhoto = file;

    resetAnalysis();

    displayPhoto(file);

    analyzeButton.disabled = false;

    setStatus(
        "Photo selected. Click Analyze My Face to continue."
    );

});


// ==========================================
// DISPLAY PHOTO
// ==========================================

function displayPhoto(file) {

    if (uploadedPhotoUrl) {
        URL.revokeObjectURL(uploadedPhotoUrl);
    }

    uploadedPhotoUrl = URL.createObjectURL(file);

    photoPreview.src = uploadedPhotoUrl;

    previewPanel.classList.remove("hidden");
}


// ==========================================
// RESET ANALYSIS
// ==========================================

function resetAnalysis() {

    detectedFaceShape = null;

    analysisResult.classList.add("hidden");

    analysisPlaceholder.classList.remove("hidden");

    faceShapeResult.textContent = "—";

    analysisMessage.textContent = "";

    recommendationGrid.innerHTML = `
        <div class="empty-recommendations">
            <span>✿</span>
            <h3>Your recommendations will appear here</h3>
            <p>Analyze your photo to explore styles.</p>
        </div>
    `;

    recommendationHeading.textContent =
        "Find your next favorite.";

    recommendationDescription.textContent =
        "Analyze your face and select a beauty category.";

}


// ==========================================
// REMOVE PHOTO
// ==========================================

document.getElementById("removePhoto")
    .addEventListener("click", function () {

        selectedPhoto = null;

        photoInput.value = "";

        if (uploadedPhotoUrl) {

            URL.revokeObjectURL(uploadedPhotoUrl);

            uploadedPhotoUrl = null;
        }

        photoPreview.removeAttribute("src");

        previewPanel.classList.add("hidden");

        analyzeButton.disabled = true;

        resetAnalysis();

        setStatus("Photo removed.");

    });


// ==========================================
// CAMERA ACCESS
// ==========================================

document.getElementById("openCamera")
    .addEventListener("click", async function () {

        if (!navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia) {

            setStatus(
                "Camera access is unavailable in this browser."
            );

            return;
        }

        try {

            cameraStream =
                await navigator.mediaDevices.getUserMedia({

                    video: {
                        facingMode: "user"
                    },

                    audio: false

                });

            cameraVideo.srcObject = cameraStream;

            cameraPanel.classList.remove("hidden");

            setStatus(
                "Camera opened. Position your face and capture."
            );

        } catch (error) {

            console.error("Camera error:", error);

            setStatus(
                "Unable to access the camera. Check browser permissions."
            );

        }

    });


// ==========================================
// CAPTURE PHOTO
// ==========================================

document.getElementById("capturePhoto")
    .addEventListener("click", async function () {

        if (!cameraStream) {

            setStatus("Please open the camera first.");

            return;
        }

        const width = cameraVideo.videoWidth;
        const height = cameraVideo.videoHeight;

        if (!width || !height) {

            setStatus(
                "Camera is starting. Please try again."
            );

            return;
        }

        cameraCanvas.width = width;
        cameraCanvas.height = height;

        const context = cameraCanvas.getContext("2d");

        context.drawImage(
            cameraVideo,
            0,
            0,
            width,
            height
        );

        cameraCanvas.toBlob(async function (blob) {

            if (!blob) {

                setStatus("Unable to capture the photo.");

                return;
            }

            selectedPhoto = new File(
                [blob],
                "camera-photo.jpg",
                {
                    type: "image/jpeg"
                }
            );

            resetAnalysis();

            displayPhoto(selectedPhoto);

            analyzeButton.disabled = false;

            stopCamera();

            cameraPanel.classList.add("hidden");

            setStatus(
                "Photo captured. Click Analyze My Face."
            );

        }, "image/jpeg", 0.92);

    });


// ==========================================
// CLOSE CAMERA
// ==========================================

document.getElementById("closeCamera")
    .addEventListener("click", function () {

        stopCamera();

        cameraPanel.classList.add("hidden");

        setStatus("Camera closed.");

    });


// ==========================================
// STOP CAMERA
// ==========================================

function stopCamera() {

    if (cameraStream) {

        cameraStream.getTracks().forEach(function (track) {

            track.stop();

        });

        cameraStream = null;
    }

    cameraVideo.srcObject = null;
}


// ==========================================
// FACE DETECTION
// ==========================================

analyzeButton.addEventListener("click", async function () {

    if (!selectedPhoto) {

        setStatus("Please upload or capture a photo first.");

        return;
    }

    analyzeButton.disabled = true;

    analyzeButton.textContent = "Analyzing...";

    setStatus("Detecting your face. Please wait.");

    const formData = new FormData();

    formData.append("photo", selectedPhoto);

    try {

        const response = await fetch("/detect-face", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Face detection failed."
            );
        }

        detectedFaceShape =
            data.face_shape || "Oval";

        analysisPlaceholder.classList.add("hidden");

        analysisResult.classList.remove("hidden");

        faceShapeResult.textContent =
            detectedFaceShape;

        analysisMessage.textContent =
            "Your face was detected successfully. " +
            "Explore the beauty categories below.";

        setStatus(
            "Face detected! You can now explore recommendations."
        );

        await loadRecommendations(selectedCategory);

    } catch (error) {

        console.error("Face detection error:", error);

        detectedFaceShape = null;

        setStatus(error.message);

        analysisPlaceholder.classList.remove("hidden");

        analysisResult.classList.add("hidden");

    } finally {

        analyzeButton.disabled = !selectedPhoto;

        analyzeButton.textContent = "Analyze My Face →";

    }

});


// ==========================================
// CATEGORY BUTTONS
// ==========================================

document.querySelectorAll("[data-category]")
    .forEach(function (button) {

        button.addEventListener("click", function () {

            const category =
                button.dataset.category;

            selectCategory(category);

        });

    });


// ==========================================
// SELECT CATEGORY
// ==========================================

function selectCategory(category) {

    selectedCategory = category;

    document.querySelectorAll(".category-tab")
        .forEach(function (tab) {

            tab.classList.toggle(
                "active",
                tab.dataset.category === category
            );

        });

    if (!detectedFaceShape) {

        setStatus(
            "Please upload a photo and analyze your face first."
        );

        document.getElementById("analyzer")
            .scrollIntoView({
                behavior: "smooth"
            });

        return;
    }

    loadRecommendations(category);

    document.getElementById("recommendations")
        .scrollIntoView({
            behavior: "smooth"
        });

}


// ==========================================
// LOAD RECOMMENDATIONS
// ==========================================

async function loadRecommendations(category) {

    if (!detectedFaceShape) {

        setStatus(
            "Analyze your face before viewing recommendations."
        );

        return;
    }

    recommendationGrid.innerHTML = `
        <div class="empty-recommendations">
            <span>✧</span>
            <h3>Finding your styles...</h3>
            <p>Please wait a moment.</p>
        </div>
    `;

    recommendationHeading.textContent =
        category + " recommendations";

    recommendationDescription.textContent =
        "Explore " + category.toLowerCase() +
        " inspiration based on your estimated face shape.";

    try {

        const response = await fetch("/recommend", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                category: category,

                face_shape: detectedFaceShape

            })

        });

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Unable to load recommendations."
            );
        }

        displayRecommendations(
            data.recommendations || []
        );

        setStatus(
            category + " recommendations loaded successfully."
        );

    } catch (error) {

        console.error("Recommendation error:", error);

        recommendationGrid.innerHTML = `
            <div class="empty-recommendations">
                <span>!</span>
                <h3>Unable to load styles</h3>
                <p>${escapeHTML(error.message)}</p>
            </div>
        `;

        setStatus(error.message);

    }

}


// ==========================================
// DISPLAY RECOMMENDATIONS
// ==========================================

function displayRecommendations(recommendations) {

    recommendationGrid.innerHTML = "";

    if (recommendations.length === 0) {

        recommendationGrid.innerHTML = `
            <div class="empty-recommendations">
                <span>✿</span>
                <h3>No styles found</h3>
                <p>Please choose another category.</p>
            </div>
        `;

        return;
    }

    recommendations.forEach(function (style) {

        const card = document.createElement("article");

        card.className = "style-card";

        const image = document.createElement("img");

        image.src = style.image;

        image.alt = style.name;

        image.loading = "lazy";

        image.onerror = function () {

            this.style.display = "none";

        };

        const content = document.createElement("div");

        content.className = "style-card-content";

        const title = document.createElement("h3");

        title.textContent = style.name;

        const reason = document.createElement("p");

        reason.textContent = style.reason;

        const button = document.createElement("button");

        button.type = "button";

        button.className = "style-button";

        button.textContent = "Save as Favorite ♡";

        button.addEventListener("click", function () {

            const isSelected =
                button.classList.toggle("selected");

            button.textContent = isSelected
                ? "Added to Favorites ♥"
                : "Save as Favorite ♡";

        });

        content.appendChild(title);

        content.appendChild(reason);

        content.appendChild(button);

        card.appendChild(image);

        card.appendChild(content);

        recommendationGrid.appendChild(card);

    });

}


// ==========================================
// HTML ESCAPING FOR ERROR MESSAGES
// ==========================================

function escapeHTML(value) {

    return String(value).replace(/[&<>"']/g, function (character) {

        const entities = {

            "&": "&amp;",

            "<": "&lt;",

            ">": "&gt;",

            '"': "&quot;",

            "'": "&#39;"

        };

        return entities[character];

    });

}


// ==========================================
// INITIALIZATION
// ==========================================

window.addEventListener("beforeunload", function () {

    stopCamera();

    if (uploadedPhotoUrl) {

        URL.revokeObjectURL(uploadedPhotoUrl);

    }

});