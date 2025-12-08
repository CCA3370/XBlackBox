## 快速上手 — 给 AI 编码代理的项目说明

目标：帮助 AI 代理在本仓库中高效定位责任边界、常用命令、关键模式和可直接编辑的代码位置。

要点（简短）：
- 代码库由三大部分组成：
  - C++ 插件 (src/, include/, SDK/)：核心功能，生成 X-Plane 插件 (.xpl)。关键入口 `src/main.cpp`。主类使用单例（Settings, DatarefManager, Recorder, UIManager）。
  - Tauri 桌面查看器 (web_viewer/)：Rust 后端解析 XDR（`web_viewer/src-tauri/src/xdr.rs`），前端在 `web_viewer/static/`，构建脚本 `web_viewer/build.sh`、`package.json`。
  - Python 旧版查看器/工具：根目录下的 `xdr_viewer.py` / `xdr_reader.py`，依赖 `requirements.txt`。

快速命令（可直接运行，已在 README/BUILD.md 中）：
- 构建插件（跨平台，CMake）：
  - mkdir build && cd build
  - cmake ..
  - cmake --build . --config Release
  - cmake --install .
- 构建 Tauri 查看器：
  - cd web_viewer
  - npm install
  - npm run build   # 或使用 web_viewer/build.sh
- 运行 Python 查看器（legacy）：
  - pip install -r requirements.txt
  - python xdr_viewer.py

重要位置（文件/目录示例）：
- 插件入口与生命周期：`src/main.cpp`（初始化单例、flight loop 回调，注意回调必须非常轻量）
- 数据/录制核心：`src/Recorder.cpp`、`include/Recorder.h`、`src/DatarefManager.cpp`
- 配置与持久化：`Settings` 单例（`src/Settings.cpp`、`include/Settings.h`），默认配置保存在 X-Plane 输出目录 `Output/XBlackBox/config.ini`
- XDR 格式与查看器：`web_viewer/src-tauri/src/xdr.rs`（Rust 解析器），Python 读取/工具在 `xdr_reader.py` / `xdr_viewer.py`
- CI 构建工作流：`.github/workflows/build.yml`（自动发布构建产物）

项目约定与可修改点（对 AI 很重要）：
- Singleton 模式广泛使用：优先查找 `Class::Instance()` 用法以定位主要状态与副作用位置（例如 Recorder 的 Start/Stop/Update）。
- Flight loop callback（`src/main.cpp`）是热点：避免在回调中做阻塞 I/O 或昂贵计算；若需扩展，建议将重负载移到异步队列或后台线程。
- 日志与调试：插件日志写入 X-Plane 的 `Log.txt`（检查 README 中的“Plugin starting/started”字符串）。修改需同时考虑在异常路径下的稳定性（不要抛出异常导致插件崩溃）。
- 文件输出路径与格式：录制文件在 `X-Plane 12/Output/XBlackBox/`，文件名 `flightdata_YYYYMMDD_HHMMSS.xdr`；解析器与查看器假设该格式（改动需双向兼容）。

常见任务的具体示例（可直接实现或修改）：
- 添加新的 DataRef（参数）：修改 `include/DatarefManager.h` 与 `src/DatarefManager.cpp`，并在 Recorder 的数据帧定义中注册（查看 Dataref 定义/映射实现）。
- 在 Tauri 后端暴露新命令：编辑 `web_viewer/src-tauri/src/lib.rs` 添加命令，并在前端 `web_viewer/static/js/tauri-api.js` 中注册调用。
- 优化写入性能：优先在 `src/Recorder.cpp` 中检查缓冲写入、批量序列化与后台 flush 策略。

要避免的错误与陷阱：
- 不要在 `FlightLoopCallback` 中做文件系统同步写入或长时间阻塞操作。
- 修改 XDR 的二进制布局需同时更新 `web_viewer/src-tauri/src/xdr.rs` 与 Python 读取器（`xdr_reader.py`），并保持向后兼容或增加版本标记。

质量门与验证（可自动化）：
- 本仓库没有单元测试框架；但每次更改核心 C++/Rust 解析器后，应：
  1) 本地构建（CMake / npm / cargo），
  2) 使用 `uploads/flightdata_20251207_164533.xdr`（示例文件）做解析回归测试（确保 viewer 能打开且字段匹配），
  3) 检查 X-Plane Log.txt 是否含异常信息。

如何提出变更（PR 指南）
- 小变更：修改对应模块并在 PR 描述中列出受影响的运行步骤（例如“运行 cmake && cmake --build 后验证 plugin 加载”）。
- 涉及文件格式或跨语言改动：在 PR 中提供兼容策略与回归测试步骤（包括用例 xdr 文件和解析前/后对比）。

如果有不清楚的部分，请指定：
- 想要补充的主题（例如：更详细的 CMake 变量说明、更多代码位置引用、或示例 PR 模板）

---
参考文件（起点）：
- `README.md`, `BUILD.md`, `QUICKSTART.md`
- `src/main.cpp`, `src/Recorder.cpp`, `include/Recorder.h`
- `web_viewer/README.md`, `web_viewer/build.sh`, `web_viewer/package.json`, `web_viewer/src-tauri/src/xdr.rs`
- CI: `.github/workflows/build.yml`

请审阅这份简短说明并告诉我是否需要把某个部分扩展为更详细的步骤或示例代码片段。
