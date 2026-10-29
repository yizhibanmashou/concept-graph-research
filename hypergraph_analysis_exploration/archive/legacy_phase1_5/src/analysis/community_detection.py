"""
社区检测分析模块
"""
import json
import networkx as nx
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import community as community_louvain  # python-louvain

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from visualization.visualizer import Visualizer


class CommunityDetector:
    """社区检测分析器"""

    def __init__(self, config_path: str = "config/project_config.json"):
        """初始化社区检测器"""
        self.loader = DataLoader(config_path)
        self.config = self.loader.config

        # 输出目录
        self.output_dir = self.loader.get_phase_output_dir('phase2')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.visualizer = Visualizer(str(self.output_dir))

    def build_undirected_graph(self, graph: Dict[str, Set[str]]) -> nx.Graph:
        """
        将有向依赖图转换为无向图（用于社区检测）

        Args:
            graph: 依赖图 head -> set of dependencies

        Returns:
            无向图
        """
        G = nx.Graph()

        # 添加所有边
        for head, deps in graph.items():
            for dep in deps:
                # 无向图，双向连接
                G.add_edge(head, dep)

        return G

    def detect_communities(self, G: nx.Graph) -> Dict[str, int]:
        """
        使用Louvain算法检测社区

        Args:
            G: 无向图

        Returns:
            node -> community_id 的映射
        """
        print("🔍 运行Louvain社区检测算法...")

        partition = community_louvain.best_partition(G)

        return partition

    def compute_modularity(self, G: nx.Graph, partition: Dict[str, int]) -> float:
        """计算模块度"""
        modularity = community_louvain.modularity(partition, G)
        return modularity

    def analyze_communities(self, partition: Dict[str, int]) -> Dict:
        """
        分析社区统计信息

        Returns:
            社区统计字典
        """
        print("📊 分析社区统计信息...")

        # 按社区分组
        communities = defaultdict(list)
        for node, comm_id in partition.items():
            communities[comm_id].append(node)

        # 统计
        num_communities = len(communities)
        community_sizes = [len(nodes) for nodes in communities.values()]

        stats = {
            'num_communities': num_communities,
            'community_sizes': {
                'min': min(community_sizes),
                'max': max(community_sizes),
                'mean': sum(community_sizes) / len(community_sizes),
                'median': sorted(community_sizes)[len(community_sizes) // 2]
            },
            'size_distribution': dict(Counter(community_sizes)),
            'communities': {
                comm_id: {
                    'size': len(nodes),
                    'top_nodes': nodes[:20]  # 前20个节点
                }
                for comm_id, nodes in communities.items()
            }
        }

        return stats

    def run_analysis(self, save_results: bool = True) -> Dict:
        """
        运行完整的社区检测分析

        Returns:
            分析结果
        """
        print("="*60)
        print("社区检测分析 - Phase 2")
        print("="*60)

        # 1. 加载数据
        print("\n📥 加载数据...")
        rules = self.loader.load_hypergraph_rules()
        graph, _ = self.loader.build_dependency_graph(rules)
        print(f"  ✓ 加载 {len(graph)} 个节点")

        # 2. 构建无向图
        print("\n🔄 构建无向图...")
        G = self.build_undirected_graph(graph)
        print(f"  ✓ 节点数: {G.number_of_nodes()}")
        print(f"  ✓ 边数: {G.number_of_edges()}")

        # 3. 社区检测
        print("\n🔍 社区检测...")
        partition = self.detect_communities(G)

        # 4. 计算模块度
        modularity = self.compute_modularity(G, partition)
        print(f"  ✓ 模块度: {modularity:.4f}")

        # 5. 分析社区
        stats = self.analyze_communities(partition)
        stats['modularity'] = modularity

        print(f"\n📈 检测到 {stats['num_communities']} 个社区")
        print(f"  • 最大社区: {stats['community_sizes']['max']} 个节点")
        print(f"  • 最小社区: {stats['community_sizes']['min']} 个节点")
        print(f"  • 平均大小: {stats['community_sizes']['mean']:.1f} 个节点")

        # 6. 保存结果
        if save_results:
            output_file = self.output_dir / "community_detection_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"\n💾 结果已保存: {output_file}")

        return stats


def main():
    """主函数"""
    detector = CommunityDetector()
    results = detector.run_analysis()

    print("\n✅ 社区检测分析完成！")


if __name__ == "__main__":
    main()
