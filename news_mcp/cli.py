#!/usr/bin/env python3
"""
新闻获取MCP工具的命令行入口点
"""
import argparse
import sys
from .server import mcp

def main():
    """
    命令行入口点函数
    """
    parser = argparse.ArgumentParser(
        description="新闻获取MCP工具 - 为AI助手提供获取最新新闻的能力"
    )

    parser.add_argument(
        "--transport",
        default="stdio", 
        choices=["stdio", "http"],
        help="MCP传输方式 (默认: stdio)"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP服务器主机 (默认: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP服务器端口 (默认: 8000)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用详细日志输出"
    )

    args = parser.parse_args()

    if args.verbose:
        print("新闻MCP服务器启动中...")
        print(f"传输方式: {args.transport}")
        if args.transport == "http":
            print(f"服务器地址: {args.host}:{args.port}")

    try:
        if args.transport == "stdio":
            mcp.run(transport="stdio")
        else:
            mcp.run_http_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 