#!/usr/bin/env python
"""
HylReg-RAG: 检索增强生成系统
主入口点
"""

import sys

from src.cli.cli_interface import main as cli_main
from src.core.demo import run_demo


def main():
    """
    主函数
    """
    if len(sys.argv) > 1:
        # 如果有参数，使用CLI接口
        # 重新整理sys.argv，去除第一个元素，然后调用cli_main
        original_argv = sys.argv[:]
        sys.argv = [original_argv[0]] + original_argv[1:]
        cli_main()
    else:
        # 如果没有参数，运行演示
        run_demo()


if __name__ == "__main__":
    main()
