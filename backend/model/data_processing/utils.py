# Remove this line:
from utils.utils import map_lang

# Implement the function directly:
def map_lang(class_name: str) -> str:
    """Map English class names to Vietnamese"""
    lang_map = {
        'N': 'Nhịp bình thường',
        'S': 'Nhịp ngoại tâm thu thất trên',
        'V': 'Nhịp ngoại tâm thu thất',
        'F': 'Nhịp hợp nhất',
        'Q': 'Nhịp không xác định'
    }
    return lang_map.get(class_name, class_name)