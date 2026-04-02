import gradio as gr
import os
import re
import time

from config import Config
from chatbot import ChatBot
from content_formatter import ContentFormatter
from content_assistant import ContentAssistant
from image_advisor import ImageAdvisor
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from template_manager import load_template, get_layout_mapping
from layout_manager import LayoutManager
from logger import LOG
from openai_whisper import asr, transcribe
# from minicpm_v_model import chat_with_image
from docx_parser import generate_markdown_from_docx
from workflow_graph import create_workflow


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ChatPPT"

# 实例化 Config，加载配置文件
config = Config()
chatbot = ChatBot(config.chatbot_prompt)
content_formatter = ContentFormatter(config.content_formatter_prompt)
content_assistant = ContentAssistant(config.content_assistant_prompt)
image_advisor = ImageAdvisor(config.image_advisor_prompt)

# 加载 PowerPoint 模板，并获取可用布局
ppt_template = load_template(config.ppt_template)

# 初始化 LayoutManager，管理幻灯片布局
layout_manager = LayoutManager(get_layout_mapping(ppt_template))

# 创建工作流（chatbot + review agent 循环）
workflow = create_workflow(chatbot_prompt_file=config.chatbot_prompt, max_rounds=3)


# 定义生成幻灯片内容的函数（gradio 6.10.0 版本）
def generate_contents(message, history):
    try:
        # gradio 6.10.0 使用 message 字典格式
        # message 包含 {"text": str, "files": list}

        # 初始化一个列表，用于收集用户输入的文本和音频转录
        texts = []

        # 获取文本输入
        text_input = message.get("text", "")
        if text_input:
            texts.append(text_input)

        # 获取上传的文件列表
        files_list = message.get("files", [])

        # 处理上传的文件
        for uploaded_file in files_list:
            LOG.debug(f"[上传文件]: {uploaded_file}")
            # 获取文件的扩展名，并转换为小写
            file_path = uploaded_file.path if hasattr(uploaded_file, 'path') else str(uploaded_file)
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext in ('.wav', '.flac', '.mp3'):
                # 使用 OpenAI Whisper 模型进行语音识别
                audio_text = asr(file_path)
                texts.append(audio_text)
            # 使用 Docx 文件作为素材创建 PowerPoint
            elif file_ext in ('.docx', '.doc'):
                # 调用 generate_markdown_from_docx 函数，获取 markdown 内容
                raw_content = generate_markdown_from_docx(file_path)
                markdown_content = content_formatter.format(raw_content)
                return content_assistant.adjust_single_picture(markdown_content)
            else:
                LOG.debug(f"[格式不支持]: {file_path}")

        # 将所有文本和转录结果合并为一个字符串，作为用户需求
        user_requirement = "需求如下:\n" + "\n".join(texts)
        LOG.info(user_requirement)

        # 使用工作流（chatbot + review agent 循环）生成内容
        result = workflow.run(user_requirement, session_id="gradio_session")
        slides_content = result["content"]

        LOG.info(f"工作流完成，共 {result['rounds']} 轮审查")

        # 不使用反思的答案
        # slides_content =chatbot.chat_with_history(user_requirement)
        return slides_content
    except Exception as e:
        LOG.error(f"[内容生成错误]: {e}")
        # 抛出 Gradio 错误，以便在界面上显示友好的错误信息
        raise gr.Error(f"网络问题，请重试:)")


def handle_image_generate(history):
    try:
        # history 格式: [{"role": ..., "content": ...}, ...]
        if not history:
            raise gr.Error("【提示】请先输入主题内容")

        # 获取最后一条 AI 回复
        last_message = history[-1]
        slides_content = last_message["content"]

        # 如果 content 是列表，查找 assistant 角色的消息
        if isinstance(slides_content, list):
            LOG.info(f"[DEBUG IMAGE] slides_content is list with {len(slides_content)} items")
            # gradio 6.10.0 格式: [{"text": "...", "type": "..."}]
            extracted_texts = []
            for item in slides_content:
                if isinstance(item, dict) and "text" in item:
                    extracted_texts.append(item["text"])
                elif isinstance(item, dict) and "content" in item:
                    content = item["content"]
                    if isinstance(content, list):
                        for msg in content:
                            if isinstance(msg, dict) and "text" in msg:
                                extracted_texts.append(msg["text"])
                            elif hasattr(msg, "content"):
                                extracted_texts.append(str(msg.content))
                            else:
                                extracted_texts.append(str(msg))
                    else:
                        extracted_texts.append(str(content))
                elif hasattr(item, 'content'):
                    extracted_texts.append(str(item.content))
                else:
                    extracted_texts.append(str(item))
            slides_content = "\n".join(extracted_texts)

        # 确保是字符串
        if not isinstance(slides_content, str):
            LOG.error(f"[DEBUG IMAGE] slides_content is not str, type={type(slides_content)}, converting to str")
            slides_content = str(slides_content)

        content_with_images, image_pair = image_advisor.generate_images(slides_content)

        # 更新最后一条消息
        last_message["content"] = content_with_images

        return history
    except Exception as e:
        LOG.error(f"[配图生成错误]: {e}")
        raise gr.Error(f"【提示】未找到合适配图，请重试！")


