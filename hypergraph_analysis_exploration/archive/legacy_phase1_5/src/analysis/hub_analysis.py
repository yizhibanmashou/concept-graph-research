"""
Hub节点分析模块 - Phase 5
分析高入度节点的特征和影响
"""
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from visualization.visualizer import Visualizer


class HubAnalyzer:
    """Hub节点分析器"""

    def __init__(self, config_path: str = "config/project_config.json"):
        """初始化Hub分析器"""
        self.loader = DataLoader(config_path)
        self.config = self.loader.config

        self.output_dir = self.loader.get_phase_output_dir('phase5')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.visualizer = Visualizer(str(self.output_dir))

    def identify_hub_nodes(self, reverse_graph: Dict[str, Set[str]],
                          top_n: int = 100) -> List[Tuple[str, int]]:
        """
        识别Hub节点（高入度节点）

        Args:
            reverse_graph: 反向图（node -> dependents）
            top_n: 返回Top N节点

        Returns:
            (节点, 入度) 列表，按入度降序
        """
        print(f"🔍 识别Top {top_n} Hub节点...")

        # 计算入度
        in_degrees = [(node, len(deps)) for node, deps in reverse_graph.items()]

        # 排序
        hub_nodes = sorted(in_degrees, key=lambda x: x[1], reverse=True)[:top_n]

        return hub_nodes

    def analyze_hub_types(self, hub_nodes: List[Tuple[str, int]],
                         nodes_data) -> Dict:
        """
        分析Hub节点的类型分布

        Returns:
            类型统计
        """
        print("📊 分析Hub节点类型...")

        # 构建节点信息映射（处理DataFrame或列表）
        node_info = {}
        try:
            # 如果是DataFrame
            if hasattr(nodes_data, 'set_index'):
                node_info = nodes_data.set_index('id').to_dict('index')
            # 如果是列表
            elif isinstance(nodes_data, list) and nodes_data and isinstance(nodes_data[0], dict):
                node_info = {n['id']: n for n in nodes_data}
        except:
            pass

        # 统计词性分布
        pos_distribution = Counter()
        hub_details = []

        for node, in_degree in hub_nodes[:50]:  # 分析Top 50
            info = node_info.get(node, {})
            pos = info.get('pos', 'unknown')
            pos_distribution[pos] += 1

            hub_details.append({
                'node': node,
                'in_degree': in_degree,
                'pos': pos,
                'layer': info.get('layer', -1)
            })

        type_stats = {
            'pos_distribution': dict(pos_distribution),
            'top_50_details': hub_details
        }

        return type_stats

    def analyze_hub_in_cycles(self, hub_nodes: List[Tuple[str, int]],
                             cycle_data: Dict) -> Dict:
        """
        分析Hub节点在循环中的参与情况

        Returns:
            循环参与统计
        """
        print("🔗 分析Hub节点的循环参与...")

        # 获取循环中的高频节点
        cycle_frequent_nodes = set()
        if 'node_statistics' in cycle_data:
            top_cycle_nodes = cycle_data['node_statistics'].get('top_frequent_nodes', [])
            cycle_frequent_nodes = {n['node'] for n in top_cycle_nodes}

        # 检查Hub节点是否在循环中
        hub_in_cycles = []
        for node, in_degree in hub_nodes[:50]:
            in_cycle = node in cycle_frequent_nodes
            hub_in_cycles.append({
                'node': node,
                'in_degree': in_degree,
                'in_cycle': in_cycle
            })

        cycle_participation = {
            'hub_in_cycles': sum(1 for h in hub_in_cycles if h['in_cycle']),
            'total_hub_analyzed': len(hub_in_cycles),
            'participation_rate': sum(1 for h in hub_in_cycles if h['in_cycle']) / len(hub_in_cycles) * 100 if hub_in_cycles else 0,
            'details': hub_in_cycles
        }

        return cycle_participation

    def generate_priority_list(self, hub_nodes: List[Tuple[str, int]],
                              type_stats: Dict,
                              cycle_participation: Dict) -> List[Dict]:
        """
        生成Hub节点优先审核清单

        Returns:
            优先级排序的审核清单
        """
        print("📋 生成优先审核清单...")

        # 综合评分：入度 + 循环参与
        priority_list = []

        hub_details = {h['node']: h for h in type_stats['top_50_details']}
        cycle_details = {h['node']: h for h in cycle_participation['details']}

        for node, in_degree in hub_nodes[:20]:
            hub_info = hub_details.get(node, {})
            cycle_info = cycle_details.get(node, {})

            risk_score = in_degree
            if cycle_info.get('in_cycle', False):
                risk_score *= 1.5  # 循环参与加权

            priority_list.append({
                'node': node,
                'in_degree': in_degree,
                'pos': hub_info.get('pos', 'unknown'),
                'layer': hub_info.get('layer', -1),
                'in_cycle': cycle_info.get('in_cycle', False),
                'risk_score': risk_score
            })

        # 按风险评分排序
        priority_list.sort(key=lambda x: x['risk_score'], reverse=True)

        return priority_list

    def run_analysis(self, save_results: bool = True) -> Dict:
        """运行完整的Hub节点分析"""
        print("="*60)
        print("Hub节点分析 - Phase 5")
        print("="*60)

        # 1. 加载数据
        print("\n📥 加载数据...")
        rules = self.loader.load_hypergraph_rules()
        graph, reverse_graph = self.loader.build_dependency_graph(rules)
        nodes = self.loader.load_nodes()
        print(f"  ✓ 加载 {len(graph)} 个节点")

        # 2. 识别Hub节点
        hub_nodes = self.identify_hub_nodes(reverse_graph, top_n=100)
        print(f"  ✓ Top 1 Hub: {hub_nodes[0][0]} (入度 {hub_nodes[0][1]})")

        # 3. 分析类型
        type_stats = self.analyze_hub_types(hub_nodes, nodes)
        print(f"\n📊 Hub节点词性分布:")
        for pos, count in sorted(type_stats['pos_distribution'].items(),
                                key=lambda x: x[1], reverse=True):
            print(f"  • {pos}: {count}")

        # 4. 加载循环数据并分析
        cycle_data_path = Path("outputs/phase4/cycle_analysis_results.json")
        cycle_data = {}
        if cycle_data_path.exists():
            with open(cycle_data_path, 'r', encoding='utf-8') as f:
                cycle_data = json.load(f)

        cycle_participation = self.analyze_hub_in_cycles(hub_nodes, cycle_data)
        print(f"\n🔗 循环参与:")
        print(f"  • Hub在循环中: {cycle_participation['hub_in_cycles']}/{cycle_participation['total_hub_analyzed']}")
        print(f"  • 参与率: {cycle_participation['participation_rate']:.1f}%")

        # 5. 生成优先级清单
        priority_list = self.generate_priority_list(hub_nodes, type_stats,
                                                   cycle_participation)
        print(f"\n📋 Top 5 优先审核节点:")
        for i, item in enumerate(priority_list[:5], 1):
            cycle_marker = "🔄" if item['in_cycle'] else ""
            print(f"  {i}. {item['node']} - 入度{item['in_degree']}, {item['pos']} {cycle_marker}")

        # 6. 汇总结果
        results = {
            'hub_nodes': [{'node': n, 'in_degree': d} for n, d in hub_nodes],
            'type_statistics': type_stats,
            'cycle_participation': cycle_participation,
            'priority_review_list': priority_list
        }

        # 7. 保存结果
        if save_results:
            output_file = self.output_dir / "hub_analysis_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 结果已保存: {output_file}")

        return results


def main():
    """主函数"""
    analyzer = HubAnalyzer()
    results = analyzer.run_analysis()

    print("\n✅ Hub节点分析完成！")


if __name__ == "__main__":
    main()
