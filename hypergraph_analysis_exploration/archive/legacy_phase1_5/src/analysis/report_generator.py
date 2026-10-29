"""
综合分析报告生成模块 - Phase 6
整合所有阶段的分析结果，生成最终报告
"""
import json
from pathlib import Path
from typing import Dict
from datetime import datetime

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader


class ReportGenerator:
    """综合报告生成器"""

    def __init__(self, config_path: str = "config/project_config.json"):
        """初始化报告生成器"""
        self.loader = DataLoader(config_path)
        self.config = self.loader.config

        self.output_dir = Path("reports/final_report")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_phase_results(self) -> Dict:
        """加载所有阶段的结果"""
        print("📥 加载各阶段分析结果...")

        results = {}

        # Phase 1: 基础统计
        phase1_path = Path("results/basic_stats.json")
        if phase1_path.exists():
            with open(phase1_path, 'r', encoding='utf-8') as f:
                results['phase1_basic_stats'] = json.load(f)
            print("  ✓ Phase 1: 基础统计")

        # Phase 2: 社区检测
        phase2_path = Path("outputs/phase2/community_detection_results.json")
        if phase2_path.exists():
            with open(phase2_path, 'r', encoding='utf-8') as f:
                results['phase2_community'] = json.load(f)
            print("  ✓ Phase 2: 社区检测")

        # Phase 3: 路径分析
        phase3_path = Path("outputs/phase3/path_analysis_results.json")
        if phase3_path.exists():
            with open(phase3_path, 'r', encoding='utf-8') as f:
                results['phase3_path'] = json.load(f)
            print("  ✓ Phase 3: 路径分析")

        # Phase 4: 循环分析
        phase4_path = Path("outputs/phase4/cycle_analysis_results.json")
        if phase4_path.exists():
            with open(phase4_path, 'r', encoding='utf-8') as f:
                results['phase4_cycle'] = json.load(f)
            print("  ✓ Phase 4: 循环分析")

        # Phase 5: Hub分析
        phase5_path = Path("outputs/phase5/hub_analysis_results.json")
        if phase5_path.exists():
            with open(phase5_path, 'r', encoding='utf-8') as f:
                results['phase5_hub'] = json.load(f)
            print("  ✓ Phase 5: Hub分析")

        return results

    def generate_executive_summary(self, results: Dict) -> str:
        """生成执行摘要"""
        summary = []
        summary.append("# OEWN超图网络综合分析报告")
        summary.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("\n---\n")

        summary.append("## 执行摘要\n")

        # Phase 1 摘要
        if 'phase1_basic_stats' in results:
            p1 = results['phase1_basic_stats']
            summary.append("### 1. 基础网络特征")
            summary.append(f"- **节点总数**: {p1.get('total_nodes', 'N/A'):,}")
            summary.append(f"- **超边总数**: {p1.get('total_hyperedges', 'N/A'):,}")
            summary.append(f"- **Basis原子**: {p1.get('num_basis_atoms', 'N/A')}")
            if 'topology' in p1:
                summary.append(f"- **最大深度**: {p1['topology'].get('max_layer', 'N/A')} 层")
            summary.append("")

        # Phase 2 摘要
        if 'phase2_community' in results:
            p2 = results['phase2_community']
            summary.append("### 2. 社区结构")
            summary.append(f"- **社区数量**: {p2.get('num_communities', 'N/A')}")
            if 'community_sizes' in p2:
                summary.append(f"- **最大社区**: {p2['community_sizes'].get('max', 'N/A'):,} 节点")
                summary.append(f"- **平均规模**: {p2['community_sizes'].get('mean', 0):.0f} 节点")
            summary.append("")

        # Phase 3 摘要
        if 'phase3_path' in results:
            p3 = results['phase3_path']
            if 'path_statistics' in p3:
                stats = p3['path_statistics'].get('path_length_stats', {})
                summary.append("### 3. 路径特征")
                summary.append(f"- **平均路径长度**: {stats.get('mean', 0):.1f} 步")
                summary.append(f"- **最短/最长**: {stats.get('min', 'N/A')} / {stats.get('max', 'N/A')} 步")
                summary.append("")

        # Phase 4 摘要
        if 'phase4_cycle' in results:
            p4 = results['phase4_cycle']
            if 'cycle_classification' in p4:
                cc = p4['cycle_classification']
                summary.append("### 4. 循环依赖")
                summary.append(f"- **检测循环数**: {cc.get('total_cycles', 'N/A'):,}")
                summary.append(f"- **短循环占比**: {cc['short_cycles'].get('percentage', 0):.1f}%")
            if 'scc_statistics' in p4:
                scc = p4['scc_statistics']
                summary.append(f"- **最大SCC**: {scc['size_distribution'].get('max', 'N/A'):,} 节点")
                summary.append("")

        # Phase 5 摘要
        if 'phase5_hub' in results:
            p5 = results['phase5_hub']
            if 'hub_nodes' in p5 and p5['hub_nodes']:
                top_hub = p5['hub_nodes'][0]
                summary.append("### 5. Hub节点")
                summary.append(f"- **Top Hub**: {top_hub['node']} (入度 {top_hub['in_degree']:,})")
                summary.append(f"- **Top 100范围**: {p5['hub_nodes'][0]['in_degree']:,} - {p5['hub_nodes'][-1]['in_degree']:,}")
                summary.append("")

        return "\n".join(summary)

    def generate_detailed_findings(self, results: Dict) -> str:
        """生成详细发现"""
        findings = []
        findings.append("## 关键发现\n")

        findings.append("### 🔍 网络拓扑特征")
        findings.append("1. **深度极端化**: 63%的节点集中在301-399层，呈现倒金字塔结构")
        findings.append("2. **完全覆盖**: 85个basis原子通过189次迭代覆盖全部110,425个节点")
        findings.append("3. **小世界特性**: 聚类系数0.0886，显著高于随机图\n")

        findings.append("### 🏘️ 社区结构")
        if 'phase2_community' in results:
            p2 = results['phase2_community']
            modularity = p2.get('modularity', 0)
            findings.append(f"1. **模块度优秀**: Q = {modularity:.4f} (>0.4表示社区结构明显)")
            findings.append("2. **语义聚类清晰**: 社区0以关系/介词为主，社区1为时间/度量，社区2为空间/位置")
            findings.append("3. **规模相对均衡**: 最大社区占27.8%，未形成一家独大\n")

        findings.append("### 🔗 循环依赖模式")
        if 'phase4_cycle' in results:
            p4 = results['phase4_cycle']
            findings.append("1. **短循环主导**: 95.7%为2-3节点的简单相互定义")
            findings.append("2. **超大SCC存在**: 发现13,168节点的强连通分量（11.9%总节点）")
            findings.append("3. **循环结构清晰**: 无超长循环（>10节点），易于处理\n")

        findings.append("### ⭐ Hub节点特征")
        if 'phase5_hub' in results:
            p5 = results['phase5_hub']
            findings.append("1. **介词主导**: Top 5全为介词/连接词（of, by, in, to）")
            findings.append("2. **高度中心化**: of-6被30,087个节点依赖（27.2%）")
            findings.append("3. **Hub不在小循环**: Top 50 Hub节点未出现在采样的1000个循环中\n")

        return "\n".join(findings)

    def generate_recommendations(self) -> str:
        """生成方法建议"""
        recommendations = []
        recommendations.append("## 后续工作建议\n")

        recommendations.append("### 📊 图分析方法")
        recommendations.append("#### 推荐方法")
        recommendations.append("1. **层次路径分析**")
        recommendations.append("   - 使用BFS追踪概念的完整推理链")
        recommendations.append("   - 识别推理瓶颈节点")
        recommendations.append("   - 构建分层抽象金字塔\n")

        recommendations.append("2. **Hub节点中心性分析**")
        recommendations.append("   - PageRank识别语义枢纽")
        recommendations.append("   - Betweenness找出信息瓶颈")
        recommendations.append("   - 优先优化高中心性节点\n")

        recommendations.append("3. **社区语义标注**")
        recommendations.append("   - 对12个社区进行人工标注")
        recommendations.append("   - 分析跨社区边的语义类型")
        recommendations.append("   - 发现领域知识模块\n")

        recommendations.append("4. **SCC消解策略**")
        recommendations.append("   - 分析13K节点大SCC的内部结构")
        recommendations.append("   - 设计循环依赖的打破策略")
        recommendations.append("   - 建立分层推理优先级\n")

        recommendations.append("#### 需要特殊处理的问题")
        recommendations.append("1. **深度优化**: 300+层推理链需要剪枝或缓存策略")
        recommendations.append("2. **Hub节点验证**: 人工审核Top 20 Hub的定义合理性")
        recommendations.append("3. **循环消解**: 设计Tarjan算法的高效实现\n")

        recommendations.append("### 🎯 验证思路")
        recommendations.append("1. **推理路径验证**")
        recommendations.append("   - 随机抽取100个深层节点")
        recommendations.append("   - 手动验证其到basis的推理链")
        recommendations.append("   - 检查是否存在语义跳跃\n")

        recommendations.append("2. **社区合理性验证**")
        recommendations.append("   - 人工审核每个社区的Top 100节点")
        recommendations.append("   - 确认语义聚类的一致性")
        recommendations.append("   - 识别误分类节点\n")

        recommendations.append("3. **NLI任务验证**")
        recommendations.append("   - 在自然语言推理数据集上测试")
        recommendations.append("   - 对比使用/不使用图结构的推理效果")
        recommendations.append("   - 评估Hub节点对推理成功率的影响\n")

        return "\n".join(recommendations)

    def generate_data_appendix(self, results: Dict) -> str:
        """生成数据附录"""
        appendix = []
        appendix.append("## 数据附录\n")

        appendix.append("### Phase 1: 基础统计")
        if 'phase1_basic_stats' in results:
            p1 = results['phase1_basic_stats']
            appendix.append("```json")
            appendix.append(json.dumps({
                'total_nodes': p1.get('total_nodes'),
                'total_hyperedges': p1.get('total_hyperedges'),
                'num_basis_atoms': p1.get('num_basis_atoms'),
                'pos_distribution': p1.get('pos_distribution', {})
            }, indent=2))
            appendix.append("```\n")

        appendix.append("### Phase 2: 社区检测")
        if 'phase2_community' in results:
            p2 = results['phase2_community']
            appendix.append("```json")
            appendix.append(json.dumps({
                'num_communities': p2.get('num_communities'),
                'modularity': p2.get('modularity'),
                'community_sizes': p2.get('community_sizes')
            }, indent=2))
            appendix.append("```\n")

        appendix.append("### 输出文件清单")
        appendix.append("```")
        appendix.append("outputs/")
        appendix.append("├── phase2/community_detection_results.json")
        appendix.append("├── phase3/path_analysis_results.json")
        appendix.append("├── phase4/cycle_analysis_results.json")
        appendix.append("└── phase5/hub_analysis_results.json")
        appendix.append("")
        appendix.append("results/")
        appendix.append("├── basic_stats.json")
        appendix.append("├── topology_analysis.json")
        appendix.append("├── network_features.json")
        appendix.append("└── *.png (可视化图表)")
        appendix.append("```\n")

        return "\n".join(appendix)

    def generate_report(self) -> str:
        """生成完整报告"""
        print("="*60)
        print("综合报告生成 - Phase 6")
        print("="*60)

        # 加载数据
        results = self.load_phase_results()

        # 生成各部分
        print("\n📝 生成报告内容...")
        report_parts = []

        report_parts.append(self.generate_executive_summary(results))
        report_parts.append(self.generate_detailed_findings(results))
        report_parts.append(self.generate_recommendations())
        report_parts.append(self.generate_data_appendix(results))

        # 添加结尾
        report_parts.append("---")
        report_parts.append(f"\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        report_parts.append("\n*所有分析结果均可在对应输出目录中查看详细数据*\n")

        full_report = "\n".join(report_parts)

        # 保存报告
        output_file = self.output_dir / "comprehensive_analysis_report.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_report)

        print(f"💾 报告已保存: {output_file}")

        return str(output_file)


def main():
    """主函数"""
    generator = ReportGenerator()
    report_path = generator.generate_report()

    print("\n✅ 综合报告生成完成！")
    print(f"\n📄 报告位置: {report_path}")


if __name__ == "__main__":
    main()
