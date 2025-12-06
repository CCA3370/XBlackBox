#pragma once

#include "common.h"
#include "Settings.h"
#include <map>

class DatarefManager {
public:
    // Singleton access
    static DatarefManager& Instance();
    
    // Initialize datarefs based on recording level
    void Init();
    
    // Reload datarefs (when settings change)
    void Reload();
    
    // Get all dataref definitions
    const std::vector<DatarefDef>& GetDatarefs() const { return m_datarefs; }
    
    // Read current values efficiently
    void ReadCurrentValues();
    
    // Get value accessors (for efficient writing)
    const std::vector<float>& GetFloatValues() const { return m_floatValues; }
    const std::vector<int>& GetIntValues() const { return m_intValues; }
    const std::vector<std::string>& GetStringValues() const { return m_stringValues; }
    
private:
    DatarefManager();
    ~DatarefManager() = default;
    DatarefManager(const DatarefManager&) = delete;
    DatarefManager& operator=(const DatarefManager&) = delete;
    
    void LoadDatarefs();
    void LoadBasicDatarefs();
    void LoadNormalDatarefs();
    void LoadDetailedDatarefs();
    
    void AddDataref(const std::string& name, const std::string& desc, DatarefType type, int arraySize = 0);
    
    std::vector<DatarefDef> m_datarefs;
    std::vector<float> m_floatValues;
    std::vector<int> m_intValues;
    std::vector<std::string> m_stringValues;
    
    // Indices for efficient lookup
    std::map<std::string, size_t> m_datarefIndex;
};
