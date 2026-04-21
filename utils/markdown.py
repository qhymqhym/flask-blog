#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown处理工具模块
"""
import markdown2
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


def markdown_to_html(markdown_text):
    """
    将Markdown文本转换为HTML
    
    Args:
        markdown_text: Markdown格式的文本
    
    Returns:
        转换后的HTML文本
    """
    # 配置Markdown2的扩展
    extras = [
        'fenced-code-blocks',  # 支持代码块
        'tables',  # 支持表格
        'footnotes',  # 支持脚注
        'metadata',  # 支持元数据
        'strike',  # 支持删除线
        'toc',  # 支持目录
        'smarty-pants',  # 支持智能标点
    ]
    
    # 转换Markdown为HTML
    html = markdown2.markdown(
        markdown_text,
        extras=extras
    )
    
    # 处理代码块，添加语法高亮
    import re
    
    # 匹配 fenced code blocks
    code_pattern = re.compile(r'```(\w+)?\n([\s\S]*?)```', re.MULTILINE)
    
    def replace_code_block(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except:
            lexer = get_lexer_by_name('text', stripall=True)
        
        formatter = HtmlFormatter(
            cssclass='codehilite',
            linenos='table',
            lineanchors='line',
            anchorlinenos=True,
            noclasses=False
        )
        
        return highlight(code, lexer, formatter)
    
    # 替换代码块
    html = code_pattern.sub(replace_code_block, html)
    
    return html


def get_pygments_css():
    """
    获取Pygments的CSS样式
    
    Returns:
        Pygments的CSS样式字符串
    """
    formatter = HtmlFormatter(
        cssclass='codehilite',
        linenos='table',
        lineanchors='line',
        anchorlinenos=True,
        noclasses=False
    )
    return formatter.get_style_defs('.codehilite')
