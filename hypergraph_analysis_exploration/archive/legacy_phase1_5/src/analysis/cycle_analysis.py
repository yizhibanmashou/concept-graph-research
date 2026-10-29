"""
循环依赖分析模块 - Phase 4
分类和分析依赖图中的循环结构
"""
import json
import networkx as nx
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from visualization.visualizer import Visualizer


class CycleAnalyzer:
    """循环依赖分析器"""

    def __init__(self, config_path: str = "config/project_config.json"):
        """初始化循环分析器"""
        self.loader = DataLoader(config_path)
        self.config = self.loader.config

        self.output_dir = self.loader.get_phase_output_dir('phase4')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.visualizer = Visualizer(str(self.output_dir))

    def find_cycles_sample(self, graph: Dict[str, Set[str]],
                          max_samples: int = 1000) -> List[List[str]]:
        """
        检测循环依赖（采样方式，避免内存溢出）

        Args:
            graph: 依赖图
            max_samples: 最大采样数量

        Returns:
            循环列表
        """
        print(f"🔍 检测循环依赖（最多{max_samples}个样本）...")

        G = nx.DiGraph()
        for node, deps in graph.items():
            for dep in deps:
                G.add_edge(node, dep)

        cycles = []
        try:
            # 使用simple_cycles，但限制数量
            for i, cycle in enumerate(nx.simple_cycles(G)):
                if i >= max_samples:
                    break
                cycles.append(cycle)

                if (i + 1) % 200 == 0:
                    print(f"  已检测: {i+1} 个循环...")
        except Exception as e:
            print(f"  ⚠️  循环检测中断: {e}")

        return cycles

    def classify_cycles(self, cycles: List[List[str]]) -> Dict:
        """
        按长度分类循环

        Returns:
            分类统计
        """
        print("📊 分类循环...")

        # 按长度分类
        length_distribution = Counter([len(cycle) for cycle in cycles])

        # 分组：短(2-3)、中(4-10)、长(>10)
        short_cycles = [c for c in cycles if len(c) <= 3]
        medium_cycles = [c for c in cycles if 4 <= len(c) <= 10]
        long_cycles = [c for c in cycles if len(c) > 10]

        classification = {
            'total_cycles': len(cycles),
            'length_distribution': dict(length_distribution),
            'short_cycles': {
                'count': len(short_cycles),
                'percentage': len(short_cycles) / len(cycles) * 100 if cycles else 0,
                'samples': short_cycles[:10]  # 前10个样本
            },
            'medium_cycles': {
                'count': len(medium_cycles),
                'percentage': len(medium_cycles) / len(cycles) * 100 if cycles else 0,
                'samples': medium_cycles[:5]
            },
            'long_cycles': {
                'count': len(long_cycles),
                'percentage': len(long_cycles) / len(cycles) * 100 if cycles else 0,
                'samples': long_cycles[:3]
            }
        }

        return classification

    def analyze_cycle_nodes(self, cycles: List[List[str]]) -> Dict:
        """
        分析循环中的节点类型

        Returns:
            节点类型统计
        """
        print("🔍 分析循环节点类型...")

        # 统计节点在循环中出现的频率
        node_frequency = defaultdict(int)
        for cycle in cycles:
            for node in cycle:
                node_frequency[node] += 1

        # Top 20高频节点
        top_nodes = sorted(node_frequency.items(),
                          key=lambda x: x[1], reverse=True)[:20]

        node_stats = {
            'unique_nodes_in_cycles': len(node_frequency),
            'top_frequent_nodes': [
                {'node': node, 'frequency': freq}
                for node, freq in top_nodes
            ]
        }

        return node_stats

    def detect_strongly_connected_components(self,
                                            graph: Dict[str, Set[str]]) -> Dict:
        """
        使用Tarjan算法检测强连通分量（SCC）

        Returns:
            SCC统计
        """
        print("🔗 检测强连通分量（SCC）...")

        G = nx.DiGraph()
        for node, deps in graph.items():
            for dep in deps:
                G.add_edge(node, dep)

        # 计算SCC
        sccs = list(nx.strongly_connected_components(G))

        # 按大小排序
        sccs_sorted = sorted(sccs, key=len, reverse=True)

        # 统计
        scc_sizes = [len(scc) for scc in sccs]

        scc_stats = {
            'num_sccs': len(sccs),
            'size_distribution': {
                'min': min(scc_sizes),
                'max': max(scc_sizes),
                'mean': sum(scc_sizes) / len(scc_sizes),
                'median': sorted(scc_sizes)[len(scc_sizes)//2]
            },
            'largest_sccs': [
                {
                    'size': len(scc),
                    'sample_nodes': list(scc)[:10]
                }
                for scc in sccs_sorted[:5]
            ],
            'trivial_sccs': sum(1 for s in scc_sizes if s == 1)
        }

        return scc_stats

    def run_analysis(self, save_results: bool = True) -> Dict:
        """运行完整的循环分析"""
        print("="*60)
        print("循环依赖分析 - Phase 4")
        print("="*60)

        # 1. 加载数据
        print("\n📥 加载数据...")
        rules = self.loader.load_hypergraph_rules()
        graph, _ = self.loader.build_dependency_graph(rules)
        print(f"  ✓ 加载 {len(graph)} 个节点")

        # 2. 检测循环（采样）
        cycles = self.find_cycles_sample(graph, max_samples=1000)
        print(f"  ✓ 检测到 {len(cycles)} 个循环")

        # 3. 分类循环
        classification = self.classify_cycles(cycles)
        print(f"\n📊 循环分类:")
        print(f"  • 短循环 (≤3): {classification['short_cycles']['count']} ({classification['short_cycles']['percentage']:.1f}%)")
        print(f"  • 中循环 (4-10): {classification['medium_cycles']['count']} ({classification['medium_cycles']['percentage']:.1f}%)")
        print(f"  • 长循环 (>10): {classification['long_cycles']['count']} ({classification['long_cycles']['percentage']:.1f}%)")

        # 4. 分析节点
        node_stats = self.analyze_cycle_nodes(cycles)
        print(f"\n🔍 循环节点统计:")
        print(f"  • 涉及节点数: {node_stats['unique_nodes_in_cycles']}")
        if node_stats['top_frequent_nodes']:
            print(f"  • 高频节点: {node_stats['top_frequent_nodes'][0]['node']} (出现{node_stats['top_frequent_nodes'][0]['frequency']}次)")

        # 5. 检测SCC
        scc_stats = self.detect_strongly_connected_components(graph)
        print(f"\n🔗 强连通分量:")
        print(f"  • SCC数量: {scc_stats['num_sccs']}")
        print(f"  • 最大SCC: {scc_stats['size_distribution']['max']} 个节点")
        print(f"  • 孤立节点: {scc_stats['trivial_sccs']}")

        # 6. 汇总结果
        results = {
            'cycle_classification': classification,
            'node_statistics': node_stats,
            'scc_statistics': scc_stats
        }

        # 7. 保存结果
        if save_results:
            output_file = self.output_dir / "cycle_analysis_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 结果已保存: {output_file}")

        return results


def main():
    """主函数"""
    analyzer = CycleAnalyzer()
    results = analyzer.run_analysis()

    print("\n✅ 循环依赖分析完成！")


if __name__ == "__main__":
    main()
