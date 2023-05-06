# PageSnap

[中文文档](./README_zh.md)

PageSnap is a tool that allows you to save web pages offline as single-page HTML files, preserving the original appearance of the web page as much as possible. It is developed using Python and Playwright, which means it can also save dynamic JavaScript web pages offline.

The advantage of using single-page HTML format is that users can conveniently open and browse the files with any W3C-compliant browser.

As a Python library, PageSnap can be easily added as a dependency to other projects. If your project uses Python and Playwright, simply import the PageSnap library to add offline-saving capabilities to your pages.

Note: Currently, this project is still in the early stages of feature development and cannot be directly used as a library. The related APIs are still under development. You can keep an eye on the progress, or feel free to clone the project to try it out and share your thoughts.

## As a Library

PageSnap provides an asyncio-based API. In your Playwright project, you can complete the offline saving of a page in just two steps. Here's an example code:

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

## As a Command Line

Use the following pip command to install:

```
pip install pagesnap
```

Initialize Playwright:

```
playwright install
```

Start using:

```
pagesnap https://example.com/ test.html
```

## Discussion

If you have any suggestions or improvements, please feel free to submit an issue or pull request. If you like this project, please give it a star.

I am usually active on [Sina Weibo](https://www.weibo.com/u/1240212845) and welcome technical discussions there as well.