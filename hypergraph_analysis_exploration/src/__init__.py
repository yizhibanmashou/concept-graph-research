"""
项目初始化和统一入口
"""
from pathlib import Path


def ensure_project_structure(project_root: Path | None = None):
    """确保当前项目目录结构存在；默认以仓库根目录为基准。"""
    base_dir = Path(project_root) if project_root is not None else Path(__file__).resolve().parent.parent

    required_dirs = [
        "src/analysis",
        "src/logic",
        "outputs",
        "reports",
        "config",
        "docs",
        "archive",
        "sources",
        "tests",
        "tmp",
    ]

    for dir_path in required_dirs:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)


# 项目元数据
PROJECT_NAME = "OEWN超图依赖网络深度分析"
VERSION = "3.0.0"
AUTHOR = "未指定"

# 导出
__all__ = [
    'PROJECT_NAME',
    'VERSION',
    'AUTHOR',
    'ensure_project_structure'
]


if __name__ == "__main__":
    ensure_project_structure()
    print(f"✓ {PROJECT_NAME} v{VERSION}")
    print("✓ 项目结构检查完成")
