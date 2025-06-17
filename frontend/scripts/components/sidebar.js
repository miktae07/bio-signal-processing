// scripts/components/sidebar.js
export function createSidebar() {
	const sidebar = document.createElement('aside');
	sidebar.id = 'sidebar';
	sidebar.className = 'fixed top-0 left-0 w-64 h-full bg-gray-800 text-white p-4';

	sidebar.innerHTML = `
		<h2 id="greeting" class="text-xl font-bold mb-4"></h2>
		<nav>
			<ul>
				<li><a href="index.html" class="block p-2 rounded bg-gray-600">🏠 Trang Chủ</a></li>
				<li><a href="analysis.html" class="block p-2 rounded hover:bg-gray-700">📊 Phân Tích</a></li>
				<li><a href="history.html" class="block p-2 rounded hover:bg-gray-700">🕒 Lịch sử</a></li>
				<li><a href="image.html" class="block p-2 rounded hover:bg-gray-700">📷 Phân tích ảnh</a></li>
			</ul>
		</nav>
		<hr class="my-6">
		<div class="mb-4">
			<label for="userSelect" class="block text-sm font-medium">👤 Chọn Người Dùng</label>
			<select id="userSelect" class="w-full bg-gray-700 text-white border rounded p-2">
				<option value="user1">user1</option>
				<option value="user2">user2</option>
				<option value="user3">user3</option>
			</select>
		</div>
		<div class="mb-4">
			<p><strong>Tên:</strong> <span id="userName">Nguyễn Văn A</span></p>
			<p><strong>Tuổi:</strong> <span id="userAge">30</span></p>
			<p><strong>Địa chỉ:</strong> <span id="userAddress">123 Đường ABC, Quận XYZ, Thành phố ABC</span></p>
			<p><strong>Giới tính:</strong> <span id="userGender">Nam</span></p>
		</div>
	`;

	return sidebar;
}