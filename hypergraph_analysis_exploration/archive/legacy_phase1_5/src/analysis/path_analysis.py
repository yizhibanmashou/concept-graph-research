"""
路径分析模块 - Phase 3
追踪从basis到目标概念的推理路径
"""
import json
import networkx as nx
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque
import random

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from visualization.visualizer import Visualizer


class PathAnalyzer:
    """路径分析器"""

    def __init__(self, config_path: str = "config/project_config.json"):
        """初始化路径分析器"""
        self.loader = DataLoader(config_path)
        self.config = self.loader.config

        self.output_dir = self.loader.get_phase_output_dir('phase3')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.visualizer = Visualizer(str(self.output_dir))

    def find_shortest_path(self, graph: Dict[str, Set[str]],
                          start: str, target: str,
                          max_depth: int = 400) -> List[str]:
        """
        使用BFS查找从start到target的最短路径

        Args:
            graph: 依赖图（反向：target -> dependencies）
            start: 起点（通常是basis）
            target: 终点（目标概念）
            max_depth: 最大搜索深度

        Returns:
            路径列表，如果不存在返回空列表
        """
        if start == target:
            return [start]

        # 构建前向图（basis -> derived）
        forward_graph = defaultdict(set)
        for node, deps in graph.items():
            for dep in deps:
                forward_graph[dep].add(node)

        # BFS
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if len(path) > max_depth:
                continue

            for neighbor in forward_graph.get(current, []):
                if neighbor == target:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []  # 未找到路径

    def analyze_sample_paths(self, graph: Dict[str, Set[str]],
                            basis_atoms: List[str],
                            num_samples: int = 20) -> Dict:
        """
        分析样本路径

        Args:
            graph: 依赖图
            basis_atoms: basis原子列表
            num_samples: 采样数量

        Returns:
            路径分析统计
        """
        print(f"📊 分析 {num_samples} 个样本路径...")

        # 随机采样目标节点（不同深度层）
        all_nodes = list(graph.keys())
        sample_targets = random.sample(all_nodes, min(num_samples, len(all_nodes)))

        paths_data = []
        path_lengths = []

        for i, target in enumerate(sample_targets, 1):
            # 尝试从多个basis找路径
            found_path = False
            basis_list = list(basis_atoms)[:10]  # 转换为列表并只用前10个basis
            for basis in basis_list:
                path = self.find_shortest_path(graph, basis, target)
                if path:
                    paths_data.append({
                        'target': target,
                        'basis': basis,
                        'path_length': len(path) - 1,
                        'path': path[:10]  # 只保存前10个节点
                    })
                    path_lengths.append(len(path) - 1)
                    found_path = True
                    break

            if not found_path:
                paths_data.append({
                    'target': target,
                    'basis': 'none',
                    'path_length': -1,
                    'path': []
                })

            if i % 5 == 0:
                print(f"  进度: {i}/{num_samples}")

        # 统计
        valid_lengths = [l for l in path_lengths if l > 0]

        stats = {
            'total_samples': num_samples,
            'found_paths': len(valid_lengths),
            'path_length_stats': {
                'min': min(valid_lengths) if valid_lengths else 0,
                'max': max(valid_lengths) if valid_lengths else 0,
                'mean': sum(valid_lengths) / len(valid_lengths) if valid_lengths else 0,
                'median': sorted(valid_lengths)[len(valid_lengths)//2] if valid_lengths else 0
            },
            'sample_paths': paths_data
        }

        return stats

    def identify_bottlenecks(self, graph: Dict[str, Set[str]],
                           paths_data: List[Dict]) -> Dict:
        """
        识别路径瓶颈节点（频繁出现在路径中的节点）

        Returns:
            瓶颈节点统计
        """
        print("🔍 识别路径瓶颈节点...")

        node_frequency = defaultdict(int)

        for path_info in paths_data:
            path = path_info.get('path', [])
            for node in path[1:-1]:  # 排除起点和终点
                node_frequency[node] += 1

        # Top 20瓶颈节点
        top_bottlenecks = sorted(node_frequency.items(),
                                key=lambda x: x[1], reverse=True)[:20]

        bottlenecks = {
            'top_bottlenecks': [
                {'node': node, 'frequency': freq}
                for node, freq in top_bottlenecks
            ],
            'total_unique_nodes': len(node_frequency)
        }

        return bottlenecks

    def run_analysis(self, save_results: bool = True) -> Dict:
        """运行完整的路径分析"""
        print("="*60)
        print("路径分析 - Phase 3")
        print("="*60)

        # 1. 加载数据
        print("\n📥 加载数据...")
        rules = self.loader.load_hypergraph_rules()
        graph, _ = self.loader.build_dependency_graph(rules)
        basis_atoms = self.loader.load_basis_atoms()
        print(f"  ✓ 加载 {len(graph)} 个节点")
        print(f"  ✓ 加载 {len(basis_atoms)} 个basis原子")

        # 2. 分析样本路径
        print("\n🔍 分析样本路径...")
        path_stats = self.analyze_sample_paths(graph, basis_atoms, num_samples=20)

        print(f"\n📈 路径统计:")
        print(f"  • 找到路径: {path_stats['found_paths']}/{path_stats['total_samples']}")
        if path_stats['found_paths'] > 0:
            print(f"  • 最短路径: {path_stats['path_length_stats']['min']} 步")
            print(f"  • 最长路径: {path_stats['path_length_stats']['max']} 步")
            print(f"  • 平均长度: {path_stats['path_length_stats']['mean']:.1f} 步")

        # 3. 识别瓶颈
        bottlenecks = self.identify_bottlenecks(graph, path_stats['sample_paths'])
        print(f"\n🔗 发现 {len(bottlenecks['top_bottlenecks'])} 个主要瓶颈节点")
        if bottlenecks['top_bottlenecks']:
            print(f"  Top 1: {bottlenecks['top_bottlenecks'][0]['node']} (出现{bottlenecks['top_bottlenecks'][0]['frequency']}次)")

        # 4. 汇总结果
        results = {
            'path_statistics': path_stats,
            'bottlenecks': bottlenecks
        }

        # 5. 保存结果
        if save_results:
            output_file = self.output_dir / "path_analysis_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 结果已保存: {output_file}")

        return results


def main():
    """主函数"""
    analyzer = PathAnalyzer()
    results = analyzer.run_analysis()

    print("\n✅ 路径分析完成！")


if __name__ == "__main__":
    main()
