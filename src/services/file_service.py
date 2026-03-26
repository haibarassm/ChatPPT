"""
文件处理服务
处理上传的文件，提取内容
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from logger import LOG


class FileService:
    """文件处理服务类"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def process_file(self, file_path: str) -> Dict:
        """处理单个文件，提取内容"""
        if not file_path:
            return {"content": "", "images": [], "type": None}

        file_ext = Path(file_path).suffix.lower()
        result = {"content": "", "images": [], "type": file_ext}

        # 图片文件
        if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            result["images"].append(self._save_image(file_path))
            result["type"] = "image"

        # Excel文件
        elif file_ext in ['.xlsx', '.xls']:
            result["content"] = self._read_excel(file_path)
            result["type"] = "table"

        # CSV文件
        elif file_ext == '.csv':
            result["content"] = self._read_csv(file_path)
            result["type"] = "table"

        # 文本文件
        elif file_ext in ['.txt', '.md']:
            result["content"] = self._read_text(file_path)
            result["type"] = "text"

        return result

    def process_files(self, file_paths: List[str]) -> Dict:
        """处理多个文件，合并结果"""
        all_images = []
        all_content = ""

        for file_path in file_paths:
            file_info = self.process_file(file_path)
            all_images.extend(file_info.get("images", []))
            if file_info.get("content"):
                all_content += f"\n\n{file_info['content']}"

        return {"images": all_images, "content": all_content}

    def _save_image(self, file_path: str) -> str:
        """保存图片到uploads目录，返回标准化的相对路径"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 如果同一秒上传多张图片，添加序号
        counter = 1
        while True:
            file_ext = Path(file_path).suffix
            new_filename = f"img_{timestamp}_{counter}{file_ext}"
            new_path = os.path.join(self.upload_dir, new_filename)
            if not os.path.exists(new_path):
                break
            counter += 1

        shutil.copy2(file_path, new_path)

        # 返回标准化的相对路径（使用正斜杠，兼容所有平台）
        return Path(new_path).as_posix()

    def _read_excel(self, file_path: str) -> str:
        """读取Excel文件"""
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_markdown(index=False)
        except Exception as e:
            LOG.error(f"处理Excel文件失败: {e}")
            return ""

    def _read_csv(self, file_path: str) -> str:
        """读取CSV文件"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            return df.to_markdown(index=False)
        except Exception as e:
            LOG.error(f"处理CSV文件失败: {e}")
            return ""

    def _read_text(self, file_path: str) -> str:
        """读取文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            LOG.error(f"处理文本文件失败: {e}")
            return ""
