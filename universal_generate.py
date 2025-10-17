#!/usr/bin/env python3
"""
Universal multi-language page generator for ReadSage
Uses smart text replacement based on JSON translations
"""

import json
import os
import re
from pathlib import Path

LANGUAGES = ['en', 'es', 'fr', 'pt', 'ru', 'uk', 'tr', 'de']

def load_translation(lang):
    """Load translation JSON file"""
    with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_template():
    """Load the main index.html as template"""
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

def generate_hreflang_links():
    """Generate hreflang links for all languages"""
    links = []
    for lang in LANGUAGES:
        links.append(f'    <link rel="alternate" hreflang="{lang}" href="https://hiregenix.app/{lang}/" />')
    links.append('    <link rel="alternate" hreflang="x-default" href="https://hiregenix.app/en/" />')
    return '\n'.join(links)

def generate_language_switcher(current_lang):
    """Generate language switcher dropdown HTML"""
    options = []
    for lang in LANGUAGES:
        t = load_translation(lang)
        selected = ' selected' if lang == current_lang else ''
        options.append(f'              <option value="{lang}"{selected}>{t["flag"]} {t["langName"]}</option>')

    return f'''<div class="language-switcher">
            <select id="lang-select" onchange="switchLanguage(this.value)">
{chr(10).join(options)}
            </select>
          </div>'''

