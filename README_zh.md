# PageSnap

PageSnap 能将网页离线保存为单页 HTML，实现对网页的离线保存，能够最大程度还原网页原貌。使用 Python 基于 Playwright 开发，因此对于动态的 JavaScript 网页，也能够离线保存。

使用单页 HTML 格式的好处是，用户可以很方便地使用任何 W3C 浏览器打开并浏览。

作为一个 Python 库，可以作为依赖很容易地添加到其它项目中。如果您地项目使用 Python 和 Playwright，只需要引入 PageSnap 库，就能够对您的页面加入离线保存能力。

注意：目前该项目仍处于早期功能开发阶段，暂时还无法作为库直接引用，相关的 API 还在开发中。可以保持关注，也欢迎直接 clone 项目进行体验、交流。

## 作为库

PageSnap 提供基于 asyncio 的 API，在您的 playwright 工程中，只需要两步，即可完成对页面的离线保存，示例代码如下：


```python
# Step1: Hook page to intercept requests and save resources
#        note: you can also hook after goto, but you may miss some resources
await hook_page(page) 

# Develop your code, doing your actions
await page.goto(url)
# It's better to wait for the page to be fully loaded
await page.wait_for_load_state("networkidle")

# Step2: Get the page content
embedded_html = await page_snap(page)

# Then you can save it to a file
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(embedded_html)
```

## 作为命令行

使用 pip 安装命令：

```
pip install pagesnap
```

初始化 Playwright：

```
playwright install
```

开始使用：

```
pagesnap https://example.com/ test.html
```

## 讨论

如果有好的建议或者改进意见，欢迎提交 issue 或者 pr，如果喜欢这个项目，欢迎 star。

我通常活跃在[新浪微博](https://www.weibo.com/u/1240212845)，也欢迎在微博上一起交流技术~