# XBlackBox 安全性和日志改进 / Security and Logging Improvements

## 概述 / Overview

本次更新为 XBlackBox Tauri 应用添加了全面的安全措施和日志记录功能，解决了加载 XDR 文件时的错误处理问题。

This update adds comprehensive security measures and logging functionality to the XBlackBox Tauri application, addressing error handling issues when loading XDR files.

## 主要改进 / Major Improvements

### 1. 安全性增强 / Security Enhancements

#### 文件路径验证 / File Path Validation
- ✅ 路径清理和规范化 / Path sanitization and canonicalization
- ✅ 防止路径遍历攻击 / Path traversal attack prevention
- ✅ 文件扩展名验证 / File extension validation
- ✅ 文件大小限制（500MB）/ File size limits (500MB)
- ✅ 文件存在性和权限检查 / File existence and permission checks

```rust
// 使用示例 / Usage example
let validated_path = validate_file_path(&filepath)?;
```

#### 错误消息清理 / Error Message Sanitization
- ✅ 防止敏感路径信息泄露 / Prevents sensitive path information leakage
- ✅ 限制错误消息长度 / Limits error message length
- ✅ 仅显示文件名，不显示完整路径 / Shows only filename, not full path

### 2. 日志系统 / Logging System

#### 日志存储位置 / Log Storage Location
日志文件存储在用户主目录：
Log files are stored in the user's home directory:

```
~/.xblackbox/logs/xblackbox_YYYYMMDD.log
```

**Windows**: `C:\Users\<username>\.xblackbox\logs\`
**macOS**: `/Users/<username>/.xblackbox/logs/`
**Linux**: `/home/<username>/.xblackbox/logs/`

#### 日志功能 / Logging Features
- ✅ 按日期自动分割日志文件 / Automatic log file splitting by date
- ✅ 日志轮转（保留最近30天）/ Log rotation (keeps last 30 days)
- ✅ 多级别日志（INFO, WARN, ERROR, DEBUG）/ Multi-level logging
- ✅ 时间戳（精确到毫秒）/ Timestamps (millisecond precision)
- ✅ 启动时自动创建日志目录 / Auto-creates log directory on startup

#### 日志示例 / Log Example
```
[2025-12-08 12:00:30.123] [INFO] XBlackBox Viewer started
[2025-12-08 12:00:30.124] [INFO] Log file: /home/user/.xblackbox/logs/xblackbox_20251208.log
[2025-12-08 12:01:15.456] [INFO] Attempting to load file: test.xdr
[2025-12-08 12:01:15.789] [INFO] Successfully loaded file: 1234 frames, 45 parameters
[2025-12-08 12:02:30.012] [ERROR] File validation failed: File too large
```

### 3. 改进的错误处理 / Improved Error Handling

#### 前端错误处理 / Frontend Error Handling
- ✅ JSON 响应验证 / JSON response validation
- ✅ Content-Type 检查 / Content-Type checking
- ✅ 防止 HTML 错误页面被解析为 JSON / Prevents HTML error pages from being parsed as JSON
- ✅ 详细的错误消息和上下文 / Detailed error messages with context

```javascript
// 改进前 / Before
return response.json();  // 可能抛出 "Unexpected token '<'" 错误

// 改进后 / After
const contentType = response.headers.get('content-type');
if (!contentType || !contentType.includes('application/json')) {
    throw new Error('Server returned non-JSON response');
}
return response.json();
```

#### 后端错误处理 / Backend Error Handling
- ✅ 所有关键操作都有日志记录 / All critical operations are logged
- ✅ 错误消息清理（防止信息泄露）/ Error message sanitization
- ✅ 详细的验证错误 / Detailed validation errors
- ✅ 优雅的错误恢复 / Graceful error recovery

### 4. 新增 API / New APIs

#### `get_log_path` 命令 / Command
获取当前日志文件路径：
Get the current log file path:

```javascript
const logPath = await api.getLogPath();
console.log('Logs stored at:', logPath);
```

## 安全改进详情 / Security Improvements Details

### 防护措施 / Protection Measures

| 威胁 / Threat | 防护措施 / Protection |
|--------------|----------------------|
| 路径遍历攻击 / Path Traversal | 路径规范化和 `..` 检测 / Path canonicalization and `..` detection |
| 文件注入 / File Injection | 严格的扩展名验证 / Strict extension validation |
| 拒绝服务 / DoS | 文件大小限制（500MB）/ File size limits (500MB) |
| 信息泄露 / Information Disclosure | 错误消息清理 / Error message sanitization |
| 无效输入 / Invalid Input | 全面的输入验证 / Comprehensive input validation |

### 代码示例 / Code Examples

#### 安全的文件加载 / Secure File Loading
```rust
// 1. 验证路径
let validated_path = validate_file_path(&filepath)?;

