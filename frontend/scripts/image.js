import analyzeImage from './image_processing/image_analyze.js';

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
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');

// State
let files = [];

// Update selection display
function updateSelection() {
  const imageType = imageTypeSelect.value;
  const bodyPart = bodyPartSelect.value;
  const bodyPartVi = Object.keys(BODY_PARTS).find(key => BODY_PARTS[key] === bodyPart);
  selectionSpan.textContent = `${imageType} - ${bodyPartVi}`;
}

// Display image with base64
function displayImage(base64, caption) {
  return `
    <div>
      <img src="${base64}" alt="${caption}" class="w-full h-auto border rounded">
      <p class="text-center mt-2">${caption}</p>
    </div>
  `;
}

// Handle analyze button click
async function handleAnalyze() {
  resultsDiv.innerHTML = ''; // Clear previous results
  errorDiv.classList.add('hidden');
  loadingDiv.classList.remove('hidden');
  analyzeBtn.disabled = true;

  const imageType = imageTypeSelect.value;
  const bodyPart = bodyPartSelect.value;

  for (const file of files) {
    const reader = new FileReader();
    const imgSrcPromise = new Promise(resolve => {
      reader.onload = e => resolve(e.target.result);
      reader.readAsDataURL(file);
    });
    const imgSrc = await imgSrcPromise;

    const result = await analyzeImage(file, imageType, bodyPart);
    loadingDiv.classList.add('hidden');

    if (result.error) {
      errorDiv.textContent = `Lỗi: ${result.error} - ${result.details || ''}`;
      errorDiv.classList.remove('hidden');
      continue;
    }

    const resultDiv = document.createElement('div');
    let resultHtml = displayImage(imgSrc, 'Ảnh gốc');

    if (result.detections && result.detections.length > 0) {
      // Handle YOLO detections
      resultHtml += displayImage(result.result_image, `Kết quả ${imageType} ${bodyPart}`);
      resultHtml += `<p class="mt-2">Phát hiện: ${result.detections.map(d => `${d[0]} (${(d[1] * 100).toFixed(2)}%)`).join(', ')}</p>`;
    } else if (result.mask_image) {
      // Handle Keras mask
      resultHtml += displayImage(result.mask_image, `Mask phân đoạn ${imageType} ${bodyPart}`);
    } else {
      resultHtml += `<p class="text-red-600">Không có kết quả từ backend</p>`;
    }

    resultDiv.innerHTML = resultHtml;
    resultsDiv.appendChild(resultDiv);
  }

  analyzeBtn.disabled = false;
}

// Toggle sidebar
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('-translate-x-full');
}

// Event listeners
imageTypeSelect.addEventListener('change', updateSelection);
bodyPartSelect.addEventListener('change', updateSelection);
fileInput.addEventListener('change', (e) => {
  files = Array.from(e.target.files);
  analyzeBtn.disabled = files.length === 0;
});
analyzeBtn.addEventListener('click', handleAnalyze);
document.getElementById('toggleSidebarBtn').addEventListener('click', toggleSidebar);
document.getElementById('userSelect').addEventListener('change', (e) => {
  updateUserProfile(e.target.value);
});

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
  updateSelection();
  setGreeting();
  updateUserProfile('user1'); // Default user
});