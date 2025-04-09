# Mirror-Leech-Telegram-Bot 中文说明文档

本 Telegram 机器人基于 [python-aria-mirror-bot](https://github.com/lzzy12/python-aria-mirror-bot)，经过了大量修改，旨在高效地将互联网上的文件镜像或下载到各种目的地，包括 Google Drive、Telegram 或任何 rclone 支持的云存储。它使用 Python 的异步编程构建。

**特别版本说明**：本版本在原版基础上进行了全面汉化，并集成了 Alist 文件管理系统，方便用户管理和访问云端文件。

- **Telegram 频道:** https://t.me/mltb_official_channel
- **Telegram 群组:** https://t.me/mltb_official_support

<details>
  <summary><h1>功能特性</h1></summary>

<details>
  <summary><h5>QBittorrent</h5></summary>

- 支持外部访问 WebUI，可以删除文件或编辑设置，然后可以通过机器人设置中的同步按钮同步到数据库
- 在下载前和下载过程中使用 MLTB 文件选择器选择种子文件（需要基本 URL）（任务选项）
- 将种子做种到特定的比率和时间（任务选项）
- 在机器人运行时通过机器人设置编辑全局选项（全局选项）

</details>

<details>
  <summary><h5>Aria2c</h5></summary>

- 在下载前和下载过程中选择种子文件（需要基本 URL）（任务选项）
- 将种子做种到特定的比率和时间（任务选项）
- 支持 Netrc 认证（全局选项）
- 在使用机器人时为特定链接进行直接链接认证（即使仅提供用户名或密码也可以工作）（任务选项）
- 在机器人运行时通过机器人设置编辑全局选项（全局选项）

</details>

<details>
  <summary><h5>Sabnzbd</h5></summary>

- 支持外部访问 Web 界面，可以删除文件或编辑设置，然后可以通过机器人设置中的同步按钮同步到数据库
- 在下载前和下载过程中使用 MLTB 文件选择器从任务中删除文件（需要基本 URL）（任务选项）
- 在机器人运行时通过机器人设置编辑全局选项（全局选项）
- 服务器菜单，用于编辑/添加/删除 Usenet 服务器

</details>

<details>
  <summary><h5>TG 上传/下载</h5></summary>

- 分割大小（全局、用户和任务选项）
- 缩略图（用户和任务选项）
- 下载文件名前缀（用户选项）
- 设置上传为文档或媒体（全局、用户和任务选项）
- 将所有文件上传到特定的聊天（超级群组/频道/私人/话题）（全局、用户和任务选项）
- 平均分割大小设置（全局和用户选项）
- 能够在媒体组中下载分割文件部分（全局和用户选项）
- 通过 TG 私人/公共/超级链接下载受限消息（文档或链接）（任务选项）
- 如果您有高级套餐，可以选择使用机器人或用户会话进行传输（全局、用户和任务选项）
- 根据文件大小混合使用用户和机器人会话上传（全局、用户和任务选项）
- 使用自定义布局的多个缩略图上传（全局、用户和任务选项）
- 支持话题功能

</details>

<details>
  <summary><h5>Google Drive</h5></summary>

- 从/向 Google Drive 下载/上传/克隆/删除/计数
- 计算 Google Drive 文件/文件夹数量
- 在多个 Drive 文件夹/TeamDrive 中搜索
- 对于所有 Gdrive 功能，如果使用服务帐户找不到文件，则使用 Token.pickle
- 为每个任务随机使用服务帐户
- 递归搜索（仅适用于 `root` 或 TeamDrive ID，文件夹 ID 将使用非递归方法列出）。基于 [Sreeraj](https://github.com/SVR666) 的 searchX-bot。（任务选项）
- 停止重复（全局和用户选项）
- 自定义上传目的地（全局、用户和任务选项）
- 能够从列表中选择 token.pickle 或服务帐户和上传目的地，可以使用或不使用按钮（全局、用户和任务选项）
- 索引链接仅支持 [Bhadoo](https://gitlab.com/GoogleDriveIndex/Google-Drive-Index/-/blob/master/src/worker.js) 索引

</details>

<details>
  <summary><h5>Rclone</h5></summary>

- 不使用或使用随机服务帐户进行传输（下载/上传/服务器端克隆）（全局和用户选项）
- 能够从列表中选择配置、远程和路径，可以使用或不使用按钮（全局、用户和任务选项）
- 能够为每个任务或全局从配置中设置标志（全局、用户和任务选项）
- 能够使用按钮选择特定文件或文件夹进行下载/复制（任务选项）
- Rclone.conf（全局和用户选项）
- Rclone serve 用于将远程组合起来，将其用作所有远程的索引（全局选项）
- 上传目的地（全局、用户和任务选项）

</details>

<details>
  <summary><h5>状态</h5></summary>

- 下载/上传/提取/压缩/做种/克隆状态
- 无限数量任务的状态页面，在一条消息中查看特定数量的任务（全局选项）
- 消息更新间隔（全局选项）
- 下一页/上一页按钮获取不同页面（全局和用户选项）
- 如果任务数量超过 30 个，则根据传输类型获取特定任务状态的状态按钮（全局和用户选项）
- 步进按钮，用于下一页/上一页按钮应该后退/前进多少步（全局和用户选项）
- 每个用户的状态（无自动刷新）

</details>

<details>
  <summary><h5>Yt-dlp</h5></summary>

- Yt-dlp 质量按钮（任务选项）
- 能够使用特定的 yt-dlp 选项（全局、用户和任务选项）
- Netrc 支持（全局选项）
- Cookies 支持（全局选项）
- 嵌入原始缩略图并为下载添加缩略图
- 所有支持的音频格式

</details>

<details>
  <summary><h5>JDownloader</h5></summary>

- 同步设置（全局选项）
- 等待选择（在下载开始前启用/禁用文件或更改变体）
- DLC 文件支持
- 所有设置都可以通过远程访问 JDownloader 的 Web 界面、Android 应用、iPhone 应用或浏览器扩展进行编辑

</details>

<details>
  <summary><h5>Mongo 数据库</h5></summary>

- 存储机器人设置
- 存储用户设置，包括缩略图和所有私人文件
- 存储 RSS 数据
- 存储未完成的任务消息
- 存储 JDownloader 设置
- 在首次构建时存储 config.py 文件，如果其发生任何变化，则在下一次构建时将从 config.py 定义变量，而不是从数据库定义

</details>

<details>
  <summary><h5>种子搜索</h5></summary>

- 使用种子搜索 API 搜索种子
- 使用 qBittorrent 搜索引擎的变量插件搜索种子

</details>

<details>
  <summary><h5>压缩文件</h5></summary>

- 提取带有或不带密码的分割文件
- 在下载的情况下，使用或不使用密码压缩文件/文件夹，并进行分割
- 使用 7z 包通过或不通过密码提取所有支持的类型

</details>

<details>
  <summary><h5>RSS</h5></summary>

- 基于此存储库 [rss-chan](https://github.com/hyPnOtICDo0g/rss-chan)
- RSS 源（用户选项）
- 标题过滤器（源选项）
- 在运行时编辑任何源：暂停、恢复、编辑命令和编辑过滤器（源选项）
- Sudo 设置以控制用户源
- 所有功能都已通过一个命令中的按钮得到改进。

</details>

<details>
  <summary><h5>Alist 文件管理系统</h5></summary>

- 集成了 Alist 文件管理系统，可以通过 Web 界面轻松管理和访问您的云端文件
- 支持多种云存储服务，包括 Google Drive、OneDrive、阿里云盘等
- 提供文件预览、分享、移动、重命名等功能
- 直观的文件管理界面，支持拖放操作
- 强大的搜索功能，快速找到所需文件
- 多用户管理系统
- 详细的文件操作日志
- 支持 WebDAV 协议访问

</details>

<details>
  <summary><h5>总体功能</h5></summary>

- Docker 镜像支持 Linux `amd64, arm64/v8, arm/v7`
- 在机器人运行时编辑变量并覆盖私人文件（机器人、用户设置）
- 使用 `UPSTREAM_REPO` 在启动时和重启命令时更新机器人
- Telegraph。基于 [Sreeraj](https://github.com/SVR666) 的 loaderX-bot
- 通过回复进行镜像/下载/观看/克隆/计数/删除
- 使用一个命令镜像/下载/克隆多个链接/文件
- 除种子外的所有链接的自定义名称。对于文件，您应该添加扩展名，yt-dlp 链接除外（全局和用户选项）
- 排除具有特定扩展名的文件，使其不被上传/克隆（全局和用户选项）
- 查看链接按钮。额外的按钮，用于在浏览器中打开索引链接，而不是直接下载文件
- 所有任务的队列系统（全局选项）
- 能够在同一目录中压缩/解压缩多个链接。主要有助于解压缩 TG 文件部分（任务选项）
- 从 Telegram txt 文件或包含按新行分隔的链接的文本消息批量下载（任务选项）
- 连接之前由 split（Linux 包）分割的文件（任务选项）
- 样本视频生成器（任务选项）
- 截图生成器（任务选项）
- 能够取消上传/克隆/压缩/提取/分割/队列（任务选项）
- 取消所有按钮，用于选择特定任务状态以取消（全局选项）
- 使用过滤器将视频和音频转换为特定格式（任务选项）
- 一旦添加下载，就可以使用命令或参数强制从队列开始上传或下载或两者（任务选项）
- Shell 和 Executor
- 添加 sudo 用户
- 能够保存上传路径
- 名称替换，用于在上传前重命名文件
- 用户可以选择是否使用其 rclone.conf/token.pickle，而无需在路径/gd-id 前添加 mpt: 或 mrcc:
- FFmpeg 命令，在下载后执行（任务选项）
- 支持的直接链接生成器：

> mediafire（文件/文件夹），hxfile.co（需要带名称的 cookies txt）[hxfile.txt]，streamtape.com，streamsb.net，streamhub.ink，streamvid.net，doodstream.com，feurl.com，upload.ee，pixeldrain.com，racaty.net，1fichier.com，1drv.ms（仅适用于文件，不适用于文件夹或商业帐户），filelions.com，streamwish.com，send.cm（文件/文件夹），solidfiles.com，linkbox.to（文件/文件夹），shrdsk.me（sharedisk.io），akmfiles.com，wetransfer.com，pcloud.link，gofile.io（文件/文件夹），easyupload.io，mdisk.me（使用 ytdl），tmpsend.com，qiwi.gg，berkasdrive.com，mp4upload.com，terabox.com（仅视频文件/文件夹）。

</details>
</details>

<details>
  <summary><h1>如何部署？</h1></summary>

<details>
  <summary><h2>前提条件</h2></summary>

<details>
  <summary><h5>1. 安装要求</h5></summary>

- 克隆此仓库：

```bash
git clone https://github.com/anasty17/mirror-leech-telegram-bot mirrorbot/ && cd mirrorbot
```

- 对于基于 Debian 的发行版

```bash
sudo apt install python3 python3-pip
```

按照[官方 Docker 文档](https://docs.docker.com/engine/install/debian/)安装 Docker

- 对于 Arch 及其衍生版：

```bash
sudo pacman -S docker python
```

- 安装运行设置脚本的依赖项：

```bash
pip3 install -r requirements-cli.txt
```

------

</details>

<details>
  <summary><h5>2. 设置配置文件</h5></summary>

```bash
cp config_sample.py config.py
```

填写剩余的字段。每个字段的含义在下面讨论。

**1. 必填字段**

- `BOT_TOKEN` (`Str`): 从 [@BotFather](https://t.me/BotFather) 获取的 Telegram 机器人令牌。
- `OWNER_ID` (`Int`): 机器人所有者的 Telegram 用户 ID（非用户名）。
- `TELEGRAM_API` (`Int`): 用于验证您的 Telegram 帐户以下载 Telegram 文件。您可以从 <https://my.telegram.org> 获取此信息。
- `TELEGRAM_HASH` (`Str`): 用于验证您的 Telegram 帐户以下载 Telegram 文件。您可以从 <https://my.telegram.org> 获取此信息。

**2. 可选字段**
见配置文件中的详细中文注释。

</details>
</details>

<details>
  <summary><h2>构建和运行</h2></summary>

确保您仍然挂载存储库文件夹，并已从官方文档安装了 Docker。

- 有两种方法可以构建和运行 Docker：
    1. 使用官方 Docker 命令。
    2. 使用 Docker Compose 插件。（推荐）

------

<details>
  <summary><h3>使用官方 Docker 命令</h3></summary>

- 构建 Docker 镜像：

```bash
sudo docker build . -t mltb
```

- 运行镜像：

```bash
sudo docker run --network host mltb
```

- 停止运行的镜像：

```bash
sudo docker ps
```

```bash
sudo docker stop id
```

----

</details>

<details>
  <summary><h3>使用 Docker Compose 插件</h3></summary>

- 安装 Docker Compose 插件

```bash
sudo apt install docker-compose-plugin
```

- 构建并运行 Docker 镜像：

```bash
sudo docker compose up
```

- 编辑文件后，例如（nano start.sh）或 git pull 后，必须使用 --build 来编辑容器文件：

```bash
sudo docker compose up --build
```

- 停止运行的容器：

```bash
sudo docker compose stop
```

- 运行容器：

```bash
sudo docker compose start
```

- 从已运行的容器获取日志（挂载文件夹后）：

```bash
sudo docker compose logs --follow
```

------

</details>

**重要注意事项**:
1. 刷新机器的 iptables 以使用主机网络中的已打开端口与 Docker 一起使用。

```bash
# 刷新所有规则（重置 iptables）
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
sudo iptables -t mangle -F
sudo iptables -t mangle -X

sudo ip6tables -F
sudo ip6tables -X
sudo ip6tables -t nat -F
sudo ip6tables -t nat -X
sudo ip6tables -t mangle -F
sudo ip6tables -t mangle -X

# 设置默认策略
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT

sudo ip6tables -P INPUT ACCEPT
sudo ip6tables -P FORWARD ACCEPT
sudo ip6tables -P OUTPUT ACCEPT

# 保存
sudo iptables-save | sudo tee /etc/iptables/rules.v4
sudo ip6tables-save | sudo tee /etc/iptables/rules.v6
```

2. 将 `BASE_URL_PORT` 和 `RCLONE_SERVE_PORT` 变量设置为您想要使用的任何端口。默认分别为 `80` 和 `8080`。

3. 使用 `nproc` 命令检查机器的处理单元数量，然后乘以 4，然后在 qBittorrent.conf 中编辑 `AsyncIOThreadsCount`，或者在机器人工作时从 bsetting->qbittorrent 设置。

------

</details>
</details>

<details>
  <summary><h1>其他信息</h1></summary>

<details>
  <summary><h5>在 <a href="https://t.me/BotFather">@BotFather</a> 中设置机器人命令</h5></summary>

```
mirror - 或 /m 镜像文件
qbmirror - 或 /qm 使用 qBittorrent 镜像种子
jdmirror - 或 /jm 使用 jdownloader 镜像
nzbmirror - 或 /nm 使用 sabnzbd 镜像
ytdl - 或 /y 镜像 yt-dlp 支持的链接
leech - 或 /l 上传到 Telegram
qbleech - 或 /ql 使用 qBittorrent 下载种子
jdleech - 或 /jl 使用 jdownloader 下载
nzbleech - 或 /nl 使用 sabnzbd 下载
ytdlleech - 或 /yl 下载 yt-dlp 支持的链接
clone - 复制文件/文件夹到 Drive
count - 计算 GDrive 中的文件/文件夹
usetting - 或 /us 用户设置
bsetting - 或 /bs 机器人设置
status - 获取镜像状态消息
sel - 从种子中选择文件
rss - RSS 菜单
list - 在 Drive 中搜索文件
search - 使用 API 搜索种子
cancel - 或 /c 取消任务
cancelall - 取消所有任务
forcestart - 或 /fs 从队列开始任务
del - 从 GDrive 删除文件/文件夹
log - 获取机器人日志
auth - 授权用户或聊天
unauth - 取消授权用户或聊天
shell - 在 Shell 中运行命令
aexec - 执行异步函数
exec - 执行同步函数
restart - 重启机器人
restartses - 重启 Telegram 会话
stats - 机器人使用统计
ping - Ping 机器人
help - 所有带有描述的命令
```

------

</details>

<details>
  <summary><h5>获取 Google OAuth API 凭据文件和 token.pickle</h5></summary>

**注意**

- 旧的认证方式已更改，现在我们不能使用机器人或 replit 生成 token.pickle。您需要具有本地浏览器的操作系统。例如 `Termux`。
- Windows 用户应该安装 python3 和 pip。您可以从谷歌或从 [Wiszky](https://github.com/vishnoe115) 的[这个教程](https://telegra.ph/Create-Telegram-Mirror-Leech-Bot-by-Deploying-App-with-Heroku-Branch-using-Github-Workflow-12-06)中找到如何安装和使用它们。
- 您只能在本地浏览器中打开从 `generate_drive_token.py` 生成的链接。

1. 访问 [Google Cloud Console](https://console.developers.google.com/apis/credentials)
2. 转到 OAuth Consent 选项卡，填写并保存。
3. 转到凭据选项卡，点击创建凭据 -> OAuth Client ID
4. 选择桌面并创建。
5. 发布您的 OAuth consent screen 应用程序，以防止 **token.pickle** 过期
6. 使用下载按钮下载您的凭据。
7. 将该文件移动到镜像机器人的根目录，并重命名为 **credentials.json**
8. 访问 [Google API 页面](https://console.developers.google.com/apis/library)
9. 搜索 Google Drive Api 并启用它
10. 最后，运行脚本生成 Google Drive 的 **token.pickle** 文件：

```bash
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 generate_drive_token.py
```

------

</details>

<details>
  <summary><h5>生成 rclone.conf</h5></summary>

1. 从[官方网站](https://rclone.org/install/)安装 rclone
2. 使用 `rclone config` 命令创建新的远程
3. 将 rclone.conf 从 .config/rclone/rclone.conf 复制到存储库文件夹

------

</details>

<details>
  <summary><h5>上传</h5></summary>

- `RCLONE_PATH` 类似于 `GDRIVE_ID`，是镜像的默认路径。除了这些变量外，还有 `DEFAULT_UPLOAD` 来选择默认工具，无论是 rclone 还是 google-api-python-client。
- 如果 `DEFAULT_UPLOAD` = 'rc'，则必须用路径填充 `RCLONE_PATH` 作为默认路径，或者用 `rcl` 在每个新任务上选择目标路径。
- 如果 `DEFAULT_UPLOAD` = 'gd'，则必须用文件夹/TD id 填充 `GDRIVE_ID`。
- rclone.conf 可以在部署前添加，如 token.pickle 到存储库文件夹根目录，或者使用 bsetting 上传为私人文件。
- 如果 rclone.conf 从 usetting 上传或添加到 `rclone/{user_id}.conf`，则 `RCLONE_PATH` 必须以 `mrcc:` 开头。
- 所以简而言之，up: 有 4 个可能的值，分别是：gd(上传到 GDRIVE_ID)，rc(上传到 RCLONE_PATH)，rcl(选择 Rclone 路径)和 rclone_path(remote:path(所有者 rclone.conf) 或 mrcc:remote:path(用户 rclone.conf))

------

</details>

<details>
  <summary><h5>UPSTREAM REPO（推荐）</h5></summary>

- `UPSTREAM_REPO` 变量可用于编辑/添加存储库中的任何文件。
- 您可以添加私人/公共存储库链接以获取/覆盖所有文件。
- 您可以跳过在部署前添加私人文件，如 token.pickle 或帐户文件夹，只需填写私人 `UPSTREAM_REPO` 以获取所有文件，包括私人文件。
- 如果您在部署时添加了私人文件，并且您添加了私人 `UPSTREAM_REPO` 和此私人存储库中的私人文件，则您的私人文件将从此存储库中被覆盖。此外，如果您使用数据库存储私人文件，则数据库中的所有文件将覆盖在部署前或从私人 `UPSTREAM_REPO` 添加的私人文件。
- 如果您使用官方存储库链接填充了 `UPSTREAM_REPO`，那么要小心，如果 requirements.txt 有任何变化，您的机器人将在重启后无法启动。在这种情况下，您需要使用更新的代码重新部署以安装新的要求，或者只需将 `UPSTREAM_REPO` 更改为您的 fork 链接并带有旧的更新。
- 如果您用您的 fork 链接填充了 `UPSTREAM_REPO`，如果您从官方存储库获取了提交，也要小心。
- 您的 `UPSTREAM_REPO` 中的更改只有在重启后才会生效。

------

</details>

<details>
  <summary><h5>比特种子种子</h5></summary>

- 单独使用 `-d` 参数将导致使用 aria2c 或 qbittorrent 的全局选项。

<details>
  <summary><h3>QBittorrent</h3></summary>

- 全局选项：qbittorrent.conf 中的 `GlobalMaxRatio` 和 `GlobalMaxSeedingMinutes`，`-1` 表示无限制，但您可以手动取消。
    - **注意**：不要更改 `MaxRatioAction`。

</details>

<details>
  <summary><h3>Aria2c</h3></summary>

- 全局选项：aria.sh 中的 `--seed-ratio`（0 表示无限制）和 `--seed-time`（0 表示不种子）。

------

</details>
</details>

<details>
  <summary><h5>使用服务帐户上传以避免用户速率限制</h5></summary>

> 要使服务帐户工作，您必须在配置文件或环境变量中设置 `USE_SERVICE_ACCOUNTS` = "True"。
> **注意**：仅在上传到 Team Drive 时才建议使用服务帐户。

<details>
  <summary><h3>1. 生成服务帐户。<a href="https://cloud.google.com/iam/docs/service-accounts">什么是服务帐户？</a></h3></summary>
让我们只创建我们需要的服务帐户。

**警告**：滥用此功能不是本项目的目的，我们**不**建议您创建大量项目，只需一个项目和 100 个 SA 就足够使用，过度滥用也可能导致您的项目被谷歌封禁。

> **注意**：如果您之前已经从此脚本创建了 SA，您也可以通过运行以下命令重新下载密钥：

```bash
python3 gen_sa_accounts.py --download-keys $PROJECTID
```

> **注意：** 1 个服务帐户每天可以上传/复制大约 750 GB，1 个项目可以创建 100 个服务帐户，所以您每天可以上传 75 TB。

> **注意：** 所有人每天可以从每个文件创建者（上传者帐户）复制 `2TB/天`，所以如果您收到错误 `userRateLimitExceeded`，这并不意味着您的限制已超过，而是文件创建者的限制已超过，即 `2TB/天`。

#### 创建服务帐户的两种方法

选择以下方法之一

<details>
  <summary><h5>1. 在现有项目中创建服务帐户（推荐方法）</h5></summary>

- 列出您的项目 ID

```bash
python3 gen_sa_accounts.py --list-projects
```

- 通过此命令自动启用服务

```bash
python3 gen_sa_accounts.py --enable-services $PROJECTID
```

- 创建当前项目的服务帐户

```bash
python3 gen_sa_accounts.py --create-sas $PROJECTID
```

- 将服务帐户下载为 accounts 文件夹

```bash
python3 gen_sa_accounts.py --download-keys $PROJECTID
```

</details>

<details>
  <summary><h5>2. 在新项目中创建服务帐户</h5></summary>

```bash
python3 gen_sa_accounts.py --quick-setup 1 --new-only
```

将创建一个名为 accounts 的文件夹，其中包含服务帐户的密钥。

</details>
</details>

<details>
  <summary><h3>2. 添加服务帐户</h3></summary>

#### 添加服务帐户的两种方法

选择以下方法之一

<details>
  <summary><h5>1. 将它们添加到 Google 群组，然后添加到 Team Drive（推荐）</h5></summary>

- 挂载 accounts 文件夹

```bash
cd accounts
```

- 从所有帐户中获取电子邮件到将在 accounts 文件夹中创建的 emails.txt 文件
- `对于使用 PowerShell 的 Windows`

```powershell
$emails = Get-ChildItem .\**.json |Get-Content -Raw |ConvertFrom-Json |Select -ExpandProperty client_email >>emails.txt
```

- `对于 Linux`

```bash
grep -oPh '"client_email": "\K[^"]+' *.json > emails.txt
```

- 卸载 acounts 文件夹

```bash
cd ..
```

然后将 emails.txt 中的电子邮件添加到 Google 群组，之后将此 Google 群组添加到您的共享驱动器并将其提升为管理员，然后从 accounts 文件夹中删除 email.txt 文件

</details>

<details>
  <summary><h5>2. 直接将它们添加到 Team Drive</h5></summary>

- 运行：

```bash
python3 add_to_team_drive.py -d SharedTeamDriveSrcID
```

------

</details>
</details>
</details>

<details>
  <summary><h5>创建数据库</h5></summary>

1. 前往 `https://mongodb.com/` 并注册。
2. 创建共享集群。
3. 在 `Deployment` 标题下按 `Database`，您创建的集群将在那里。
5. 按连接，选择 `Allow Access From Anywhere` 并在不编辑 IP 的情况下按 `Add IP Address`，然后创建用户。
6. 创建用户后，按 `Choose a connection`，然后按 `Connect your application`。选择 `Driver` **python** 和 `version` **3.12 or later**。
7. 复制您的 `connection string` 并将 `<password>` 替换为您用户的密码，然后按关闭。

------

</details>

<details>
  <summary><h5>多 Drive 列表</h5></summary>

要使用来自多个 TD/文件夹的列表。在您的终端中运行 driveid.py 并按照它进行操作。它将生成 **list_drives.txt** 文件，或者您可以简单地在工作目录中创建 `list_drives.txt` 文件并填写它，检查以下格式：

```
DriveName folderID/tdID or `root` IndexLink(if available)
DriveName folderID/tdID or `root` IndexLink(if available)
```

示例：

```
TD1 root https://example.dev
TD2 0AO1JDB1t3i5jUk9PVA https://example.dev
```

-----

</details>

<details>
  <summary><h5>使用 .netrc 文件进行 Yt-dlp 和 Aria2c 认证</h5></summary>

要在 yt-dlp 中使用您的高级帐户或用于受保护的索引链接，请根据以下格式创建 .netrc 文件：

**注意**：创建 .netrc 而不是 netrc，此文件将被隐藏，因此在创建后查看隐藏文件以进行编辑。

格式：

```
machine host login username password my_password
```

使用 Aria2c，您也可以使用机器人内置功能，带或不带用户名。这里是没有用户名的索引链接示例。

```
machine example.workers.dev password index_password
```
其中主机是提取器的名称（例如 instagram、Twitch）。不同主机的多个帐户可以添加，每个由一个新行分隔。

**Yt-dlp**: 
使用 [cookies.txt](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies) 文件进行认证。在隐身标签中创建它。


-----

</details>

<details>
  <summary><h5>Alist 文件管理系统使用说明</h5></summary>

Alist 是一个强大的文件列表程序，支持多种存储，提供 WebDAV、API 等功能，同时拥有在线预览和编辑等功能。

**特点**:
- 支持多种存储服务，包括本地存储、阿里云盘、OneDrive、Google Drive 等
- 文件在线预览功能，支持图片、视频、音频、文本和多种文档格式
- WebDAV 支持，可以挂载到本地系统
- 受保护的路径和文件/文件夹密码功能
- 文件永久链接和分享功能
- 元数据支持，包括自定义头图、readme 和描述
- 多用户系统和权限控制

**初始配置**:
1. 默认访问地址：`http://你的IP:5244`
2. 默认用户名：`admin`
3. 默认密码：首次启动时随机生成，可以通过查看日志获取：
   ```
   docker logs mirrorbot | grep "初始管理员信息"
   ```

**添加存储**:
1. 登录后，进入"管理" → "存储"
2. 点击"添加"按钮
3. 选择存储类型，填写相应配置
4. 测试连接成功后保存

**配置 WebDAV**:
1. 进入"管理" → "设置" → "WebDAV"
2. 配置 WebDAV 路径和权限

**文件操作**:
- 上传、下载、移动、复制、重命名文件
- 创建文件夹、删除文件或文件夹
- 在线预览和编辑文本文件
- 视频在线播放和音频在线听

**注意事项**:
- 首次登录后请立即修改默认密码
- 重要数据请定期备份

有关更多详细信息，请参考 [Alist 官方文档](https://alist.nn.ci/)。

-----

</details>
</details>


# 感谢所有贡献者

<a href="https://github.com/anasty17/mirror-leech-telegram-bot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=anasty17/mirror-leech-telegram-bot" />
</a>

# 捐赠

<p>如果您觉得这个项目有用并想表示感谢，不妨请我喝杯咖啡。</p>

[!["Buy Me A Coffee"](https://storage.ko-fi.com/cdn/kofi2.png)](https://ko-fi.com/anasty17)

Binance ID:

```
52187862
```

USDT 地址:

```
TEzjjfkxLKQqndpsdpkA7jgiX7QQCL5p4f
```

网络:

```
TRC20
```
TRX 地址:

```
TEzjjfkxLKQqndpsdpkA7jgiX7QQCL5p4f
```

网络:

```
TRC20
```

BTC 地址:

```
17dkvxjqdc3yiaTs6dpjUB1TjV3tD7ScWe
```

ETH 地址:

```
0xf798a8a1c72d593e16d8f3bb619ebd1a093c7309
```

-----