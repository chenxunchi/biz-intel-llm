# 📊 Data Management

This directory manages temporary data storage and caching for the Business Intelligence system.

## 📁 Structure

### `/scraped_content/` Directory
**Temporary data storage** for scraped website content during analysis.

**Subdirectories:**
- `cache/` - Temporary caching for repeated URL analysis
- `images/` - Temporary storage for downloaded business images  
- `text/` - Temporary storage for extracted text content

## 🔄 Data Flow

### Storage Pattern
```
URL Analysis → Temporary Storage → AI Processing → Results → Cleanup
```

### Data Lifecycle
1. **Scraping Phase**: Content temporarily stored in subdirectories
2. **Analysis Phase**: Data processed by 3-pass pipeline
3. **Results Phase**: Final analysis generated
4. **Cleanup Phase**: Temporary data automatically cleaned up

## 🛠️ Data Management

### Automatic Cleanup
- **Stateless Design**: No persistent data storage required
- **Memory Processing**: Analysis runs entirely in memory when possible
- **Temporary Files**: Automatically cleaned up after analysis

### Cache Strategy
- **URL-based caching**: Avoid re-scraping recently analyzed websites
- **Configurable TTL**: Cache duration controlled via environment variables
- **Size Limits**: Automatic cleanup when cache size limits exceeded

## 🔧 Configuration

### Environment Variables
```bash
# Cache configuration (optional)
CACHE_TTL_HOURS=24
MAX_CACHE_SIZE_MB=100
ENABLE_CACHING=true
```

### Directory Permissions
- **Read/Write Access**: Required for temporary file operations
- **Cleanup Permissions**: Automatic file deletion capabilities
- **Size Monitoring**: Disk space usage tracking

## ⚠️ Important Notes

### Data Privacy
- **No Persistent Storage**: Business data not permanently stored
- **Temporary Processing**: All data processing is transient
- **Cleanup Guarantee**: System ensures no data persistence beyond analysis

### Performance Considerations
- **Disk I/O Optimization**: Minimal disk usage, primarily memory-based
- **Cleanup Automation**: Prevents disk space accumulation
- **Cache Benefits**: Reduces API calls for repeated analyses

### Troubleshooting
```bash
# Check disk space usage
du -sh data/scraped_content/

# Manual cleanup if needed
rm -rf data/scraped_content/cache/*
rm -rf data/scraped_content/images/*
rm -rf data/scraped_content/text/*
```