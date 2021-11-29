---
title: hello world!
intro: 又名：我的第一篇blog。简单记录一下搭博客的经过。
author: Sapio-S
date: 2021-11-05
categories: [杂项]
tags: [踩坑, 碎碎念]
---
人到底会在《网络安全工程》课上做出什么啊。

大致的框架挺眼熟的，20年暑假给开源社区提交过blog就是这个格式，当时不太理解，现在看一眼就差不多明白了，进步了～

第一步自然是找模版，自己搭是不可能的，这辈子都不可能的，因为我懒。找了半天，好不容易锁定了一个还不错的样式`Flex`，兴高采烈就搬到自己的仓库里了，很快啊。无师自通装了个github action，美滋儿滋儿地自我陶醉了一下，换上头像，发个blog庆祝。

然而简单测试了一下其他的功能，发现这个排版……有一点点一言难尽。（虽然现在看起来也还可以…呃）

于是继续踏上寻找模版之旅。一个彩蛋：`persephone`模版的demo链接是作者的个人网站，里面有她写的小说。说起来这个模版还真不错，我为什么不用呢（突然陷入沉思）。

最终挑了半天决定用`chalk`，另外几个觉得还不错的包括`jekyllDecent`，`monochrome`，`simple-texture`，都是偏简约的设计。考虑到`chalk`的功能比较多，还支持视频播放，最终决定用它。
万万没想到`chalk`的水还挺深，我直接挖了个坑给自己跳。

##### github action不通过
仔细阅读了README，发现*Chalk does not support the standard way of Jekyll hosting on GitHub Pages*这句话，泪目。不死心的我试图在github actions中加入ruby，仍然直接用github跑，往里面一点点加命令，未果，在`npm run publish`的时候会报错，让我set github account。然后再次仔细阅读README，灵光一闪，意识到我应该在本地运行这一切。

##### windows装Ruby
别装，深坑。在这一步我把github的仓库迁移到了gitee上。私心觉得gitee确实挺好用的。

##### Mac装Homebrew
github的响应速度太慢，请使用以下命令：`/bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"`。

##### Mac build web pages
之后按照README的方式运行即可。血的教训：**先commit再deploy**！！发现改动没了，整个人都麻了。

##### trouble shooting (11.08 update)
在本机启动了另一份jekyll后ruby开始疯狂报错，用了stackoverflow上的各种方法都没用，几个gem的版本换了好几个也于事无补。切到windows上也是同样的问题，抓狂。终于，重新装了个2.7的ruby，好了。`brew reinstall ruby@2.7`

### 之后的改造计划
需要一个放个人简历的页面（暂定用about页面）。边距等等的设定也需要调整。希望有个侧边栏、有检索功能，并且有瀑布流式的portfolio展示页面。需要研究一下纯音频的播放和文件的下载。