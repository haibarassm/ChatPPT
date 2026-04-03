from PIL import Image
import torch
import os

# 设置 CUDA 内存分配策略（需要在使用 CUDA 之前设置）
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:4096"

from transformers import AutoModel, AutoTokenizer
from logger import LOG  # 引入日志模块，用于记录日志

# 延迟加载模型的函数
_model = None
_tokenizer = None


def _load_model():
    """
    延迟加载 MiniCPM 模型
    """
    global _model, _tokenizer
    if _model is None:
        try:
            LOG.info("正在加载 MiniCPM-V 模型...")
            # 先加载到 CPU，确保所有权重都正确初始化
            _model = AutoModel.from_pretrained(
                'openbmb/MiniCPM-V-2_6',
                trust_remote_code=True,
                torch_dtype=torch.float16
            )
            _tokenizer = AutoTokenizer.from_pretrained(
                'openbmb/MiniCPM-V-2_6',
                trust_remote_code=True
            )
            # 然后移到 GPU
            _model = _model.to('cuda')
            _model.eval()  # 设置模型为评估模式

            # 验证模型真的在 GPU 上
            device = next(_model.parameters()).device
            LOG.info(f"MiniCPM-V 模型加载完成，运行设备: {device}")

            if device.type != 'cuda':
                LOG.warning(f"⚠️ 模型未在 GPU 上，当前设备: {device}")
        except Exception as e:
            LOG.error(f"MiniCPM-V 模型加载失败: {e}")
            raise


def get_model():
    """获取模型实例（延迟加载）"""
    global _model, _tokenizer
    if _model is None:
        _load_model()
    return _model, _tokenizer


def release_model():
    """释放模型占用的 GPU 显存"""
    global _model, _tokenizer
    if _model is not None:
        del _model
        _model = None
    if _tokenizer is not None:
        del _tokenizer
        _tokenizer = None
    torch.cuda.empty_cache()
    LOG.info("MiniCPM 模型已释放，显存已清空")


def chat_with_image(image_file, question='描述下这幅图', sampling=False, temperature=0.7, stream=False):
    """
    使用模型的聊天功能生成对图像的回答。

    参数:
        image_file: 图像文件，用于处理的图像。
        question: 提问的问题，默认为 '描述下这幅图'。
        sampling: 是否使用采样进行生成，默认为 False。
        temperature: 采样温度，用于控制生成文本的多样性，值越高生成越多样。
        stream: 是否流式返回响应，默认为 False。

    返回:
        生成的回答文本字符串。
    """
    model, tokenizer = get_model()

    # 打开并转换图像为 RGB 模式
    image = Image.open(image_file).convert('RGB')

    # 创建消息列表，模拟用户和 AI 的对话
    msgs = [{'role': 'user', 'content': [image, question]}]

    # 如果不启用流式输出，直接返回生成的完整响应
    if not stream:
        return model.chat(image=None, msgs=msgs, tokenizer=tokenizer, temperature=temperature)
    else:
        # 启用流式输出，则逐字生成并打印响应
        generated_text = ""
        for new_text in model.chat(image=None, msgs=msgs, tokenizer=tokenizer, sampling=sampling, temperature=temperature, stream=True):
            generated_text += new_text
            print(new_text, flush=True, end='')  # 实时输出每部分生成的文本
        return generated_text  # 返回完整的生成文本

# 主程序入口
if __name__ == "__main__":
    import sys  # 引入 sys 模块以获取命令行参数
    if len(sys.argv) != 2:
        print("Usage: python src/minicpm_v_model.py <image_file>")  # 提示正确的用法
        sys.exit(1)  # 退出并返回状态码 1，表示错误

    image_file = sys.argv[1]  # 获取命令行传入的图像文件路径
    question = 'What is in the image?'  # 定义默认问题
    response = chat_with_image(image_file, question, sampling=True, temperature=0.7, stream=True)  # 调用生成响应函数
    print("\nFinal Response:", response)  # 输出最终响应
