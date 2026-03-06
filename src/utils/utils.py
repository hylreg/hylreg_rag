import os
from dotenv import load_dotenv
from src.config.settings import get_settings


def load_env_vars():
    """
    加载环境变量，优先从.env文件加载
    """
    # 尝试加载.env文件
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    # 通过配置中心统一验证并返回配置
    return get_settings()


def create_sample_docs_folder():
    """
    创建示例文档文件夹和示例文档
    """
    sample_dir = os.path.join(os.getcwd(), "sample_docs")
    os.makedirs(sample_dir, exist_ok=True)

    # 清理历史遗留的伪PDF/伪DOCX示例文件
    for legacy_file in ("sample.pdf", "services.docx"):
        legacy_path = os.path.join(sample_dir, legacy_file)
        if os.path.exists(legacy_path):
            os.remove(legacy_path)

    # 统一提供真实文本示例，避免“伪PDF/伪DOCX”影响加载结果
    sample_txt_path = os.path.join(sample_dir, "company_info.txt")
    with open(sample_txt_path, "w", encoding="utf-8") as f:
        f.write("""
About AI Solutions Inc.

History:
- Founded in 2015 by Dr. Jane Smith and Dr. John Doe
- Started as a small startup with 5 employees
- First major breakthrough in 2017 with the development of NLP algorithm
- Expanded internationally in 2019

Key Personnel:
- CEO: Dr. Jane Smith, PhD in Natural Language Processing
- CTO: Dr. John Doe, PhD in Machine Learning
- Head of Research: Dr. Emily Chen, PhD in Computer Vision

Technologies:
- Natural Language Processing (NLP)
- Computer Vision
- Deep Learning
- Reinforcement Learning

Notable Achievements:
- Patented algorithm for real-time image recognition in 2020
- Winner of Best AI Innovation Award in 2021
- Over 50 research papers published in top-tier conferences
- More than 100,000 active users across our platforms
""")

    overview_path = os.path.join(sample_dir, "company_overview.txt")
    with open(overview_path, "w", encoding="utf-8") as f:
        f.write("""
Sample Document for RAG System Testing

Introduction:
This document serves as a sample for testing the RAG (Retrieval-Augmented Generation) system.
Our company, AI Solutions Inc., was founded in 2015 with the mission to advance artificial intelligence technologies for business applications.

Company Overview:
AI Solutions Inc. is a leading technology company specializing in artificial intelligence and machine learning solutions.
We provide consulting services, custom AI development, and ready-to-use AI-powered products to clients worldwide.
""")

    services_path = os.path.join(sample_dir, "services.txt")
    with open(services_path, "w", encoding="utf-8") as f:
        f.write("""
AI Solutions Inc. Service Offerings

Consulting Services:
Our consulting team provides expert guidance to help businesses identify opportunities for AI implementation. 
We offer:
- AI readiness assessment
- Strategy development
- Implementation planning
- Risk evaluation

Development Services:
Our development team creates custom AI solutions tailored to specific business needs.
Services include:
- Model development and training
- Integration with existing systems
- API development
- Deployment and maintenance

Training Programs:
We provide comprehensive training programs to help your team leverage AI technologies.
Programs cover:
- AI fundamentals
- Practical applications
- Ethical considerations
- Hands-on workshops

Support and Maintenance:
Post-deployment, we provide ongoing support to ensure optimal performance of AI solutions.
Our support includes:
- 24/7 monitoring
- Performance optimization
- Regular updates
- Troubleshooting
""")


def validate_file_path(file_path: str) -> bool:
    """
    验证文件路径是否存在且为支持的格式
    
    Args:
        file_path: 要验证的文件路径
        
    Returns:
        如果路径有效返回True，否则返回False
    """
    if not os.path.exists(file_path):
        return False
    
    # 检查文件扩展名
    valid_extensions = ['.pdf', '.txt', '.docx']
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in valid_extensions:
        return True
    elif os.path.isdir(file_path):
        # 如果是目录，检查是否包含支持的文件
        for root, dirs, files in os.walk(file_path):
            for file in files:
                _, file_ext = os.path.splitext(file.lower())
                if file_ext in valid_extensions:
                    return True
        return False
    else:
        return False
