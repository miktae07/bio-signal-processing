// Constants
    const IMAGE_TYPES = ["X-Ray", "MRI", "Ultrasound", "CT"];
    const BODY_PARTS = {
      Ngực: "Chest",
      Não: "Brain",
      Gan: "Liver",
      Bụng: "Abdomen"
    };

    // DOM Elements
    const imageTypeSelect = document.getElementById('imageType');
    const bodyPartSelect = document.getElementById('bodyPart');
    const selectionSpan = document.getElementById('selection');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsDiv = document.getElementById('results');

    // State
    let files = [];

    // Update selection display
    function updateSelection() {
      const imageType = imageTypeSelect.value;
      console.log(imageType);
      const bodyPart = bodyPartSelect.value;
      console.log(bodyPart);
      selectionSpan.textContent = `${imageType} - ${bodyPart}`;
    }

    // Process image
    function processImage(file, index) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imgSrc = e.target.result;
        let resultSrc = imgSrc; // Placeholder for processed image
        let caption = "Kết quả detection";
        let isError = false;

        const imageType = imageTypeSelect.value;
        const bodyPart = bodyPartSelect.value;

        if (imageType === "X-Ray" && bodyPart === "Ngực") {
          caption = "Kết quả X-Ray";
          // Simulate CheXNet prediction
          resultSrc = imgSrc; // Replace with actual processed image
        } else if (imageType === "CT" && bodyPart === "Gan") {
          caption = "Kết quả CT Gan";
          // Simulate CT liver mask prediction
          resultSrc = imgSrc; // Replace with actual processed image
        } else if (imageType !== "MRI") {
          // Simulate YOLO detection
          resultSrc = imgSrc; // Replace with actual processed image
        } else {
          caption = "Không hỗ trợ MRI Não";
          isError = true;
        }

        // Render result
        const resultDiv = document.createElement('div');
        resultDiv.innerHTML = `
          <div>
            <img src="${imgSrc}" alt="Original" class="w-full h-auto">
            <p class="text-center">Ảnh gốc</p>
          </div>
          ${!isError ? `
            <div>
              <img src="${resultSrc}" alt="Result" class="w-full h-auto">
              <p class="text-center">${caption}</p>
            </div>
          ` : `
            <p class="text-red-600">${caption}</p>
          `}
        `;
        resultsDiv.appendChild(resultDiv);
      };
      reader.readAsDataURL(file);
    }

    // Handle analyze button click
    function handleAnalyze() {
      resultsDiv.innerHTML = ''; // Clear previous results
      files.forEach((file, index) => {
        processImage(file, index);
      });
    }

    // Event listeners
    imageTypeSelect.addEventListener('change', updateSelection);
    bodyPartSelect.addEventListener('change', updateSelection);
    fileInput.addEventListener('change', (e) => {
      files = Array.from(e.target.files);
      analyzeBtn.disabled = files.length === 0;
    });
    analyzeBtn.addEventListener('click', handleAnalyze);
    document.getElementById('userSelect').addEventListener('change', (e) => {
      updateUserProfile(e.target.value);
    });

    // Initial setup
    document.addEventListener('DOMContentLoaded', () => {
      updateSelection();
      setGreeting();
      updateUserProfile('user1'); // Default user
    });