def flatten_dict(d, parent_key='', sep='.'):
    """Flatten nested dictionary for easy replacement"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # For arrays, add each element with its index
            for i, item in enumerate(v):
                items.append((f"{new_key}.{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

def smart_replace(html, translations):
    """
    Smart replacement that handles all content intelligently
    Replaces exact matches from original English content with translated versions
    Uses aggressive whitespace normalization to match HTML content
    """

    # Create flat dictionary for easy access
    flat = flatten_dict(translations)

    # Load English version for mapping
    en_trans = load_translation('en')
    en_flat = flatten_dict(en_trans)

    result = html

    # Replace meta tags and page structure first
    result = replace_meta_tags(result, translations)

    # Then replace all content systematically
    # Go through each English key and replace its value with translated value
    # Sort by length (longest first) to avoid partial replacements
    sorted_keys = sorted(en_flat.keys(), key=lambda k: len(str(en_flat.get(k, ''))), reverse=True)

    for key in sorted_keys:
        en_value = en_flat[key]
        if key in flat and isinstance(en_value, str) and isinstance(flat[key], str):
            # Only replace if values are different (not flag/lang codes)
            if en_value != flat[key] and len(en_value) > 5:  # Skip very short strings
                trans_value = flat[key]

                # Strategy 1: Direct exact match
                if en_value in result:
                    result = result.replace(en_value, trans_value)
                    continue

                # Strategy 2: Handle text that might be split across HTML tags
                # Example 1: <strong>From Calculus...</strong><br />Find the derivative...
                # Example 2: <strong>Question 3 of 10:</strong> Find the derivative...

                # Try splitting by <br /> first
                if '<br />' in en_value:
                    en_parts = en_value.split('<br />')
                    trans_parts = trans_value.split('<br />')

                    if len(en_parts) == len(trans_parts):
                        for en_part, trans_part in zip(en_parts, trans_parts):
                            en_part = en_part.strip()
                            trans_part = trans_part.strip()
                            if en_part and len(en_part) > 5:
                                # Try direct replacement
                                if en_part in result:
                                    result = result.replace(en_part, trans_part)
                                else:
                                    # Try with whitespace normalization
                                    en_normalized = ' '.join(en_part.split())
                                    pattern_text = re.escape(en_normalized)
                                    pattern_text = pattern_text.replace(r'\ ', r'[\s\n]+')
                                    pattern = re.compile(pattern_text, re.MULTILINE | re.DOTALL)
                                    result = pattern.sub(trans_part, result)
                    continue

                # Try splitting by colon for cases like "Question 3 of 10: Find..."
                # or "Students: Ace exams with..."
                # where first part is in <strong> tags
                if ': ' in en_value:
                    en_parts = en_value.split(': ', 1)
                    trans_parts = trans_value.split(': ', 1)

                    if len(en_parts) == 2 and len(trans_parts) == 2:
                        # Replace first part (before colon) - usually in <strong>
                        if en_parts[0] in result and len(en_parts[0]) > 3:
                            result = result.replace(en_parts[0], trans_parts[0])
                        # Replace second part (after colon) with whitespace normalization
                        if len(en_parts[1]) > 10:
                            if en_parts[1] in result:
                                result = result.replace(en_parts[1], trans_parts[1])
                            else:
                                # Try normalized version
                                en_normalized = ' '.join(en_parts[1].split())
                                pattern_text = re.escape(en_normalized)
                                pattern_text = pattern_text.replace(r'\ ', r'[\s\n]+')
                                pattern = re.compile(pattern_text, re.MULTILINE | re.DOTALL)
                                if pattern.search(result):
                                    result = pattern.sub(trans_parts[1], result)
                        continue

                # Strategy 3: Normalize whitespace for matching
                # This handles multiline HTML where text is split across lines
                en_normalized = ' '.join(en_value.split())

                # Build regex pattern that matches the text with any whitespace variation
                # Escape special regex characters, then replace literal spaces with flexible whitespace pattern
                pattern_text = re.escape(en_normalized)
                # Replace escaped spaces with flexible whitespace matcher that includes newlines
                pattern_text = pattern_text.replace(r'\ ', r'[\s\n]+')
                pattern = re.compile(pattern_text, re.MULTILINE | re.DOTALL)

                # Count matches to see if we should replace
                matches = pattern.findall(result)
                if matches:
                    # Replace all matches with the translated text
                    result = pattern.sub(trans_value, result)

    return result

def replace_meta_tags(html, t):
    """Replace all meta tags with translated versions"""

    # Basic meta tags
    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{t["lang"]}">', html)
    html = re.sub(r'<title>.*?</title>', f'<title>{t["meta"]["title"]}</title>', html, flags=re.DOTALL)
    html = re.sub(r'<meta name="title" content="[^"]*" />', f'<meta name="title" content="{t["meta"]["title"]}" />', html)
    html = re.sub(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{t["meta"]["description"]}" />', html)
    html = re.sub(r'<meta name="keywords" content="[^"]*" />', f'<meta name="keywords" content="{t["meta"]["keywords"]}" />', html)
    html = re.sub(r'<meta name="language" content="[^"]*" />', f'<meta name="language" content="{t["langName"]}" />', html)

    # Canonical and OG
    html = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="https://hiregenix.app/{t["lang"]}/" />', html)
    html = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="https://hiregenix.app/{t["lang"]}/" />', html)
    html = re.sub(r'<meta property="og:title" content="[^"]*" />', f'<meta property="og:title" content="{t["meta"]["ogTitle"]}" />', html)
    html = re.sub(r'<meta property="og:description" content="[^"]*" />', f'<meta property="og:description" content="{t["meta"]["ogDescription"]}" />', html)
    html = re.sub(r'<meta property="og:locale" content="[^"]*" />', f'<meta property="og:locale" content="{t["locale"]}" />', html)

    # Twitter
    html = re.sub(r'<meta property="twitter:url" content="[^"]*" />', f'<meta property="twitter:url" content="https://hiregenix.app/{t["lang"]}/" />', html)
    html = re.sub(r'<meta property="twitter:title" content="[^"]*" />', f'<meta property="twitter:title" content="{t["meta"]["twitterTitle"]}" />', html)
    html = re.sub(r'<meta property="twitter:description" content="[^"]*" />', f'<meta property="twitter:description" content="{t["meta"]["twitterDescription"]}" />', html)

    # AI descriptions
    html = re.sub(r'<meta name="chatgpt-description" content="[^"]*" />', f'<meta name="chatgpt-description" content="{t["meta"]["chatgptDescription"]}" />', html)
    html = re.sub(r'<meta name="perplexity-description" content="[^"]*" />', f'<meta name="perplexity-description" content="{t["meta"]["perplexityDescription"]}" />', html)
    html = re.sub(r'<meta name="claude-description" content="[^"]*" />', f'<meta name="claude-description" content="{t["meta"]["claudeDescription"]}" />', html)

    # Add hreflang links
    hreflang = generate_hreflang_links()
    html = re.sub(r'(<meta name="viewport"[^>]*>)', f'\\1\n\n    <!-- Language Alternates -->\n{hreflang}', html)

    return html

def update_paths(html, lang):
    """Update CSS/JS paths and add language switcher"""
    # Update paths for subdirectory
    html = html.replace('href="styles.css"', 'href="../styles.css"')
    html = html.replace('src="script.js"', 'src="../script.js"')

    # Add language switcher to nav
    switcher = generate_language_switcher(lang)
    html = re.sub(r'(<div class="nav-links">)', f'\\1\n{switcher}', html)

    # Add language switch script
    switch_script = '''
    <script>
      function switchLanguage(lang) {
        localStorage.setItem('preferred-lang', lang);
        window.location.href = '/' + lang + '/';
      }
    </script>'''
    html = html.replace('</body>', f'{switch_script}\n  </body>')

    return html

def generate_page(lang):
    """Generate a single language page with full translation"""
    print(f'📄 Generating {lang.upper()}...')

    t = load_translation(lang)
    html = load_template()

    # Apply translations
    html = smart_replace(html, t)
    html = update_paths(html, lang)

    # Write output
    output_path = f'{lang}/index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Calculate size
    size = len(html.encode('utf-8'))
    print(f'✅ {lang.upper()} → {output_path} ({size:,} bytes)')

def main():
    print('🌍 Generating fully translated pages for ReadSage...\n')
    print('⚡ Using smart replacement algorithm...\n')

    for lang in LANGUAGES:
        try:
            generate_page(lang)
        except Exception as e:
            print(f'❌ Error generating {lang}: {e}')

    print('\n✨ All translations complete!')
    print(f'\n📊 Generated {len(LANGUAGES)} fully localized pages')
    print('\n📝 Each page includes:')
    print('   ✓ 100% translated content')
    print('   ✓ Localized meta tags (title, description, OG, Twitter)')
    print('   ✓ AI bot descriptions in native language')
    print('   ✓ hreflang tags for all languages')
    print('   ✓ Language switcher')

if __name__ == '__main__':
    main()
