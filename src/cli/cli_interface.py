import argparse
import sys

from src.core.rag_system import RAGSystem
from src.utils.utils import create_sample_docs_folder, load_env_vars, validate_file_path


def interactive_mode(rag_system: RAGSystem):
    """
    交互模式，允许用户连续提问
    """
    print("\n=== RAG系统交互模式 ===")
    print("输入您的问题，输入 'quit' 或 'exit' 退出")
    print("输入 'add' 添加新文档")
    print("========================\n")

    while True:
        try:
            user_input = input("请输入您的问题: ").strip()

            if user_input.lower() in ["quit", "exit", "退出", "q"]:
                print("感谢使用RAG系统！再见！")
                break

            if user_input.lower() in ["add", "添加"]:
                file_path = input("请输入要添加的文档路径: ").strip()
                if not validate_file_path(file_path):
                    print(f"错误：文件路径 '{file_path}' 不存在或格式不支持")
                    continue

                print("正在添加文档...")
                rag_system.add_document(file_path)
                print(f"成功添加文档: {file_path}")
                continue

            if not user_input:
                print("请输入有效的问题")
                continue

            # 获取答案
            result = rag_system.query(user_input)
            print(f"\n答案: {result['answer']}")

            if result["source_documents"]:
                print("\n参考来源:")
                for i, source in enumerate(
                    result["source_documents"][:2], 1
                ):  # 只显示前2个来源
                    print(f"{i}. {source[:200]}...")  # 只显示前200个字符

            print("\n" + "=" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")


def main():
    """
    CLI主函数
    """
    parser = argparse.ArgumentParser(description="RAG系统命令行接口")
    parser.add_argument("--file", "-f", type=str, help="要处理的文档文件路径或目录路径")
    parser.add_argument("--question", "-q", type=str, help="要查询的问题")
    parser.add_argument("--interactive", "-i", action="store_true", help="进入交互模式")
    parser.add_argument("--create-sample", action="store_true", help="创建示例文档")
    parser.add_argument(
        "--load-index", action="store_true", help="从本地向量库目录加载索引"
    )
    parser.add_argument(
        "--save-index", action="store_true", help="将当前向量库保存到本地目录"
    )

    args = parser.parse_args()

    # 加载环境变量
    try:
        load_env_vars()
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

    # 如果请求创建示例文档
    if args.create_sample:
        create_sample_docs_folder()
        print("已创建示例文档文件夹 'sample_docs'")
        return

    # 初始化RAG系统
    try:
        rag_system = RAGSystem()
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

    if args.load_index:
        try:
            rag_system.load_vectorstore()
            if rag_system.vectorstore:
                print(f"已加载向量索引: {rag_system.vectorstore_dir}")
            else:
                print(f"未找到向量索引目录: {rag_system.vectorstore_dir}")
        except Exception as e:
            print(f"加载向量索引失败: {str(e)}")
            sys.exit(1)

    # 如果提供了文件路径
    if args.file:
        if not validate_file_path(args.file):
            print(f"错误：文件路径 '{args.file}' 不存在或格式不支持")
            sys.exit(1)

        print(f"正在处理文档: {args.file}")
        try:
            rag_system.process_and_store(args.file)
            print("文档处理完成")
        except Exception as e:
            print(f"处理文档时出错: {str(e)}")
            sys.exit(1)

    # 如果提供了问题
    if args.question and args.file:
        try:
            result = rag_system.query(args.question)
            print(f"问题: {args.question}")
            print(f"答案: {result['answer']}")
        except Exception as e:
            print(f"查询时出错: {str(e)}")
            sys.exit(1)

    # 如果指定了交互模式
    if args.interactive or (not args.question and not args.create_sample):
        if not args.file:
            print("警告：未指定文件，您需要先添加文档才能进行查询")
        interactive_mode(rag_system)

    if args.save_index:
        try:
            rag_system.save_vectorstore()
            print(f"已保存向量索引: {rag_system.vectorstore_dir}")
        except Exception as e:
            print(f"保存向量索引失败: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
