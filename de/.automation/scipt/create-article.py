import re
import os

def replace_links(text):
    # Define the regular expression pattern to match [text](url)
    pattern = r'\[(.*?)\]\((.*?)\)'
    
    # Define a function to use in re.sub for replacing matches
    def replace_match(match):
        link_text = match.group(1)  # The text part
        link_url = match.group(2)   # The URL part
        # Return the HTML formatted link
        return f'<a href="{link_url}">{link_text}</a>'
    
    # Use re.sub to replace all occurrences of the pattern in the text
    replaced_text = re.sub(pattern, replace_match, text)
    return replaced_text


def markdown_table_to_html(markdown):
    # Regex to match multiple markdown tables
    table_pattern = r"(\|(?:[^\n\|]+\|)+)\n(\|(?:[-: ]+\|)+)\n((?:\|(?:[^\n\|]+\|)+\n)*)"
    
    def convert_table(match):
        header = match.group(1)
        rows = match.group(3)
        
        # Convert header row to HTML
        headers = header.strip().split('|')[1:-1]
        header_html = "<thead><tr>" + "".join(f"<th>{col.strip()}</th>" for col in headers) + "</tr></thead>"
        
        # Convert table rows to HTML
        rows_html = ""
        for row in rows.strip().split('\n'):
            columns = row.split('|')[1:-1]
            rows_html += "<tr>" + "".join(f"<td>{col.strip()}</td>" for col in columns) + "</tr>"
        
        # Create full HTML table
        table_html = f"<div class=\"table-container\"><table class=\"styled-table\">{header_html}<tbody>{rows_html}</tbody></table></div>"
        
        return table_html
    
    # Replace each markdown table with corresponding HTML
    updated_markdown = re.sub(table_pattern, convert_table, markdown)
    
    return updated_markdown

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

def replace_bold_with_html(md_string):
    # Regular expression to find text enclosed in **bold**
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_string)

def replace_markdown_with_html_img(md_string):
    # Replace markdown bold with HTML <strong> tags
    md_string = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_string)
    
    # Replace markdown image links ![[image]] with HTML <img> tags
    md_string = re.sub(r'!\[\[(.*?)\]\]', r'<img src="../img/\1" alt="\1">', md_string)
    
    return md_string

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

    full_art = markdown_table_to_html(full_art)

    full_art = replace_links(full_art)

    full_art = replace_bold_with_html(full_art)

    full_art = replace_markdown_with_html_img(full_art)

    art = full_art.splitlines()

    title = art[0].replace("# ", "")
    date = art[1]
    thumbnail = art[2].replace("![[", "").replace("]]", "")

    content = ""

    languages = {
        "": "language-json",
        "yaml": "language-yaml",
        "dart": "language-dart"
    }

    codePresets = {
        "lineStart": "<p>",
        "lineEnd": "</p>" + "\n",
        "codeBlockStart": "<pre><code class=\"LANG\">",
        "codeBlockEnd": "</pre></code>" + "\n",
        "inlineCodeStart": "<code class=\"language-json\">",
        "inlineCodeEnd": "</code>",
        "headingStart": "<hI id=\"EL\">",
        "headingEnd": "</hI>" + "\n",
        "unorderedListStart": "<ul>",
        "unorderedListEnd": "</ul>" + "\n",
        "ListElement": lambda el : "<li>" + el + "</li>" + "\n",
    }

    inCodeBlock = False
    inUnorderedList = False
    headingCounter = 1

    for line in art[3:]:
        if line.startswith("```"):
            if inCodeBlock:
                content += codePresets["codeBlockEnd"]
                inCodeBlock = False
            else:
                lang = languages[line.replace("```", "")]
                content += codePresets["codeBlockStart"].replace("LANG", lang)
                inCodeBlock = True
            continue
        elif inCodeBlock:
            content += line + "\n"
            continue
        
        if line.startswith("#"):
            i = 0
            for char in line:
                if char == "#":
                    i += 1
            content += codePresets["headingStart"].replace("I", str(i)).replace("EL", f"heading{headingCounter}")
            content += line[i:]
            content += codePresets["headingEnd"].replace("I", str(i))
            headingCounter += 1
        elif line.startswith("- "):
            if not inUnorderedList:
                content += codePresets["unorderedListStart"]
                inUnorderedList = True
            content += codePresets["ListElement"](line[2:])
        else:
            if inUnorderedList:
                content += codePresets["unorderedListEnd"]
                inUnorderedList = False
            content += codePresets["lineStart"]
            inlineCode = 0
            for char in line:
                if char == "`":
                    if inlineCode % 2 == 0:
                        content += codePresets["inlineCodeStart"]
                    else:
                        content += codePresets["inlineCodeEnd"]
                    inlineCode += 1
                else:
                    content += char
            content += codePresets["lineEnd"]

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