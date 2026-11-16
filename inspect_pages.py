from pathlib import Path
from pathlib import Path
import os
os.chdir(r'd:\Capstone Project\Eco_Life_Store-main - Copy - Copy - Copy')
files=['account.html','cart.html','checkout.html','contact.html','login.html','product-detail.html','register.html','wishlist.html','admin.html']
for f in files:
    p = Path(f)
    print('---', f)
    if not p.exists():
        print('MISSING', f)
        continue
    txt = p.read_text(encoding='utf-8')
    has_nav = ('<div class="nav-actions"' in txt) or ('<div class="top-bar-actions"' in txt)
    print('translateBtn present?', 'translateBtn' in txt)
    print('translatePage present?', 'function translatePage' in txt)
    print('nav actions present?', has_nav)
    print('home link attrs?', 'href="index.html"' in txt and 'data-en="Home"' in txt)
    print('footer 2024 count', txt.count('&copy; 2024'))
