from pathlib import Path
import re

NAV_TRANSLATIONS = [
    ('index.html', 'Home', 'الرئيسية'),
    ('products.html', 'Products', 'المنتجات'),
    ('about.html', 'About', 'حول'),
    ('contact.html', 'Contact', 'اتصل'),
]

translate_button_snippet = '''<button class="btn rounded-pill" id="translateBtn" style="font-size:.85rem;padding:.4rem .85rem;border-color:rgba(255,255,255,0.35)!important;color:var(--cream)!important;">
                    <i class="fas fa-language"></i>
                    <span id="translateBtnText">EN</span>
                </button>'''

inventory_files = [p for p in Path('.').glob('*.html')]

for path in inventory_files:
    text = path.read_text(encoding='utf-8')
    changed = False

    # Footer copyright year dynamic span
    new_text = re.sub(r'<p>&copy; 2024 Eco Life Store(?: Admin)?\. Made with 💚 for a better planet\.</p>',
                      lambda m: m.group(0).replace('&copy; 2024 ', '&copy; <span id="copyrightYear"></span> '),
                      text)
    if new_text != text:
        text = new_text
        changed = True

    # Copyright JS insertion into first inline script if needed
    if 'copyrightYear' not in text or '<span id="copyrightYear"></span>' in text and 'document.getElementById(' not in text:
        pass
    if '<span id="copyrightYear"></span>' in text and 'document.getElementById(' not in text:
        # insert script at first inline <script> tag
        m = re.search(r'<script(?![^>]*src)[^>]*>', text)
        if m:
            insert = m.end()
            text = text[:insert] + '\n    document.getElementById(\'copyrightYear\').textContent = new Date().getFullYear();\n' + text[insert:]
            changed = True

    # Add translation button after the cart button if missing
    if 'id="translateBtn"' not in text and "id='translateBtn'" not in text and 'href="cart.html"' in text:
        cart_pattern = re.compile(r'(<a[^>]*href="cart\.html"[^>]*>.*?</a>)(\s*)', re.S)
        new_text, count = cart_pattern.subn(lambda m: m.group(1) + '\n                ' + translate_button_snippet + '\n' + m.group(2), text, count=1)
        if count:
            text = new_text
            changed = True

    # Add data-en/data-ar to main nav links
    for href, en, ar in NAV_TRANSLATIONS:
        def repl(match, en=en, ar=ar):
            attrs = match.group(1)
            if 'data-en=' in attrs or 'data-ar=' in attrs:
                return match.group(0)
            return f'<a{attrs} data-en="{en}" data-ar="{ar}">{match.group(2)}</a>'
        # match anchors with optional icon inside
        pattern = re.compile(r'<a([^>]*href="' + re.escape(href) + r'"[^>]*)>(\s*(?:<i[^>]*></i>\s*)?' + re.escape(en) + r')(\s*)</a>')
        new_text, count = pattern.subn(repl, text)
        if count:
            text = new_text
            changed = True

    # Add translation script if missing
    if 'function translatePage' not in text:
        script_end = text.rfind('</script>')
        if script_end != -1:
            injection = r'''
        let currentLang = localStorage.getItem('siteLang') || 'en';
        function translatePage(lang) {
            document.querySelectorAll('[data-en][data-ar]').forEach(el => {
                if (!el.querySelector('*')) {
                    el.textContent = el.getAttribute('data-' + lang) || el.textContent;
                }
            });
            const btn = document.getElementById('translateBtnText');
            if (btn) btn.textContent = lang === 'en' ? 'AR' : 'EN';
            document.documentElement.lang = lang;
            document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
            localStorage.setItem('siteLang', lang);
            currentLang = lang;
        }
        const translateBtn = document.getElementById('translateBtn');
        if (translateBtn) {
            translateBtn.addEventListener('click', () => translatePage(currentLang === 'en' ? 'ar' : 'en'));
        }
        translatePage(currentLang);
'''
            text = text[:script_end] + injection + text[script_end:]
            changed = True

    # Fix footer placeholder href="#" links inside footer sections
    def fix_footer_block(match):
        block = match.group(0)
        block = re.sub(r'<a href="#"((?:(?!>).)*)>', lambda m: '<a href="#"' + m.group(1) + ' onclick="event.preventDefault(); alert(\'Coming soon!\');" title="Coming soon">' if 'onclick=' not in m.group(1) else m.group(0), block)
        return block
    new_text = re.sub(r'<footer[^>]*>.*?</footer>', fix_footer_block, text, flags=re.S)
    if new_text != text:
        text = new_text
        changed = True

    # Update social media links in footers
    social_links = [
        ('https://facebook.com', 'fa-facebook-f'),
        ('https://instagram.com', 'fa-instagram'),
        ('https://tiktok.com', 'fa-tiktok'),
        ('https://youtube.com', 'fa-youtube'),
    ]
    for url, icon_class in social_links:
        pattern = re.compile(r'<a href="#"[^>]*>(\s*<i[^>]*' + icon_class + r'[^>]*></i>\s*)</a>', re.I)
        replace = r'<a href="' + url + '" target="_blank" rel="noopener">\1</a>'
        text, count = pattern.subn(replace, text)
        if count:
            changed = True

    if changed:
        path.write_text(text, encoding='utf-8')
        print('Updated', path.name)
