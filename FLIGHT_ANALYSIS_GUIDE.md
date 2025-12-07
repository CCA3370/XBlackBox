# Flight Analysis Feature - User Guide

## 航空黑匣子分析功能用户指南

### 概述 / Overview

新的飞行分析功能专为航空飞行数据分析设计，取代了原有的FFT频率分析功能。

The new Flight Analysis feature is designed specifically for aviation flight data analysis, replacing the previous FFT frequency analysis.

---

### 功能特点 / Features

#### 1. 飞行阶段检测 / Flight Phase Detection
自动识别飞行的不同阶段：
- **起飞 (Takeoff)**: 当高度超过10英尺AGL时检测
- **降落 (Landing)**: 当高度下降到10英尺AGL以下时检测

Automatically identifies different flight phases:
- **Takeoff**: Detected when altitude exceeds 10 feet AGL
- **Landing**: Detected when altitude drops below 10 feet AGL

#### 2. 关键性能指标 / Key Performance Metrics
- **总飞行时间 / Total Flight Time**: 完整飞行的持续时间
- **最大高度 / Max Altitude**: 飞行过程中达到的最高高度
- **最大速度 / Max Speed**: 记录的最高地速
- **平均燃油流量 / Average Fuel Flow**: 全程平均燃油消耗率（如果数据可用）
- **着陆G力 / Landing G-Force**: 着陆时的垂直加速度（如果数据可用）

#### 3. 相位时间轴 / Phase Timeline
显示每个飞行阶段的：
- 开始时间
- 持续时间

Shows for each flight phase:
- Start time
- Duration

---

### 使用方法 / How to Use

1. **加载XDR文件 / Load XDR File**
   - 点击"打开文件"按钮
   - 选择一个XDR飞行数据文件
   
   Click "Open File" button and select an XDR flight data file

2. **切换到飞行分析标签 / Switch to Flight Analysis Tab**
   - 在主界面点击"Flight Analysis"标签
   
   Click the "Flight Analysis" tab in the main interface

3. **运行分析 / Run Analysis**
   - 点击"Analyze Flight"按钮
   - 系统将自动分析飞行数据
   
   Click "Analyze Flight" button, system will automatically analyze the flight data

4. **查看结果 / View Results**
   - 飞行摘要显示关键指标
   - 飞行阶段表格显示详细的阶段信息
   
   Flight summary shows key metrics
   Phase table shows detailed phase information

---

### 数据要求 / Data Requirements

为了获得最佳分析结果，XDR文件应包含以下数据：

For best analysis results, the XDR file should contain:

- **必需 / Required**:
  - 高度AGL (Altitude AGL)
  - 地速 (Ground Speed)
  
- **可选 / Optional**:
  - 垂直速度 (Vertical Speed)
  - 燃油流量 (Fuel Flow)
  - G力 (G-Force/G Load)

---

### 技术实现 / Technical Implementation

#### 后端 / Backend (Rust)
```rust
// 在 src-tauri/src/lib.rs 中实现
#[tauri::command]
async fn analyze_flight(state: State<'_, AppState>) -> Result<FlightAnalysis, String>
```

功能：
- 解析XDR数据
- 检测飞行阶段
- 计算性能指标
- 返回结构化分析结果

Features:
- Parses XDR data
- Detects flight phases
- Calculates performance metrics
- Returns structured analysis results

#### 前端 / Frontend (JavaScript)
```javascript
// 在 static/js/app.js 中实现
async function loadFlightAnalysis()
```

功能：
- 调用后端分析API
- 渲染分析结果
- 显示交互式表格

Features:
- Calls backend analysis API
- Renders analysis results
- Displays interactive tables

---

### 与FFT功能的对比 / Comparison with FFT

| 特性 / Feature | FFT 频率分析 | 飞行阶段分析 |
|---------------|------------|------------|
| 用途 / Purpose | 信号频率分析 | 航空飞行分析 |
| 输出 / Output | 频谱图 | 飞行阶段和指标 |
| 应用场景 / Use Case | 振动分析 | 飞行复盘 |
| 航空相关性 / Aviation Relevance | 低 / Low | 高 / High |

---

### 未来增强 / Future Enhancements

计划添加的功能：
- 进近分析（下滑道偏差）
- 起飞性能分析
- 燃油效率分析
- 自动异常检测
- 导出分析报告

Planned features:
- Approach analysis (glideslope deviation)
- Takeoff performance analysis
- Fuel efficiency analysis
- Automatic anomaly detection
- Export analysis reports

---

### 常见问题 / FAQ

**Q: 为什么看不到某些指标？**
A: 某些指标（如燃油流量、G力）取决于XDR文件中是否记录了相应的数据。

**Q: Why are some metrics not shown?**
A: Some metrics (like fuel flow, G-force) depend on whether the corresponding data was recorded in the XDR file.

**Q: 飞行阶段检测不准确怎么办？**
A: 当前使用10英尺AGL作为阈值。未来版本将允许自定义阈值。

**Q: What if flight phase detection is inaccurate?**
A: Currently uses 10 feet AGL as threshold. Future versions will allow custom thresholds.

---

### 技术支持 / Support

如有问题或建议，请访问：
For issues or suggestions, visit:
https://github.com/CCA3370/XBlackBox/issues
