"""Real-browser reading checks. Run against a built preview, not the dev server."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = os.environ.get('BOOK_PREVIEW_URL', 'http://127.0.0.1:4322/LLMs-for-Backend-Engineers').rstrip('/')
OUTPUT = Path(__file__).resolve().parents[1] / 'review'
OUTPUT.mkdir(exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width':1440, 'height':1000})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: errors.append(f'{response.status}: {response.url}') if response.status >= 400 and response.url.startswith(BASE) else None)
    page.goto(BASE + '/zh-Hans/', wait_until='networkidle')
    page.keyboard.press('Tab')
    assert page.locator(':focus').get_attribute('href') == '#main'
    assert page.locator('.hero-reading-note').is_visible()
    assert page.locator('.hero-reading-note a[href="#contents"]').count() == 1
    page.screenshot(path=str(OUTPUT / 'home-desktop.png'))
    page.goto(BASE + '/zh-Hans/read/from-onehot-to-embedding/', wait_until='networkidle')
    assert page.locator('.katex').count() > 0
    page.screenshot(path=str(OUTPUT / 'reader-desktop.png'))
    before = page.locator('#article').evaluate('(e)=>getComputedStyle(e).fontSize')
    page.locator('#larger').click()
    assert before != page.locator('#article').evaluate('(e)=>getComputedStyle(e).fontSize')
    original_theme = page.locator('html').get_attribute('data-theme')
    page.locator('#theme').click()
    page.reload(wait_until='networkidle')
    assert original_theme != page.locator('html').get_attribute('data-theme')
    page.screenshot(path=str(OUTPUT / 'reader-dark.png'))
    page.locator('#focus').click()
    assert page.locator('body').evaluate('(e)=>e.classList.contains("focused")')
    page.locator('#focus').click()
    section = page.locator('#article h2').nth(1)
    section_scroll = section.evaluate('(e) => scrollY + e.getBoundingClientRect().top - 180')
    page.evaluate('(y) => { document.documentElement.style.scrollBehavior = "auto"; scrollTo(0, y); dispatchEvent(new Event("scroll")) }', section_scroll)
    page.wait_for_timeout(400)
    saved_position = page.evaluate('JSON.parse(localStorage.getItem("llms-position:zh-Hans:from-onehot-to-embedding"))')
    saved_heading = page.locator(f'#article [id="{saved_position["section"]}"]')
    assert saved_position['version'] == 2 and saved_heading.count() == 1, saved_position
    page.reload(wait_until='networkidle')
    assert page.locator('#resume').is_visible()
    assert saved_heading.inner_text() in page.locator('#resume-label').inner_text()
    page.locator('#resume-button').click()
    page.wait_for_timeout(1200)
    assert abs(saved_heading.bounding_box()['y'] - 85) < 150
    # Select actual text to exercise quote anchoring and cross-reload persistence.
    quote = page.locator('#article p').first.inner_text()
    page.locator('#article p').first.evaluate('e=>{const r=document.createRange();r.selectNodeContents(e);getSelection().removeAllRanges();getSelection().addRange(r)}')
    page.locator('#notes-open').click()
    page.locator('#note-text').fill('Smoke test: review this explanation.')
    page.locator('#save-note').click()
    assert 'Smoke test:' in page.locator('#notes-list').inner_text()
    with page.expect_download() as download:
        page.locator('#export-notes').click()
    backup = Path(download.value.path()).read_text()
    assert 'Smoke test:' in backup
    assert page.evaluate('CSS.highlights.get("book-notes").size') == 1
    page.locator('#notes-dialog [data-close]').click()
    page.reload(wait_until='networkidle')
    page.locator('#notes-open').click()
    assert 'Smoke test:' in page.locator('#notes-list').inner_text()
    page.locator('#notes-dialog [data-close]').click()
    assert page.evaluate('CSS.highlights.get("book-notes").size') == 1
    page.locator('#search-open').click()
    page.locator('.pagefind-ui__search-input').fill('梯度消失')
    page.locator('.pagefind-ui__result').first.wait_for(timeout=15000)
    page.locator('#search-dialog [data-close]').click()
    page.goto(BASE + '/chapters/part1-math-foundations/softmax.html#从分数到概率：四步走', wait_until='networkidle')
    page.wait_for_url('**/zh-Hans/read/softmax/**')
    assert page.locator('[id="从分数到概率：四步走"]').count() == 1
    page.goto(BASE + '/chapters/part2-llm-internal/attention-mechanism.html', wait_until='networkidle')
    page.wait_for_url('**/zh-Hans/read/transformer-architecture/**')
    assert page.locator('.chapter-heading h1').inner_text() == 'Transformer 架构：从数据流理解'
    page.goto(BASE + '/en/read/from-onehot-to-embedding/', wait_until='networkidle')
    assert page.locator('html').get_attribute('lang') == 'en'
    assert page.locator('.translation-notice').is_visible()
    page.locator('#notes-open').click()
    assert 'Smoke test:' not in page.locator('#notes-list').inner_text()
    page.locator('#notes-dialog [data-close]').click()
    page.locator('#search-open').click()
    page.locator('.pagefind-ui__search-input').fill('gradient')
    page.locator('.pagefind-ui__result').first.wait_for(timeout=15000)
    assert all('/en/read/' in href for href in page.locator('.pagefind-ui__result-link').evaluate_all('(els)=>els.map(e=>e.href)'))
    mobile = browser.new_page(viewport={'width':390, 'height':844})
    for name, route in [('home-mobile','/zh-Hans/'), ('reader-mobile','/zh-Hans/read/from-onehot-to-embedding/')]:
        mobile.goto(BASE + route, wait_until='networkidle')
        mobile.screenshot(path=str(OUTPUT / (name + '.png')))
        assert not mobile.evaluate('document.documentElement.scrollWidth>innerWidth')
    assert not mobile.locator('#book-navigation').evaluate('(e)=>e.open')
    # Basic reader navigation remains usable without JavaScript.
    plain = browser.new_page(java_script_enabled=False, viewport={'width':390,'height':844})
    plain.goto(BASE + '/zh-Hans/read/softmax/')
    assert plain.locator('#article').inner_text()
    assert plain.locator('.pager a').count() > 0
    assert not errors, errors
    browser.close()
print('Browser checks passed: keyboard entry, editorial home, math, fonts, theme, focus, section resume, notes/backup, edition isolation, bilingual search, legacy anchors, mobile, no-JS reading.')
