# 猎户信号 · 故事学单词（Orion）

> 一个把 **科幻英雄之旅故事** 和 **NGSL 1.2 高频词表（2809 词）** 结合在一起的网页英语学习应用（PWA，可装到手机主屏幕）。
> 当前版本：**v4.16**

## 这是什么

《猎户信号 / The Last Signal of Orion》用一篇原创科幻英雄之旅故事串起英语最常用的 2809 个核心词（NGSL 1.2）。读故事时，生词会标成蓝色，点一下就能看中文释义、听发音、加入复习。

核心特性：

- **分级阅读（L1–L4）**：按词汇量分四档（≈500 / 1000 / 1800 / 2809 词头，对应 CEFR A1 / A2 / B1 / B2）。首启做一次自适应起点测试，自动挑合适的难度。
- **自适应起点测试**：约 20 题的二分定位 + 边界探测，给出「词汇量估计区间」（含正常作答误差），不是死板的固定题数。
- **蓝词即生词**：系统按你的已知词估算哪些不认识，标蓝；点任意单词（含已认识的词和专有名词）都能查释义。
- **轻量间隔复习（SM-2 风格）**：标记的词进入复习队列，按简化间隔算法复习。
- **打赏**：「我」页可放收款码（占位图 `donate.png`，替换成你自己的即可）。
- **可安装 PWA**：支持 Service Worker 离线缓存、添加到主屏幕。

## 本地运行

应用用到了 Service Worker 和 `fetch` 加载 `ngsl_gloss.json`，**不能直接双击 `file://` 打开**，需要一个本地 HTTP 服务器：

```bash
# 进入构建产物目录
cd dist
# 用 Python 起一个静态服务器（或用任意静态服务器）
python -m http.server 8080
# 浏览器打开
# http://localhost:8080
```

`dist/` 里已经是可直接部署的成品（含 `index.html`、`sw.js`、`manifest.webmanifest`、图标、`ngsl_gloss.json`、`LICENSE.txt`、`donate.png`）。

## 从源码构建

源码在仓库根目录，构建脚本会读取 `index_template.html` + `data.js`，把数据内联进单文件 HTML：

```bash
node build_app.js
```

这会输出 `index.html`（根目录，便于本地预览）和 `dist/index.html`（部署用）。

> ⚠️ 注意：`build_app.js` 只注入数据，**不会**自动同步 `sw.js`。如果你改了缓存内容，记得手动把 `sw.js` 和 `dist/sw.js` 的 `CACHE` 名称 bump 一下（当前 `orion-v4-16`），否则老用户不会拿到更新。

## 目录结构

```
.
├── index_template.html   # 应用主模板（含所有逻辑 + __APP_DATA__ 占位）
├── data.js               # 故事 + 词表数据（window.APP_DATA）
├── build_app.js          # 构建脚本：注入数据 → index.html / dist/index.html
├── gen_story.py          # 故事生成管线（读取词表 → 生成 data.js）
├── dist/                 # 构建产物，可直接部署 / 本地运行
│   ├── index.html
│   ├── sw.js
│   ├── manifest.webmanifest
│   ├── ngsl_gloss.json
│   ├── LICENSE.txt
│   ├── donate.png
│   └── app-icon-*.png
└── LICENSE.txt
```

## 数据来源与许可

- **NGSL 1.2 词表**：(C) Browne, Culligan & Phillips (2013)，来源 https://www.newgeneralservicelist.com ，按 **CC BY-SA 4.0** 使用。
- **故事《猎户座的最后信号》**：runking 原创，CC BY-SA 4.0。
- **中文释义与「猎户档案」16–23 章**：基于 NGSL 英文释义改编的衍生内容，CC BY-SA 4.0。

整体以 **CC BY-SA 4.0** 发布，详见 `LICENSE.txt`。

> ⚠️ **待确认（pending confirmation）**：随包发布的 2809 条英文释义，是从一份本地词表文件汇编而来，未逐条标注出处。如果它们并非 NGSL 1.2 官方原文的逐字内容，上面的 NGSL 署名在公开发布前可能需要更正。这部分需要作者确认来源后再定性。

## 部署

`dist/` 是纯静态文件，可部署到任意静态托管（本仓库示例部署在 CloudStudio 沙箱）。改 `sw.js` 后务必 bump `CACHE` 名称以触发更新；导航策略为 network-first，在线用户会自动拿到新的 `index.html`。

## 版本

当前 `v4.16`。版本号在以下位置保持一致：`index_template.html` 标题/副标题、`manifest.webmanifest`、导出数据、`LICENSE.txt`。