// 2. 记录日志
state.logger.log_info(&format!("Loading file: {}", sanitize_error_message(&filepath)));

// 3. 读取文件
let data = xdr::XDRData::read(&validated_path)?;

// 4. 记录成功
state.logger.log_info("File loaded successfully");
```

## 使用指南 / Usage Guide

### 查看日志 / Viewing Logs

#### 方法 1: 使用 API / Method 1: Using API
```javascript
// 在浏览器控制台中 / In browser console
const logPath = await api.getLogPath();
console.log('Log file location:', logPath);
```

#### 方法 2: 手动导航 / Method 2: Manual Navigation
1. 打开文件管理器 / Open file manager
2. 导航到主目录 / Navigate to home directory
3. 进入 `.xblackbox/logs/` 文件夹 / Go to `.xblackbox/logs/` folder
4. 查看日志文件 / View log files

### 日志分析 / Log Analysis

日志文件可以帮助诊断问题：
Log files help diagnose issues:

- **加载失败** / **Load failures**: 查找 `[ERROR]` 行 / Look for `[ERROR]` lines
- **性能问题** / **Performance issues**: 检查时间戳间隔 / Check timestamp intervals
- **用户操作** / **User actions**: 跟踪 `[INFO]` 日志 / Track `[INFO]` logs

## 测试 / Testing

### 安全测试场景 / Security Test Scenarios

1. **路径遍历测试** / **Path Traversal Test**
   ```
   ../../../etc/passwd  ❌ 应该被拒绝 / Should be rejected
   ```

2. **无效扩展名** / **Invalid Extension**
   ```
   test.txt  ❌ 应该被拒绝 / Should be rejected
   test.xdr  ✅ 应该被接受 / Should be accepted
   ```

3. **超大文件** / **Oversized File**
   ```
   > 500MB  ❌ 应该被拒绝 / Should be rejected
   < 500MB  ✅ 应该被接受 / Should be accepted
   ```

4. **不存在的文件** / **Non-existent File**
   ```
   /path/to/nonexistent.xdr  ❌ 应该返回友好错误 / Should return friendly error
   ```

## 性能影响 / Performance Impact

- ✅ **最小开销** / **Minimal overhead**: 路径验证 < 1ms / Path validation < 1ms
- ✅ **异步日志** / **Async logging**: 不阻塞主线程 / Does not block main thread
- ✅ **自动清理** / **Auto cleanup**: 日志轮转防止磁盘填满 / Log rotation prevents disk fill

## 向后兼容性 / Backward Compatibility

- ✅ 现有 API 保持不变 / Existing APIs remain unchanged
- ✅ 新功能是附加的 / New features are additive
- ✅ 不影响现有功能 / No impact on existing functionality

## 已知限制 / Known Limitations

1. **日志文件数量** / **Log File Count**: 最多保留 30 个日志文件 / Maximum 30 log files kept
2. **单个日志大小** / **Single Log Size**: 无限制，每天创建新文件 / Unlimited, new file created daily
3. **并发访问** / **Concurrent Access**: 使用互斥锁保护 / Protected by mutex

## 未来改进 / Future Improvements

- [ ] 可配置的日志级别 / Configurable log levels
- [ ] 日志文件压缩 / Log file compression
- [ ] 日志查看器 UI / Log viewer UI
- [ ] 导出日志功能 / Export logs functionality
- [ ] 日志搜索和过滤 / Log search and filtering

## 依赖项变更 / Dependency Changes

新增依赖 / New dependencies:
```toml
dirs = "5.0"  # 用于获取用户主目录 / For getting user home directory
```

## 贡献 / Contributing

如果您发现安全问题，请通过 GitHub Issues 报告。
If you discover security issues, please report via GitHub Issues.

## 许可证 / License

与主项目相同 / Same as main project
