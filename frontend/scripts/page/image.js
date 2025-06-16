import analyzeImage from '../image_processing/image_analyze.js';
import { setGreeting, updateUserProfile, getUnit } from '../utils.js';

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

// Create image element with caption
function createImageWithCaption(src, caption) {
  const container = document.createElement('div');
  container.className = 'flex flex-col items-center px-2';
  const img = document.createElement('img');
  img.src = src;
  img.alt = caption;
  img.className = 'w-[300px] md:w-[400px] h-auto border rounded shadow-lg';
  const p = document.createElement('p');
  p.className = 'text-center mt-2 text-sm md:text-base';
  p.textContent = caption;
  container.appendChild(img);
  container.appendChild(p);
  return container;
}


// Handle analyze button click
async function handleAnalyze() {
  resultsDiv.innerHTML = '';
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

    // Create result-card container
    const resultCard = document.createElement('div');
    resultCard.className = 'result-card';

    // Create image-pair wrapper
    const imagePair = document.createElement('div');
    imagePair.className = 'image-pair flex flex-col md:flex-row gap-4';

    // Add original image
    imagePair.appendChild(createImageWithCaption(imgSrc, 'Ảnh gốc'));

    // Add result image
    if (result.detections && result.detections.length > 0) {
      imagePair.appendChild(createImageWithCaption(result.result_image, `Kết quả ${imageType} ${bodyPart}`));
    } else if (result.mask_image) {
      imagePair.appendChild(createImageWithCaption(result.mask_image, `Mask phân đoạn ${imageType} ${bodyPart}`));
    } else {
      const p = document.createElement('p');
      p.className = 'text-red-600 mt-2';
      p.textContent = 'Không có kết quả từ backend';
      resultCard.appendChild(p);
    }

    // Append image pair to card
    resultCard.appendChild(imagePair);

    // Append detection info if available
    if (result.detections && result.detections.length > 0) {
      const p = document.createElement('p');
      p.className = 'mt-2';
      p.textContent = `Phát hiện: ${result.detections.map(d => `${d[0]} (${(d[1] * 100).toFixed(2)}%)`).join(', ')}`;
      resultCard.appendChild(p);
    }

    resultsDiv.appendChild(resultCard);
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
  updateUserProfile('user1');
});
