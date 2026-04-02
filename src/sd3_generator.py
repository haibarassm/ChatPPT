import torch
from diffusers import StableDiffusion3Pipeline
from PIL import Image
from logger import LOG


class SD3Generator:
    """
    Stable Diffusion 3 图像生成器
    用于在图像相关性不足时生成相关图片
    """
    def __init__(self, model_id="stabilityai/stable-diffusion-3-medium-diffusers"):
        """
        初始化 SD3 生成器

        参数:
            model_id: 模型名称，默认为 medium 版本
                     如有 small 权限可替换为 "stabilityai/stable-diffusion-3-small-diffusers"
        """
        self.model_id = model_id
        self.pipe = None
        self._load_model()

    def _load_model(self):
        """加载 SD3 模型"""
        try:
            LOG.info(f"正在加载 SD3 模型: {self.model_id}")
            self.pipe = StableDiffusion3Pipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16
            )
            # 显存优化
            self.pipe.enable_model_cpu_offload()
            LOG.info("SD3 模型加载完成")
        except Exception as e:
            LOG.error(f"SD3 模型加载失败: {e}")
            raise

    def generate(self, prompt, num_inference_steps=28, guidance_scale=7.0, save_path=None):
        """
        生成图片

        参数:
            prompt: 提示词
            num_inference_steps: 推理步数，默认 28
            guidance_scale: 引导系数，默认 7.0
            save_path: 保存路径，如果为 None 则不保存

        返回:
            image: 生成的 PIL Image 对象
        """
        try:
            LOG.debug(f"开始生成图片，prompt: {prompt}")
            result = self.pipe(
                prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
            image = result.images[0]

            if save_path:
                image.save(save_path)
                LOG.info(f"图片生成完成，已保存至: {save_path}")

            return image
        except Exception as e:
            LOG.error(f"图片生成失败: {e}")
            raise


# 单例模式，避免重复加载模型
_generator_instance = None


def get_sd3_generator():
    """获取 SD3 生成器单例"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = SD3Generator()
    return _generator_instance


if __name__ == "__main__":
    # 测试代码
    generator = get_sd3_generator()
    test_prompt = "a futuristic city, cyberpunk style, highly detailed, 4k"
    image = generator.generate(test_prompt, save_path="output.png")
    print("生成完成 ✅ 已保存为 output.png")
