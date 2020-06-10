import asyncio
from pyppeteer import launch

async def main():
    try:
        print('pyppeteer launch')
        browser = await launch()
        print('pyppeteer browser.newPage()')
        page = await browser.newPage()
        await page.goto('https://baidu.com')
        await browser.close()
        print('pyppeteer browser.close()')
    except Exception as ex:
        print("pyppeteer Error")
        print(ex)
    finally:
        print("pyppeteer main() Done")
    

loop = asyncio.get_event_loop_policy().new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.close()

print('Get Chrome Done.')