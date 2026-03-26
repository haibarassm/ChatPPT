"""
UI样式定义
统一深色主题
"""

GITHUB_THEME = """
/* 全局样式 - 深色主题 */
:root {
    --background-fill-primary: #0d1117;
    --background-fill-secondary: #161b22;
    --border-color-primary: #30363d;
    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
}

body {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
}

/* 全局容器 - 统一深色背景 */
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    color: #c9d1d9 !important;
    background-color: #0d1117 !important;
    max-width: 1400px !important;
    margin: auto !important;
    padding-top: 20px !important;
}

/* 覆盖所有可能的白色背景 */
.gradio-container *,
.gradio-container *::before,
.gradio-container *::after {
    box-sizing: border-box;
}

/* 移除所有白色背景 */
.gradio-container .gradio-padded,
.gradio-container .gradio-group,
.gradio-container .gradio-box,
.gradio-container [class*="gradio"] {
    background-color: transparent !important;
}

/* 主容器 */
.main-container {
    display: flex;
    gap: 16px;
    padding: 24px;
    background-color: #0d1117;
    border-radius: 6px;
}

/* 输入区域 */
.input-section {
    background: #161b22 !important;
    padding: 16px;
    border-radius: 6px;
    border: 1px solid #30363d;
}

/* 输出区域 */
.output-section {
    background: #161b22 !important;
    padding: 16px;
    border-radius: 6px;
    border: 1px solid #30363d;
}

/* 标题样式 */
h1, h2, h3, h4, h5, h6 {
    color: #c9d1d9 !important;
    font-weight: 600;
}

h1 {
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.3em;
    font-size: 2em;
    margin-bottom: 16px;
}

h2 {
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.3em;
    font-size: 1.5em;
    margin-top: 24px;
}

h3 {
    font-size: 1.25em;
    margin-top: 16px;
}

/* 主标题行 */
.gradio-container > .gradio-markdown:first-of-type h1,
.gradio-container > div > .gradio-markdown h1 {
    margin-top: 0;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #30363d;
}

/* 中间行布局 - 只设置间距，不干扰flex布局 */
.gradio-row {
    gap: 16px !important;
}

/* 文件操作区域 */
.gradio-column .gradio-markdown {
    margin-bottom: 12px;
}

.gradio-column .gradio-markdown h3 {
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 1.1em;
}

/* Markdown内容样式 */
.markdown-content {
    background-color: #161b22 !important;
    padding: 16px;
    border-radius: 6px;
    border: 1px solid #30363d;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #c9d1d9 !important;
    min-height: 200px;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.3em;
    margin-top: 24px;
    margin-bottom: 16px;
    color: #c9d1d9 !important;
}

.markdown-content h1 { font-size: 2em; }
.markdown-content h2 { font-size: 1.5em; }
.markdown-content h3 { font-size: 1.25em; }

.markdown-content ul,
.markdown-content ol {
    padding-left: 2em;
    margin-bottom: 16px;
}

.markdown-content li {
    color: #8b949e !important;
}

.markdown-content p {
    color: #c9d1d9 !important;
}

.markdown-content img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
}

.markdown-content code {
    background-color: #1f2428 !important;
    color: #c9d1d9 !important;
    padding: 0.2em 0.4em;
    border-radius: 6px;
    font-size: 85%;
}

.markdown-content pre {
    background-color: #161b22 !important;
    padding: 16px;
    border-radius: 6px;
    overflow: auto;
    border: 1px solid #30363d;
}

.markdown-content pre code {
    background-color: transparent !important;
    padding: 0;
}

/* 标签样式 */
.tag {
    display: inline-block;
    padding: 2px 8px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 12px;
    background-color: #1f2428 !important;
    color: #8b949e !important;
    border: 1px solid #30363d;
}

.tag-success {
    background-color: #1f2428 !important;
    color: #3fb950 !important;
    border-color: #30363d;
}

.tag-info {
    background-color: #1f2428 !important;
    color: #58a6ff !important;
    border-color: #30363d;
}

/* 文本框样式 */
textarea, input[type="text"], input[type="password"] {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
}

textarea:focus, input[type="text"]:focus, input[type="password"]:focus {
    border-color: #58a6ff !important;
    outline: none;
    box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3) !important;
}

/* 下载框样式 */
.download-box {
    background-color: #161b22 !important;
    border: 1px solid #238636;
    border-radius: 6px;
    padding: 16px;
    margin-top: 16px;
}

.download-box a {
    color: #3fb950;
    text-decoration: none;
    font-weight: 600;
}

.download-box a:hover {
    text-decoration: underline;
}

/* 强制覆盖所有可能的白色元素 */
div[style*="background: white"],
div[style*="background:#fff"],
div[style*="background:#ffffff"],
div[style*="background-color: white"],
div[style*="background-color:#fff"],
div[style*="background-color:#ffffff"] {
    background: #161b22 !important;
}

/* 覆盖Gradio默认样式 */
.form,
.gradio-form,
.gradio-container .gradio-box {
    background-color: #0d1117 !important;
}

/* 修复可能的白色文字 */
.white-text,
[class*="white"] {
    color: #c9d1d9 !important;
}

/* 分隔线样式 */
hr {
    border-color: #30363d !important;
    margin: 16px 0;
}

/* Group样式 */
.gradio-group {
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    padding: 16px !important;
    background-color: #161b22 !important;
}
"""


HEADER_HTML = """
<div style="display: flex; align-items: center; justify-content: space-between; padding: 16px 0; border-bottom: 1px solid #30363d;">
    <div style="display: flex; align-items: center; gap: 12px;">
        <svg height="32" viewBox="0 0 16 16" version="1.1" width="32" aria-hidden="true">
            <path fill="#c9d1d9" d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v12.5A1.75 1.75 0 0 1 14.25 16H1.75A1.75 1.75 0 0 1 0 14.25ZM7.5 10.75a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 0 1.5h-3.5a.75.75 0 0 1-.75-.75ZM7.5 8a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 0 1.5h-3.5A.75.75 0 0 1 7.5 8Zm-4.25-2.75a.75.75 0 0 0 0 1.5h5.5a.75.75 0 0 0 0-1.5Z"></path>
        </svg>
        <span style="font-size: 20px; font-weight: 600; color: #c9d1d9;">ChatPPT</span>
        <span class="tag tag-info">v0.2</span>
    </div>
    <div>
        <a href="https://github.com" target="_blank" style="color: #8b949e; text-decoration: none;">
            <svg height="20" viewBox="0 0 16 16" version="1.1" width="20" aria-hidden="true">
                <path fill="#8b949e" d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
            </svg>
        </a>
    </div>
</div>
"""

FOOTER_HTML = """
<div style="text-align: center; padding: 24px 0; border-top: 1px solid #30363d; margin-top: 24px; color: #8b949e;">
    <p>Built with ❤️ using <strong>Gradio</strong> | Powered by <strong>LangChain</strong></p>
    <p style="font-size: 12px; margin-top: 8px;">
        <a href="#" style="color: #58a6ff; text-decoration: none;">Documentation</a> ·
        <a href="#" style="color: #58a6ff; text-decoration: none;">GitHub</a>
    </p>
</div>
"""
