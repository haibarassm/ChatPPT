"""
内容处理工具模块
提供从各种格式中提取文本内容的公共方法
"""
from logger import LOG


def extract_text_from_content(content, context="") -> str:
    """
    从各种可能的内容格式中提取文本。

    支持的格式：
    - str: 直接返回
    - list: 包含字典或 BaseMessage 对象的列表
    - dict: 包含 "text" 或 "content" 字段

    参数:
        content: 各种可能格式的内容
        context: 调用上下文，用于日志

    返回:
        str: 提取的文本内容
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        LOG.info(f"[DEBUG {context}] content is list with {len(content)} items")
        extracted_texts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                # gradio 6.10.0 格式: {"text": "...", "type": "..."}
                extracted_texts.append(item["text"])
            elif isinstance(item, dict) and "content" in item:
                # 嵌套的 content 字段
                nested = item["content"]
                if isinstance(nested, list):
                    for msg in nested:
                        if isinstance(msg, dict) and "text" in msg:
                            extracted_texts.append(msg["text"])
                        elif hasattr(msg, "content"):
                            extracted_texts.append(str(msg.content))
                        else:
                            extracted_texts.append(str(msg))
                else:
                    extracted_texts.append(str(nested))
            elif hasattr(item, 'content'):
                # BaseMessage 或类似对象
                extracted_texts.append(str(item.content))
            else:
                extracted_texts.append(str(item))
        return "\n".join(extracted_texts)

    if isinstance(content, dict):
        if "text" in content:
            return content["text"]
        if "content" in content:
            return extract_text_from_content(content["content"], context=f"{context}.dict")

    # 其他情况转为字符串
    LOG.warning(f"[DEBUG {context}] unexpected content type: {type(content)}, converting to str")
    return str(content)
