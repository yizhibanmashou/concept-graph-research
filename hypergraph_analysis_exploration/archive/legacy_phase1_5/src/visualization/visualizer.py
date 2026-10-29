"""
可视化工具模块：统一的可视化接口
"""
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import List, Dict, Any

# 设置matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置全局样式
sns.set_style("whitegrid")
sns.set_palette("husl")

class Visualizer:
    """统一的可视化工具"""

    def __init__(self, output_dir: str = "outputs"):
        """初始化可视化器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_figure(self, fig, filename: str, dpi: int = 300):
        """保存图表"""
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f"  ✓ 保存图表: {filename}")
        return filepath

    def plot_distribution(self, data: List[float], title: str,
                         xlabel: str, filename: str,
                         log_scale: bool = False) -> Path:
        """绘制分布图"""
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(data, bins=50, edgecolor='black', alpha=0.7)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('频次', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        if log_scale:
            ax.set_yscale('log')

        ax.grid(True, alpha=0.3)

        return self.save_figure(fig, filename)

    def plot_bar_chart(self, categories: List[str], values: List[float],
                      title: str, xlabel: str, ylabel: str,
                      filename: str) -> Path:
        """绘制柱状图"""
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.bar(range(len(categories)), values, edgecolor='black', alpha=0.8)
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        ax.grid(True, alpha=0.3, axis='y')

        return self.save_figure(fig, filename)

    def plot_network_stats(self, stats: Dict[str, Any], filename: str) -> Path:
        """绘制网络统计概览"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('网络统计概览', fontsize=16, fontweight='bold')

        # 可以根据具体数据自定义
        # 这里提供基础框架

        return self.save_figure(fig, filename)

    @staticmethod
    def generate_html_report(data: Dict, output_path: str):
        """生成HTML可视化报告（可选）"""
        # 可以使用plotly等库生成交互式报告
        pass

if __name__ == "__main__":
    # 测试可视化器
    viz = Visualizer("test_output")

    import numpy as np
    test_data = np.random.normal(100, 15, 1000)

    viz.plot_distribution(
        test_data,
        "测试分布图",
        "数值",
        "test_distribution.png"
    )

    print("✓ 可视化器测试通过")
