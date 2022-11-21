我使用 [Obsidian](https://obsidian.md/) 作为我的本地 MarkDown 编辑器，使用 Hexo 作为个人博客。
受 **yukang**  [文章](https://catcoding.me/p/publish-to-wechat/) 启发，写了一个 Python 脚本 [obsidian_to_hexoblog](https://github.com/DeppWang/obsidian_to_hexoblog)，在 Obsidian 写好一篇文章后只需打上一个指定标签 `Obsidian-to-HexoBlog-Tag` ，并将文章英文名设置为第一个标签。Obsidian 私有仓库 GitHub Action 自动运行脚本将 Obsidian 指定指定标签文章同步到 HexoBlog 私有仓库指定文件夹，再触发 [HexoBlog Action](https://depp.wang/2020/02/17/use-github-actions-to-achieve-hexo-blog-auto-deploy/) 完成发布

Obsidian 私有仓库 GitHub Action：

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/20221120125228.png)

<!--more-->

两个小技巧

1. 因为 GitHub 的 Free 账户 Action 每月只有 2000min，我使用 Obsidian Git 插件，每 2 分钟同步一次，如果每次都触发，那 Action 应该不够用，所以我设置了只有手动 commit 时才触发 Action

   ![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/20221121225431.png)
![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/20221121225524.png)

2. 在 Obsidian 设置标签时不要太常用，我原来标签为 `HexoBlog`，就误将包含 `Personal access token` 草稿发出，吓我一大跳
