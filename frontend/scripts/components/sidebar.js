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
	`;

	return sidebar;
}