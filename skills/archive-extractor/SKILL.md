# Archive Extractor

**生产级压缩文件处理** - 借鉴 7-Zip, libarchive, patool

支持ZIP, RAR, 7Z, TAR, GZIP, BZIP2, XZ等格式，自动检测、安全解压。

---

## 核心特性

### 📦 支持格式

| 格式 | 扩展名 | 压缩 | 解压 |
|------|--------|------|------|
| **ZIP** | .zip | ✅ | ✅ |
| **RAR** | .rar | ❌ | ✅ |
| **7-Zip** | .7z | ✅ | ✅ |
| **TAR** | .tar | ✅ | ✅ |
| **GZIP** | .gz, .tgz | ✅ | ✅ |
| **BZIP2** | .bz2, .tbz2 | ✅ | ✅ |
| **XZ** | .xz, .txz | ✅ | ✅ |

### 🛡️ 安全特性

- **路径遍历防护**: 阻止../恶意路径
- **Zip Bomb检测**: 压缩比异常检测
- **病毒扫描集成**: 可选ClamAV
- **权限保留**: Unix权限/ACL

---

## 使用方法

### 解压
```bash
# 自动检测格式
extract archive.zip
extract archive.tar.gz

# 指定输出目录
extract archive.zip -o ./output

# 列出内容
extract archive.zip --list

# 测试完整性
extract archive.zip --test
```

### 压缩
```bash
# 创建ZIP
create archive.zip file1 file2 dir/

# 创建7Z (高压缩)
create archive.7z dir/ --level=9

# 分卷压缩
create archive.zip large_file --split=100M
```

---

## 参考实现

- **7-Zip**: https://www.7-zip.org/
- **libarchive**: https://www.libarchive.org/
- **patool**: Python压缩工具

---

## 版本信息

- **Version**: 2.0.0
- **Author**: KbotGenesis
- **References**: 7-Zip, libarchive
