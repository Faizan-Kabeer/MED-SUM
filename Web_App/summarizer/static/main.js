document.addEventListener("DOMContentLoaded", function () {
    let form = document.querySelector("form");
    let textarea = document.getElementById("article");
    let counter = document.getElementById("char-counter");
    const fileInput = document.getElementById("uploader");
    const previewContainer = document.getElementById("pdfPreviewContainer");
    const previewFrame = document.getElementById("pdfPreviewFrame");
    const fileError = document.getElementById("file-error");
    const removeFileBtn = document.getElementById("removeFile");

    //renove button
    removeFileBtn.addEventListener("click", function () {
        fileInput.value = ""; // Clear the file input
        previewFrame.src = "";
        previewContainer.classList.add("d-none");
        removeFileBtn.classList.add("d-none");
    });

    // pdf preview
    fileInput.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file && file.type === "application/pdf") {
            const fileURL = URL.createObjectURL(file);
            previewFrame.src = fileURL;
            previewContainer.classList.remove("d-none");
            fileError.style.display = "none";
            removeFileBtn.classList.remove("d-none");
        } else {
            fileError.style.display = "block";
            previewContainer.classList.add("d-none");
            previewFrame.src = "";
            removeFileBtn.classList.add("d-none");
        }
    });

    // Show Spinner When Form is Submitted
    form.addEventListener("submit", function () {
        document.getElementById("loading-spinner").style.display = "block";
    });

    // Live Character Counter for Textarea
    textarea.addEventListener("input", function () {
        counter.innerText = textarea.value.length + " characters";
    });
});

// Copy Summary to Clipboard
function copySummary() {
    let summaryText = document.getElementById("summary-box").innerText;
    navigator.clipboard.writeText(summaryText);
    alert("Summary copied to clipboard!");
}




