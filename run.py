#!/usr/bin/env python
"""
HylReg-RAG 项目入口脚本
提供统一的命令行接口来运行不同组件
"""

import argparse

from src.core.demo import run_demo


def run_cli():
    """运行命令行接口"""
    from src.cli.cli_interface import main as cli_main
    cli_main()


def run_api(host: str, port: int, reload: bool):
    """运行API服务器"""
    import uvicorn

    uvicorn.run("src.api.api_server:app", host=host, port=port, reload=reload)


def main():
    parser = argparse.ArgumentParser(description="HylReg-RAG 项目入口")
    parser.add_argument(
        'command',
        choices=['demo', 'cli', 'api'],
        nargs='?',
        default='demo',
        help='要运行的命令 (默认: demo)'
    )
    parser.add_argument("--host", default="0.0.0.0", help="API服务监听地址")
    parser.add_argument("--port", type=int, default=8000, help="API服务端口")
    parser.add_argument("--reload", action="store_true", help="启用API热重载（开发模式）")
    
    args = parser.parse_args()
    
    if args.command == 'demo':
        run_demo()
    elif args.command == 'cli':
        run_cli()
    elif args.command == 'api':
        run_api(args.host, args.port, args.reload)


if __name__ == "__main__":
    main()
