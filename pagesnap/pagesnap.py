import argparse
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page
import base64

resources = {}

async def handle_response(response):
    if response and response.ok:
        print(f'请求成功 {response.url=}')
        content_type = response.headers.get('content-type')
        if content_type == None:
            return

        if content_type and ('image' in content_type):
            print('资源类型为图片')
            url = response.url
            data = await response.body()
            resources[url] = {
                'content_type': content_type,
                'data': data
            }

        if 'text/css' in content_type:
            print('资源类型为css')
            url = response.url
            data = await response.text()
            resources[url] = {
                'content_type': content_type,
                'data': data
            }

def resources_contains(part_of_url: str) -> str|None:
    for url in resources.keys():
        if part_of_url in url:
            return url
    return None

async def hook_page(page: Page):
    """Hook page to intercept requests and save resources"""
    page.on('response', handle_response)

async def page_snap(page: Page) -> str:
    """Scrape page and embed resources"""
    content = await page.content()

    print(len(resources))

    # embed images
    for img in await page.query_selector_all('img[src]'):
        src = await img.get_attribute('src')

        if not src:
            continue

        if src.startswith('data:'):
            continue

        print('===============')
        print(f'fetching {src}')

        full_src =  resources_contains(src)
        if full_src:
            print('资源命中缓存')
            content = content.replace(src, embed_resource(resources[full_src]['content_type'], resources[full_src]['data']))
        else:
            print('资源未命中，单独发起请求')
            try:
                # response = await page.evaluate('(src) => fetch(src).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', src)
                response = await page.evaluate_handle('(src) => fetch(src).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', src)   
                await response.dispose()
            except Exception as e:
                print(f'failed to fetch {src}')
                print(e)
    
    # embed css
    for link in await page.query_selector_all('link[rel="stylesheet"]'):
        href = await link.get_attribute('href')

        if not href:
            continue

        print('===============')
        print(f'fetching {href}')

        full_href = resources_contains(href)
        if full_href:
            print('资源命中缓存')
            continue

        print('资源未命中，单独发起请求')
        try:
            # response = await page.evaluate('(src) => fetch(src).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', src)
            response = await page.evaluate_handle('(src) => fetch(src).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', href)
            await response.dispose()
        except:
            print(f'failed to fetch {href}')
        # response = await page.evaluate('(href) => fetch(href).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', href)

    for link in await page.query_selector_all('link[as="style"]'):
        href = await link.get_attribute('href')

        if not href:
            continue

        print('===============')
        print(f'fetching link[as="style"] {href}')

        full_href = resources_contains(href)
        if full_href:
            print('资源命中缓存')
            continue

        print('资源未命中，单独发起请求')
        try:
            # response = await page.evaluate('(src) => fetch(src).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', src)
            response = await page.evaluate_handle('(src) => fetch(src).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', href)
            await response.dispose()
        except:
            print(f'failed to fetch {href}')
        # response = await page.evaluate('(href) => fetch(href).then(r => r.arrayBuffer()).then(r => btoa(String.fromCharCode(...new Uint8Array(r))))', href)
    
    # Load the HTML with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Replace img tags with base64 embedded images
    for img in soup.find_all("img", src=True):
        src = resources_contains(img["src"])
        if src:
            resource = resources[src]
            content_type = resource["content_type"]
            data = resource["data"]
            embedded_data = embed_resource(content_type, data)
            img["src"] = embedded_data

    def link_as_style_filter(tag):
        return tag.name == "link" and tag.has_attr("as") and tag["as"] == "style"
    
    # Replace link tags with inline styles using resources
    for link in soup.find_all(link_as_style_filter):
        print('命中 tags with inline styles using resources')
        href = resources_contains(link["href"])
        if href:
            resource = resources[href]
            content_type = resource["content_type"]
            data = resource["data"]
            style_tag = soup.new_tag("style", type="text/css")
            style_tag.string = data
            link.replace_with(style_tag)
    
    # Replace link tags (CSS) with inline styles
    for link in soup.find_all("link", rel="stylesheet", href=True):
        href = resources_contains(link["href"])
        if href:
            resource = resources[href]
            content_type = resource["content_type"]
            data = resource["data"]
            style_tag = soup.new_tag("style", type="text/css")
            style_tag.string = data
            link.replace_with(style_tag)
    
    # Remove all script tags
    scripts = soup.find_all("script")
    for script in scripts:
        script.decompose()
    
    def link_script_filter(tag):
        return tag.name == "link" and (tag.has_attr("as") and tag["as"] == "script") or (tag.has_attr('href') and tag['href'].endswith('.js'))
    
    # Remove the matching tags from the DOM
    for tag in soup.find_all(link_script_filter):
        tag.decompose()
    
    # Define a filter function for finding the desired tags
    def ssr_dns_prefetch_filter(tag):
        return tag.name == "link" and (tag.has_attr("data-n-head") and tag["data-n-head"] == "ssr") or (tag.has_attr("rel") and "dns-prefetch" in tag["rel"])

    # Find all tags matching the filter
    tags_to_remove = soup.find_all(ssr_dns_prefetch_filter)

    # Remove the matching tags from the DOM
    for tag in tags_to_remove:
        tag.decompose()

    # Get the modified HTML
    return soup.prettify()

async def save_as_single_file(url, output_filename):
    """Save the page as a single file."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

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

        await browser.close()

def embed_resource(content_type, data):
    """Embed the resource in the HTML page."""
    if type(data) == str:
        base64_data = data
    else:
        base64_data = base64.b64encode(data).decode('utf-8')
    return f'data:{content_type};base64,{base64_data}'

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Save a webpage as a single file.')
    parser.add_argument('url', help='URL of the webpage to save')
    parser.add_argument('output_filename', help='Output filename')
    args = parser.parse_args()
    asyncio.run(save_as_single_file(args.url, args.output_filename))

if __name__ == '__main__':
    main()

