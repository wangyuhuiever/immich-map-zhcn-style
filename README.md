# Immich 中文地图样式 (Immich Map Chinese Vector Style)

<p align="center">
  <img src="https://img.shields.io/badge/Immich-Compatible-4378ff?style=for-the-badge&logo=photopea&logoColor=white" alt="Immich Compatible" />
  <img src="https://img.shields.io/badge/Language-Simplified%20Chinese%20%7C%20Bilingual-10b981?style=for-the-badge" alt="Language" />
  <img src="https://img.shields.io/badge/Tile%20Source-Protomaps%20(Official%20Immich)-7928ca?style=for-the-badge" alt="Protomaps" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" alt="License" />
</p>

专为 [Immich](https://immich.app/) 自托管照片管理系统定制的 **全球中文矢量地图样式**。完美解决官方默认地图在 **安卓 App (Android) 和 iOS 移动端只显示纯英文**、在 Web 端显示混乱的问题。

---

## 🌟 核心特性

- 🇨🇳 **原生中文优先**：全球主要国家、省份、城市、区县、岛屿、湖泊水系、道路 POI 优先显示简体中文（`name:zh-Hans` / `name:zh` / `name`）。
- 📱 **全平台三端一致**：彻底修复安卓 App、iOS App 和 Web 网页端在地图名称渲染上的差异。
- 💸 **完全免费零门槛**：直接使用 Immich 官方内置的全球矢量瓦片源（Protomaps Basemap 4.x），**无需注册 MapTiler、无需 Mapbox Key、无需配置任何 Token，开箱即用**。
- 🌓 **深浅双色主题**：提供 **亮色 (Light)** 与 **暗色 (Dark)** 完整配色，与 Immich 系统主题完美契合。
- 🔤 **双模式可选**：支持 **纯中文模式**（界面干净极简）和 **中英双语对照模式**（国内单行中文，海外双行中英）。

---

## 🔍 为什么官方默认地图在安卓 App 只有英文？

1. **官方样式的回退机制问题**：
   - 官方默认样式的国家层级（`places_country`）直接写死了只读取 `name:en`（纯英文）。
   - 城市和地名图层使用了针对复杂排版的 `is-supported-script` 条件表达式。在 Web 端浏览器（MapLibre GL JS）中能够识别并进入双语格式化；但在移动端（MapLibre Native C++ 渲染核心）中该条件判定失败，**自动退回到了最底层的 `["get", "name:en"]` 分支**，导致手机 App 上所有地名全部变成英文。
2. **官方未启用中文检索字段**：
   - Immich 官方瓦片源中其实已经包含了完整的 `name:zh-Hans` 简体中文数据，但官方默认样式从未检索该字段，导致即使有中文翻译的海外地名（如 New York、London、Tokyo、Paris）也只能显示英文或当地语言。
3. **本项目重构**：
   - 重构了全部 13 个文本符号图层的表达式，使用全平台 100% 兼容的 `coalesce` / `concat` 逻辑，优先读取 `name:zh-Hans`。

---

## 🚀 快速使用 (直接复制 URL 配置)

登录 Immich 网页端管理后台：
1. 点击右上角头像 → **Administration (管理)**。
2. 在左侧菜单进入 **Settings (设置)** → **Map & GPS Settings (地图与 GPS 设置)**。
3. 展开 **Map Settings (地图设置)**。
4. 将下方对应的 URL 填入 **Light Style** 和 **Dark Style** 输入框中。
5. 点击 **Save (保存)**，刷新网页或重启手机 App 即可生效！

### 方案 A：纯中文优先（推荐 🌟）

> 国内国外全部优先显示中文名称，无中文翻译时显示本地原名或英文。

- **Light Style (亮色)**:
  ```text
  https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-light.json
  ```
- **Dark Style (暗色)**:
  ```text
  https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-dark.json
  ```

---

### 方案 B：中英双语对照

> 国内地名显示中文，国外地名第一行显示中文、第二行显示英文/原名。

- **Light Style (亮色)**:
  ```text
  https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-light-bilingual.json
  ```
- **Dark Style (暗色)**:
  ```text
  https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-dark-bilingual.json
  ```

---

### 国内网络加速链接 (ghproxy 代理)

<details>
<summary>点击展开查看国内加速代理链接 (直连 GitHub 较慢时使用)</summary>

- 亮色纯中文: `https://ghproxy.net/https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-light.json`
- 暗色纯中文: `https://ghproxy.net/https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-dark.json`
- 亮色双语: `https://ghproxy.net/https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-light-bilingual.json`
- 暗色双语: `https://ghproxy.net/https://raw.githubusercontent.com/wangyuhuiever/immich-map-zhcn-style/main/style-dark-bilingual.json`

</details>

---

## 🛠️ 本地/内网离线自建托管方案

如果您希望完全不依赖外网 CDN，将样式文件部署在自己的 NAS 或 Immich 同台机器上：

### 方法 1：使用 Nginx 容器托管
在 `docker-compose.yml` 中添加一个极简的静态 Web 服务：
```yaml
services:
  map-style:
    image: nginx:alpine
    container_name: immich_map_style
    restart: unless-stopped
    ports:
      - "8088:80"
    volumes:
      - ./styles:/usr/share/nginx/html:ro
```
将本项目中的 `style-light.json` 和 `style-dark.json` 放置到 `./styles` 目录中。
然后在 Immich 的 Map Settings 中填入：
- `http://<您的NAS局域网IP>:8088/style-light.json`
- `http://<您的NAS局域网IP>:8088/style-dark.json`

---

## 🔄 自动化更新与构建 (GitHub Actions)

本项目配置了 **GitHub Actions 定时工作流**（[`.github/workflows/sync-styles.yml`](file:///.github/workflows/sync-styles.yml)）：
- **每天北京时间 11:00 (UTC 03:00) 自动运行**。
- 自动拉取 Immich 官方最新发布的矢量地图样式进行分析。
- 当官方样式更新（如调整配色、新增地物图层）时，Action 会自动将中文逻辑注入并提交更新到仓库。
- 支持在 GitHub 仓库的 **Actions** 标签页中随时点击 **Run workflow** 手动触发即时构建。

本地手动构建（支持 Python / PowerShell）：
```bash
# 使用 Python 构建 (跨平台 / Linux / macOS / Windows)
python build.py

# 或使用 PowerShell 构建 (Windows)
powershell -ExecutionPolicy Bypass -File .\generate_styles.ps1
```

---

## 📋 常见问题 (FAQ)

**Q: 更改样式后，安卓 App 地图还是英文怎么办？**  
A: 安卓 App 会缓存旧的地图瓦片和样式数据。进入手机系统设置 → **应用管理** → 找到 **Immich** → **存储占用** → **清除缓存 (Clear Cache)**，然后重新打开 Immich 即可。

**Q: 是否需要开启代理才能加载地图？**  
A: 地图瓦片源使用的是 Immich 官方全球 CDN（`tiles.immich.cloud`），正常情况下均可直连。如果直连 GitHub 获取样式 JSON 较慢，可选用上方提供的国内加速代理链接或使用本地 Nginx 托管。

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。地图矢量数据源来自 [OpenStreetMap](https://www.openstreetmap.org/copyright) 及 [Protomaps](https://protomaps.com/)。