# 定义处理生成按钮点击事件的函数
def handle_generate(history):
    try:
        LOG.info(f"[DEBUG] history length: {len(history) if history else 0}")
        for i, msg in enumerate(history) if history else []:
            LOG.info(f"[DEBUG] history[{i}]: role={msg.get('role')}, content_type={type(msg.get('content'))}")

        # history 格式: [{"role": ..., "content": ...}, ...]
        if not history:
            raise gr.Error("【提示】请先输入你的主题内容或上传文件")

        # 获取最后一条 AI 回复
        last_message = history[-1]
        LOG.info(f"[DEBUG] last_message: role={last_message.get('role')}, content_type={type(last_message.get('content'))}")
        slides_content = last_message.get("content", "")

        # 如果 content 是列表，需要提取文本
        if isinstance(slides_content, list):
            LOG.info(f"[DEBUG] content is list with {len(slides_content)} items")
            # gradio 6.10.0 格式: [{"text": "...", "type": "..."}]
            extracted_texts = []
            for item in slides_content:
                if isinstance(item, dict) and "text" in item:
                    # gradio 6.10.0 格式
                    extracted_texts.append(item["text"])
                elif hasattr(item, 'content'):  # BaseMessage 对象
                    extracted_texts.append(str(item.content))
                elif isinstance(item, str):
                    extracted_texts.append(item)
                elif isinstance(item, dict):
                    extracted_texts.append(item.get("content", str(item)))
                else:
                    extracted_texts.append(str(item))
            slides_content = "\n".join(extracted_texts)
        elif hasattr(slides_content, 'content'):  # 单个 BaseMessage 对象
            slides_content = str(slides_content.content)

        # 确保是字符串
        if not isinstance(slides_content, str):
            LOG.error(f"[DEBUG] slides_content is not str, type={type(slides_content)}, converting")
            slides_content = str(slides_content)

        LOG.info(f"[DEBUG] final slides_content type: {type(slides_content)}, length: {len(slides_content)}")
        LOG.info(f"[DEBUG] slides_content preview (first 500 chars): {slides_content[:500]}")

        # 解析输入文本，生成幻灯片数据和演示文稿标题
        powerpoint_data, presentation_title = parse_input_text(slides_content, layout_manager)

        # 清理标题，确保作为文件名是安全的
        # 移除或替换不适合作为文件名的字符
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', presentation_title)
        # 移除首尾空格和点
        safe_title = safe_title.strip('. ')
        # 如果为空，使用默认名称
        if not safe_title:
            safe_title = f"presentation_{int(time.time())}"

        # 定义输出的 PowerPoint 文件路径
        output_pptx = f"outputs/{safe_title}.pptx"

        LOG.info(f"[DEBUG] 生成 PPT: title={presentation_title}, safe_title={safe_title}, output={output_pptx}")

        # 生成 PowerPoint 演示文稿
        generate_presentation(powerpoint_data, config.ppt_template, output_pptx)
        return output_pptx
    except Exception as e:
        LOG.error(f"[PPT 生成错误]: {e}")
        raise gr.Error(f"【提示】请先输入你的主题内容或上传文件")


# 创建 Gradio 界面（gradio 6.10.0 版本）
with gr.Blocks(title="ChatPPT") as demo:

    # 添加标题
    gr.Markdown("## ChatPPT")

    # 定义语音（mic）转文本的接口
    # gr.Interface(
    #     fn=transcribe,  # 执行转录的函数
    #     inputs=[
    #         gr.Audio(sources="microphone", type="filepath"),  # 使用麦克风录制的音频输入
    #     ],
    #     outputs="text",  # 输出为文本
    #     flagging_mode="never",  # 禁用标记功能
    # )

    # 创建聊天机器人界面，提示用户输入
    contents_chatbot = gr.Chatbot(
        placeholder="<strong>AI 一键生成 PPT</strong><br><br>输入你的主题内容或上传音频文件",
        height=800,
    )

    # 定义 ChatBot 和生成内容的接口
    gr.ChatInterface(
        fn=generate_contents,  # 处理用户输入的函数
        chatbot=contents_chatbot,  # 绑定的聊天机器人
        multimodal=True  # 支持多模态输入（文本和文件）
    )

    image_generate_btn = gr.Button("一键为 PowerPoint 配图")

    image_generate_btn.click(
        fn=handle_image_generate,
        inputs=contents_chatbot,
        outputs=contents_chatbot,
    )

    # 创建生成 PowerPoint 的按钮
    generate_btn = gr.Button("一键生成 PowerPoint")

    # 监听生成按钮的点击事件
    generate_btn.click(
        fn=handle_generate,  # 点击时执行的函数
        inputs=contents_chatbot,  # 输入为聊天记录
        outputs=gr.File()  # 输出为文件下载链接
    )

# 主程序入口
if __name__ == "__main__":
    # 启动Gradio应用，允许队列功能，并通过 HTTPS 访问
    demo.queue().launch(
        share=False,
        server_name="0.0.0.0",
        # auth=("django", "qaz!@#$") # ⚠️注意：记住修改密码
    )