"""
数据加载模块：统一的数据加载接口
"""
import json
from pathlib import Path
import pandas as pd
from typing import Dict, List, Set, Tuple

class DataLoader:
    """统一的数据加载器"""

    def __init__(self, config_path: str = "config/project_config.json"):
        """初始化数据加载器"""
        project_root = Path(__file__).resolve().parents[2]
        config_file = Path(config_path)
        if not config_file.is_absolute():
            config_file = (project_root / config_file).resolve()
        with config_file.open('r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.project_root = project_root
        self.data_root = Path(self.config['data_source']['root'])
        if not self.data_root.is_absolute():
            self.data_root = (self.project_root / self.data_root).resolve()
        self.graph_dir = self.data_root / self.config['data_source']['graph_dir']

    def load_nodes(self) -> pd.DataFrame:
        """加载节点数据"""
        nodes_file = self.data_root / self.config['data_source']['nodes_file']
        return pd.read_csv(nodes_file, sep='\t', encoding='utf-8')

    def load_hypergraph_rules(self) -> List[Dict]:
        """加载超图规则"""
        rules_file = self.data_root / self.config['data_source']['hypergraph_rules']
        rules = []
        with open(rules_file, 'r', encoding='utf-8') as f:
            for line in f:
                rules.append(json.loads(line))
        return rules

    def load_hyperedges(self) -> List[Dict]:
        """加载超边数据"""
        edges_file = self.data_root / self.config['data_source']['hyperedges']
        edges = []
        with open(edges_file, 'r', encoding='utf-8') as f:
            for line in f:
                edges.append(json.loads(line))
        return edges

    def load_basis_atoms(self) -> Set[str]:
        """加载basis原子"""
        basis_file = self.data_root / self.config['data_source']['basis_atoms']
        with open(basis_file, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())

    def build_dependency_graph(self, rules: List[Dict] = None) -> Tuple[Dict, Dict]:
        """
        构建有向二元投影（有损，仅用于探索性拓扑分析）。

        该投影丢弃同一子句内的 AND 分组，也丢弃同一 head 的 OR 子句边界；
        不可将投影路径解释为 Horn 推导或语义证明。核心闭包请使用
        ``src.analysis.frozen_hypergraph_audit`` 中保留完整子句的实现。

        Returns:
            graph: head -> set of dependencies
            reverse_graph: dependency -> set of heads
        """
        if rules is None:
            rules = self.load_hypergraph_rules()

        from collections import defaultdict

        graph = defaultdict(set)
        reverse_graph = defaultdict(set)

        for rule in rules:
            head = rule['head']
            for clause in rule['clauses']:
                for dep in clause:
                    graph[head].add(dep)
                    reverse_graph[dep].add(head)

        return dict(graph), dict(reverse_graph)

    def get_phase_output_dir(self, phase: str) -> Path:
        """获取指定阶段的输出目录"""
        return (self.project_root / self.config['phases'][phase]['outputs']).resolve()

    def get_phase_report_dir(self, phase: str) -> Path:
        """获取指定阶段的报告目录"""
        return (self.project_root / self.config['phases'][phase]['reports']).resolve()

if __name__ == "__main__":
    # 测试数据加载
    loader = DataLoader()

    print("测试数据加载器...")
    print(f"节点数: {len(loader.load_nodes())}")
    print(f"规则数: {len(loader.load_hypergraph_rules())}")
    print(f"Basis数: {len(loader.load_basis_atoms())}")
    print("✓ 数据加载器测试通过")
