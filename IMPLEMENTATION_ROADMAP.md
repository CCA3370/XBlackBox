# Implementation Plan: Advanced Features

## 完成的功能 / Completed Features ✅

### 1. Professional Black Box Analysis
- ✅ Approach stability analysis
- ✅ Climb and descent rate tracking  
- ✅ Anomaly detection (G-forces, descent rates)
- ✅ Enhanced UI with severity indicators

### 2. Performance Optimizations
- ✅ Smart data downsampling (preserves data quality)
- ✅ WebGL rendering for large datasets (10-100x faster)
- ✅ Optimized memory usage
- ✅ Smooth visualization of long flights

## 待实现的功能 / Features To Be Implemented

### 3. 3D Earth Rendering with Flight Trajectory (较大功能)

这是一个独立的功能模块，建议在新的PR中实现。

#### 技术方案 / Technical Approach

**推荐方案 A: Cesium.js (最佳选择)**
- 优点：专业的3D地球可视化库，支持离线瓦片
- 特性：
  - 高精度地形渲染
  - 支持OSM、Mapbox等多种地图源
  - 内置离线瓦片缓存
  - 3D飞行轨迹渲染
  - 机场标注功能

**方案B: Mapbox GL JS + Three.js**
- 优点：更轻量，自定义性强
- 需要：额外集成3D引擎

#### 实现步骤
1. 添加Cesium.js依赖到Tauri项目
2. 创建地球渲染组件
3. 实现离线地图瓦片下载和缓存
4. 绘制3D飞行轨迹
5. 标注起降机场位置

#### 离线地图存储方案
```rust
// Tauri后端实现瓦片缓存
- 使用本地SQLite数据库存储瓦片
- 首次加载自动下载并缓存
- 后续访问直接从本地读取
```

#### 预计工作量
- 2-3天开发时间
- 需要测试不同地图源
- 需要优化离线存储大小

---

### 4. X-Plane Plugin: Airport Detection (需要C++插件修改)

这需要修改X-Plane插件的C++代码，也建议在新的PR中实现。

#### 技术方案

使用X-Plane SDK的导航数据库API：

```cpp
// 在 Recorder.cpp 中添加机场检测功能

// 1. 在记录开始时检测当前机场
struct AirportInfo {
    char icao[8];
    char name[256];
    float lat;
    float lon;
};

AirportInfo DetectNearestAirport(float lat, float lon) {
    XPLMNavRef navRef = XPLMGetFirstNavAid();
    float minDistance = FLT_MAX;
    AirportInfo nearest = {0};
    
    while (navRef != XPLM_NAV_NOT_FOUND) {
        XPLMNavType navType;
        float navLat, navLon;
        char navID[32];
        char navName[256];
        
        XPLMGetNavAidInfo(navRef, &navType, &navLat, &navLon, 
                         nullptr, nullptr, nullptr,
                         navID, navName, nullptr);
        
        // Check if it's an airport
        if (navType == xplm_Nav_Airport) {
            float distance = CalculateDistance(lat, lon, navLat, navLon);
            if (distance < minDistance && distance < 5.0) { // Within 5 nm
                minDistance = distance;
                strncpy(nearest.icao, navID, sizeof(nearest.icao));
                strncpy(nearest.name, navName, sizeof(nearest.name));
                nearest.lat = navLat;
                nearest.lon = navLon;
            }
        }
        
        navRef = XPLMGetNextNavAid(navRef);
    }
    
    return nearest;
}

// 2. 修改XDR文件格式，在头部添加机场信息
struct XDRHeader {
    char magic[4];      // "XFDR"
    uint16_t version;   
    uint8_t level;
    float interval;
    uint64_t start_timestamp;
    uint16_t dataref_count;
    // 新增字段:
    char departure_icao[8];
    char arrival_icao[8];
    float departure_lat;
    float departure_lon;
    float arrival_lat;
    float arrival_lon;
};

// 3. 在记录开始和结束时调用检测
bool Recorder::Start() {
    // ... existing code ...
    
    // Detect departure airport
    float lat = XPLMGetDataf(XPLMFindDataRef("sim/flightmodel/position/latitude"));
    float lon = XPLMGetDataf(XPLMFindDataRef("sim/flightmodel/position/longitude"));
    m_departureAirport = DetectNearestAirport(lat, lon);
    
    // Write updated header
    WriteHeader();
    
    // ... rest of code ...
}

bool Recorder::Stop() {
    // ... existing code ...
    
    // Detect arrival airport
    float lat = XPLMGetDataf(XPLMFindDataRef("sim/flightmodel/position/latitude"));
    float lon = XPLMGetDataf(XPLMFindDataRef("sim/flightmodel/position/longitude"));
    m_arrivalAirport = DetectNearestAirport(lat, lon);
    
    // Update header with arrival info
    UpdateHeaderWithArrival();
    
    // ... rest of code ...
}
```

#### 实现步骤
1. 修改 `include/Recorder.h` 添加机场信息结构
2. 修改 `src/Recorder.cpp` 实现机场检测逻辑
3. 更新XDR文件格式版本号
4. 修改Rust解析器以读取新字段
5. 在Tauri界面显示机场信息

#### 预计工作量
- 1-2天开发时间
- 需要测试各种机场场景
- 需要更新文件格式文档

---

## 建议实施顺序

1. **当前PR**: 
   - ✅ 已完成专业分析功能
   - ✅ 已完成性能优化
   
2. **下一个PR (3D Earth Rendering)**:
   - 集成Cesium.js
   - 实现离线地图
   - 3D轨迹渲染
   - 机场标注

3. **第三个PR (X-Plane Plugin)**:
   - 修改C++插件代码
   - 机场检测功能
   - XDR格式更新
   - 测试和文档

## 技术依赖

### 3D Earth Rendering
```json
{
  "dependencies": {
    "cesium": "^1.110.0",
    "@types/cesium": "^1.110.0"
  }
}
```

### X-Plane Plugin
- X-Plane SDK (已有)
- 导航数据库API (XPLM Navigation APIs)
- 无需额外依赖

## 参考资料

- Cesium.js Documentation: https://cesium.com/learn/cesiumjs/
- X-Plane SDK Navigation APIs: https://developer.x-plane.com/sdk/XPLMNavigation/
- OSM Tile Servers: https://wiki.openstreetmap.org/wiki/Tile_servers
