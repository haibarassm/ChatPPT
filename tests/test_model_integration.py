"""
集成测试：测试 MiniCPM 和 SDXL 模型的实际加载和运行
需要 GPU 支持，运行时间较长
"""
import unittest
import os
import sys
from PIL import Image as PILImage

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestModelIntegration(unittest.TestCase):
    """测试模型的实际加载和运行"""

    def test_minicpm_load(self):
        """测试 MiniCPM 模型加载"""
        from minicpm_v_model import get_model

        try:
            model, tokenizer = get_model()
            self.assertIsNotNone(model)
            self.assertIsNotNone(tokenizer)
            print("✓ MiniCPM 模型加载成功")
        except Exception as e:
            self.fail(f"MiniCPM 模型加载失败: {e}")

    def test_minicpm_inference(self):
        """测试 MiniCPM 推理"""
        from minicpm_v_model import chat_with_image

        # 创建一个测试图片
        test_image_path = "images/test_integration.jpg"
        os.makedirs("images", exist_ok=True)

        try:
            img = PILImage.new('RGB', (100, 100), color='red')
            img.save(test_image_path)

            response = chat_with_image(
                test_image_path,
                question="这是什么颜色？",
                sampling=False,
                temperature=0.3
            )
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            print(f"✓ MiniCPM 推理成功: {response[:50]}...")
        finally:
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    def test_sdxl_load(self):
        """测试 SDXL 模型加载"""
        from sd3_generator import get_sd3_generator

        try:
            generator = get_sd3_generator()
            self.assertIsNotNone(generator)
            self.assertIsNotNone(generator.pipe)
            print("✓ SDXL 模型加载成功")
        except Exception as e:
            self.fail(f"SDXL 模型加载失败: {e}")

    def test_sdxl_generate(self):
        """测试 SDXL 图片生成"""
        from sd3_generator import get_sd3_generator

        generator = get_sd3_generator()
        test_save_path = "outputs/test_sdxl_30steps.png"
        os.makedirs("outputs", exist_ok=True)

        image = generator.generate(
            "a red circle on white background",
            num_inference_steps=30,  # 实际使用的步数
            save_path=test_save_path
        )
        self.assertIsNotNone(image)
        self.assertTrue(os.path.exists(test_save_path))
        print(f"✓ SDXL 图片生成成功: {test_save_path}")
        print(f"  图片已保存，查看后请手动删除")

    def test_sdxl_chinese_prompt(self):
        """测试 SDXL 中文提示词问题（预期生成效果差）"""
        from sd3_generator import get_sd3_generator

        generator = get_sd3_generator()
        test_save_path = "outputs/test_sdxl_chinese.png"
        os.makedirs("outputs", exist_ok=True)

        try:
            # 中文提示词 - SDXL 可能无法正确理解
            image = generator.generate(
                "剑气长城 守卫战 场景",  # 中文武侠风格描述
                num_inference_steps=10,
                save_path=test_save_path
            )
            self.assertIsNotNone(image)
            self.assertTrue(os.path.exists(test_save_path))
            print(f"✓ SDXL 中文提示词测试完成（生成效果可能不符合预期）: {test_save_path}")
            print("  提示：SDXL 是英文训练模型，对中文提示词理解有限")
        finally:
            if os.path.exists(test_save_path):
                os.remove(test_save_path)

    def test_sdxl_english_translation(self):
        """测试 SDXL 英文翻译提示词（预期生成效果好）"""
        from sd3_generator import get_sd3_generator

        generator = get_sd3_generator()
        test_save_path = "outputs/test_sdxl_english_30steps.png"
        os.makedirs("outputs", exist_ok=True)

        # 英文翻译版 - SDXL 应该能正确理解
        image = generator.generate(
            "epic battle scene, great wall of china, sword energy, warriors defending, cinematic lighting, fantasy art style",
            num_inference_steps=30,
            save_path=test_save_path
        )
        self.assertIsNotNone(image)
        self.assertTrue(os.path.exists(test_save_path))
        print(f"✓ SDXL 英文提示词测试完成: {test_save_path}")
        print(f"  图片已保存，查看后请手动删除")


if __name__ == "__main__":
    unittest.main(verbosity=2)
