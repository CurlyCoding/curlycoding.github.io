import re
import os


# Dictionary for code languages
languages = {
    'python': 'language-python',
    'js': 'language-javascript',
    'html': 'language-html',
    'css': 'language-css',
    'json': 'language-json',
    "yaml": "language-yaml",
    "dart": "language-dart",
    "": "language-json"
}

def markdown_to_html(markdown_text):
    # A list to hold extracted code blocks
    code_blocks = []

    # Function to replace code block with a placeholder
    def extract_code_block(match):
        lang = match.group(1)
        code = match.group(2)
        code_blocks.append((lang, code))  # Store the language and code
        return f"{{codeblock_{len(code_blocks) - 1}}}"  # Return a placeholder

    # Step 1: Extract code blocks and replace with placeholders
    markdown_text = re.sub(r"```(\w+)\n([\s\S]*?)```", extract_code_block, markdown_text)

    # Step 2: Replace headings
    for i in range(6, 0, -1):
        markdown_text = re.sub(rf'(?m)^({"#" * i})\s+(.+)$', rf'<h{i} id="\2">\2</h{i}>', markdown_text)

    # Step 3: Replace bold text
    markdown_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', markdown_text)

    # Step 4: Replace inline code
    markdown_text = re.sub(r'`(.+?)`', r'<code class="language-json">\1</code>', markdown_text)

    # Step 5: Replace links
    markdown_text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', markdown_text)

    # Step 6: Replace images
    markdown_text = re.sub(r'!\[\[(.+?)\]\]', r'<img src="../img/\1" alt="\1">', markdown_text)

    # Step 7: Convert markdown tables to HTML tables
    def replace_table(match):
        rows = match.group(0).strip().split('\n')
        headers = rows[0].strip('|').split('|')
        headers_html = ''.join(f'<th>{header.strip()}</th>' for header in headers)

        table_body = ''
        for row in rows[2:]:  # Skip the separator row (---)
            cells = row.strip('|').split('|')
            row_html = ''.join(f'<td>{cell.strip()}</td>' for cell in cells)
            table_body += f'<tr>{row_html}</tr>'

        return f'<div class=\"table-container\"><table class=\"styled-table\"><thead><tr>{headers_html}</tr></thead><tbody>{table_body}</tbody></table></div>'

    markdown_text = re.sub(r"(\|(?:[^\n\|]+\|)+)\n(\|(?:[-: ]+\|)+)\n((?:\|(?:[^\n\|]+\|)+\n)*)", replace_table, markdown_text)

    # Step 8: Replace ordered lists
    def replace_ordered_list(match):
        items = match.group(0).strip().split('\n')
        items_html = ''.join('<li>{}</li>'.format(re.sub(r"^\d+\.\s+", "", item)) for item in items if item.strip())
        return f'<p><ol>{items_html}</ol></p>'

    markdown_text = re.sub(r'(?ms)(^\d+\. .+(\n\d+\. .+)*)', replace_ordered_list, markdown_text)

    # Step 9: Replace unordered lists
    def replace_unordered_list(match):
        # Capture all items in the unordered list
        items = match.group(0).strip().split('\n')
        # Perform substitution and construct the <ul> once for all list items
        items_html = ''.join('<li>{}</li>'.format(re.sub(r"^-\s+", "", item)) for item in items if item.strip())
        return f'<p><ul>{items_html}</ul></p>'

    # Capture entire blocks of unordered lists (matching `- item` across multiple lines)
    markdown_text = re.sub(r'(?m)(^- .+(\n^- .+)*)', replace_unordered_list, markdown_text)


    # Step 10: Replace paragraphs (anything not part of a special tag)
    markdown_text = re.sub(r'(?m)^(?!<h|<pre|<ol|<ul|<img|<strong|<table)(.+)$', r'<p>\1</p>', markdown_text)

    # Step 11: Restore the code blocks in the final HTML output
    def restore_code_block(match):
        index = int(match.group(1))  # Get the code block index
        lang, code = code_blocks[index]
        lang_class = languages.get(lang, 'language-plain')  # Get the language class
        return f'<pre><code class="{lang_class}">{code}</code></pre>'

    html_output = re.sub(r'\{codeblock_(\d+)\}', restore_code_block, markdown_text)

    return html_output

def generate_toc(html_content):
    # Regex patterns to capture different heading levels (h2, h3, h4)
    heading_pattern = r'<h([2-4]) id="([^"]+)">([^<]+)</h[2-4]>'
    
    # Store the TOC items
    toc = []
    
    # Find all matches for h2, h3, h4 headings
    headings = re.findall(heading_pattern, html_content)
    
    # Build TOC structure
    toc.append('<nav class="table-of-contents">\n<h2>Inhaltsverzeichnis</h2>\n<ul>')
    prev_level = 2  # Start from h2 level

    for level, heading_id, heading_text in headings:
        level = int(level)
        
        if level > prev_level:
            toc.append('<ul>\n')  # Nested list for subheadings
        elif level < prev_level:
            toc.append('</ul>\n')  # Close previous nested list
        
        toc.append(f'<li><a href="#{heading_id}">{heading_text}</a></li>\n')
        prev_level = level
    
    # Close any remaining open lists
    toc.append('</ul>\n</nav>\n')
    
    return ''.join(toc)

def insert_toc(html_content, toc):
    # Find the insertion point for the TOC (after the opening <article> tag)
    insertion_point = re.search(r'<article[^>]*>', html_content)
    
    if insertion_point:
        insert_pos = insertion_point.end()
        return html_content[:insert_pos] + '\n' + toc + html_content[insert_pos:]
    
    # If <article> tag not found, append the TOC to the top
    return toc + html_content

def get_all_filenames(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        print(f"Error: {e}")
        return []

def convert_file(file):
    with open("article-preset.html", "r") as f:
        articleFile = f.read()

    with open("../markdowns/" + file) as f:
        full_art = f.read()

    art = full_art.splitlines()

    title = art[0].replace("# ", "")
    date = art[1]
    thumbnail = "<img src=\"../img/" + art[2].replace("![[", "").replace("]]", "") + "\">"

    content = markdown_to_html("\n".join(art[3:]))

    articleFile = articleFile.replace("TITLE", title)
    articleFile = articleFile.replace("DATE", date)
    articleFile = articleFile.replace("THUMBNAIL", thumbnail)
    articleFile = articleFile.replace("CONTENT", content)

    if True:
        toc = generate_toc(articleFile)
        # Insert the TOC into the HTML
        articleFile = insert_toc(articleFile, toc)

    return articleFile

files = get_all_filenames("../markdowns")

for file in files:
    with open("../" + file.replace(".md", ".html"), "w") as f:
        f.write(convert_file(file))