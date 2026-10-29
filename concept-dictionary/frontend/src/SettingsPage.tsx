import {
  Check,
  Download,
  Upload,
  Database,
  Eye,
  BookOpen,
  ShieldCheck,
  Info,
} from "lucide-react";
import { themes, type Health, type TextSize, type Theme } from "./types";

type Props = {
  health: Health | null;
  theme: Theme;
  setTheme: (value: Theme) => void;
  textSize: TextSize;
  setTextSize: (value: TextSize) => void;
  reduceMotion: boolean;
  setReduceMotion: (value: boolean) => void;
  defaultGraph: boolean;
  setDefaultGraph: (value: boolean) => void;
  knownCount: number;
  recentCount: number;
  onClearRecent: () => void;
  openKnown: () => void;
  onImport: () => void;
  onExport: () => void;
  onReset: () => void;
};

export function SettingsPage(props: Props) {
  return (
    <div className="settings-page page">
      <div className="settings-layout">
        <nav className="settings-nav" aria-label="设置导航">
          <span className="section-kicker">设置</span>
          <a href="#settings-appearance">
            <Eye size={16} />
            外观与阅读
          </a>
          <a href="#settings-learning">
            <BookOpen size={16} />
            学习与路径
          </a>
          <a href="#settings-data">
            <Database size={16} />
            数据与状态
          </a>
          <a href="#settings-about">
            <Info size={16} />
            关于
          </a>
        </nav>
        <div className="settings-content">
          <header className="settings-header">
            <span className="section-kicker">PREFERENCES</span>
            <h1>设置</h1>
            <p>调整阅读体验，管理本地的学习状态和数据。</p>
          </header>
          <section id="settings-appearance" className="settings-section">
            <div className="settings-section-title">
              <div>
                <h2>外观与阅读</h2>
                <p>选择适合自己的阅读环境。更改会立即保存到此浏览器。</p>
              </div>
            </div>
            <div className="settings-label">主题</div>
            <div className="theme-cards">
              {themes.map((theme) => (
                <button
                  key={theme.id}
                  className={
                    "theme-card " + (props.theme === theme.id ? "selected" : "")
                  }
                  onClick={() => props.setTheme(theme.id)}
                  aria-pressed={props.theme === theme.id}
                >
                  <span className={"theme-preview preview-" + theme.id}>
                    <i />
                    <i />
                    <i />
                  </span>
                  <span className="theme-card-label">
                    <b>{theme.label}</b>
                    {props.theme === theme.id && <Check size={15} />}
                  </span>
                  <small>{theme.description}</small>
                </button>
              ))}
            </div>
            <div className="settings-row">
              <div>
                <b>释义文字大小</b>
                <p>调整解释卡片中的正文大小。</p>
              </div>
              <div className="segmented" role="group" aria-label="释义文字大小">
                {(
                  [
                    ["small", "小"],
                    ["medium", "标准"],
                    ["large", "大"],
                  ] as const
                ).map(([value, label]) => (
                  <button
                    key={value}
                    aria-pressed={props.textSize === value}
                    className={props.textSize === value ? "selected" : ""}
                    onClick={() => props.setTextSize(value)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="settings-row">
              <div>
                <b>减少动态效果</b>
                <p>降低界面过渡和滚动动画。</p>
              </div>
              <button
                className="switch"
                role="switch"
                aria-label="减少动态效果"
                aria-checked={props.reduceMotion}
                onClick={() => props.setReduceMotion(!props.reduceMotion)}
              >
                <span />
              </button>
            </div>
          </section>
          <section id="settings-learning" className="settings-section">
            <div className="settings-section-title">
              <div>
                <h2>学习与路径</h2>
                <p>控制开始探索时的工作区。</p>
              </div>
            </div>
            <div className="settings-row">
              <div>
                <b>默认显示路径图</b>
                <p>打开新的解释时，在正文旁显示当前路径。</p>
              </div>
              <button
                className="switch"
                role="switch"
                aria-label="默认显示路径图"
                aria-checked={props.defaultGraph}
                onClick={() => props.setDefaultGraph(!props.defaultGraph)}
              >
                <span />
              </button>
            </div>
            <div className="settings-row">
              <div>
                <b>已知概念</b>
                <p>
                  你主动标记了 {props.knownCount} 个义项，可以随时查看和撤销。
                </p>
              </div>
              <button className="button secondary" onClick={props.openKnown}>
                管理
              </button>
            </div>
            <div className="settings-hint">
              <Info size={16} />
              标记“我懂”是自我报告；系统不会把浏览或可达当成掌握。
            </div>
          </section>
          <section id="settings-data" className="settings-section">
            <div className="settings-section-title">
              <div>
                <h2>数据与状态</h2>
                <p>当前版本、解释卡片和本地保存状态。</p>
              </div>
            </div>
            <div className="data-status">
              <span
                className={
                  "status-indicator " + (props.health ? "ready" : "offline")
                }
              />
              <div>
                <b>{props.health ? "本地数据已连接" : "本地数据尚未连接"}</b>
                <p>
                  {props.health
                    ? `${props.health.head_count.toLocaleString()} 个义项 · ${props.health.clause_count.toLocaleString()} 条定义分支`
                    : "请检查本地服务和数据索引。"}
                </p>
              </div>
            </div>
            <div className="settings-row">
              <div>
                <b>数据版本</b>
                <p>用于判断分享的解释卡片是否匹配当前数据。</p>
              </div>
              <code
                className="settings-fingerprint"
                title={props.health?.fingerprint}
              >
                {props.health?.fingerprint.slice(0, 16) ?? "未连接"}…
              </code>
            </div>
            <div className="settings-row">
              <div>
                <b>解释卡片</b>
                <p>导出当前目标、分支和已知概念，或导入相同数据版本的卡片。</p>
              </div>
              <div className="settings-actions">
                <button className="button secondary" onClick={props.onImport}>
                  <Upload size={15} />
                  导入
                </button>
                <button className="button secondary" onClick={props.onExport}>
                  <Download size={15} />
                  导出
                </button>
              </div>
            </div>
            <div className="settings-row">
              <div>
                <b>最近探索</b>
                <p>
                  当前保存 {props.recentCount} 条，最多保留 20
                  条。清除后当前解释不会改变。
                </p>
              </div>
              <button
                className="button secondary"
                onClick={props.onClearRecent}
                disabled={!props.recentCount}
              >
                清除记录
              </button>
            </div>
            <div className="settings-row">
              <div>
                <b>重置当前学习状态</b>
                <p>清除当前目标、已知概念和展开记录。主题和阅读设置会保留。</p>
              </div>
              <button className="button danger" onClick={props.onReset}>
                重置状态
              </button>
            </div>
          </section>
          <section id="settings-about" className="settings-section">
            <div className="settings-section-title">
              <div>
                <h2>关于知径</h2>
                <p>基于冻结定义依赖图的本地研究原型。</p>
              </div>
            </div>
            <div className="settings-hint">
              <ShieldCheck size={16} />
              数据在本机读取；结构可追溯不等同于语义已审核。请使用“查看依据”检查每条分支。
            </div>
            <div className="settings-row">
              <div>
                <b>应用版本</b>
                <p>本地单用户版本</p>
              </div>
              <span className="settings-version">1.1.0</span>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
