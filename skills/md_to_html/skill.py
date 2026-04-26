"""MdToHtml Skill 实现。"""

from __future__ import annotations

from pathlib import Path

from skills import Skill

from .scripts.convert import convert


class MdToHtmlSkill(Skill):
    """将 Markdown 文档转换为精美 HTML 页面的 Skill。"""

    @property
    def name(self) -> str:
        return "md-to-html"

    @property
    def description(self) -> str:
        return (
            "将 Markdown 文档转换为精美排版的 HTML 页面，"
            "支持多种预设主题、代码高亮、数学公式和目录生成"
        )

    def run(
        self,
        md_text: str,
        style: str = "minimal",
        title: str = "",
        custom_css: str = "",
        math: bool = False,
        toc: bool = False,
        no_highlight: bool = False,
    ) -> str:
        """执行 Markdown 到 HTML 的转换。

        Args:
            md_text: Markdown 原始文本
            style: 预设样式名称
            title: HTML 文档标题
            custom_css: 自定义 CSS 内容
            math: 是否启用数学公式渲染
            toc: 是否生成目录
            no_highlight: 是否禁用代码高亮

        Returns:
            完整的 HTML 文档字符串
        """
        return convert(
            md_text,
            style=style,
            title=title,
            custom_css=custom_css,
            math=math,
            toc=toc,
            no_highlight=no_highlight,
        )

    def run_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        **kwargs,
    ) -> Path:
        """转换 Markdown 文件到 HTML 文件。

        Args:
            input_path: 输入 Markdown 文件路径
            output_path: 输出 HTML 文件路径，默认与输入同名
            **kwargs: 传递给 run() 的其他参数

        Returns:
            输出文件路径
        """
        md_text = Path(input_path).read_text(encoding="utf-8")
        html = self.run(md_text, **kwargs)
        out = Path(output_path or Path(input_path).with_suffix(".html"))
        out.write_text(html, encoding="utf-8")
        return out
