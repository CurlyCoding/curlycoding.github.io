import re

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

file = input("Enter the Markdown file: ")
date = "18. September 2024"

with open("article-preset.html", "r") as f:
    articleFile = f.read()

with open(file) as f:
    full_art = f.read()

full_art = markdown_table_to_html(full_art)

full_art = replace_links(full_art)

art = full_art.splitlines()

title = file.replace(".md", "")

thumbnail = art[0].replace("![[", "").replace("]]", "")

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
    "headingStart": "<hI>",
    "headingEnd": "</hI>" + "\n",
    "unorderedListStart": "<ul>",
    "unorderedListEnd": "</ul>" + "\n",
    "ListElement": lambda el : "<li>" + el + "</li>" + "\n",
}

inCodeBlock = False
inUnorderedList = False

for line in art[1:]:
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
        content += codePresets["headingStart"].replace("I", str(i))
        content += line[i:]
        content += codePresets["headingEnd"].replace("I", str(i))
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

with open(title + ".html", "w") as f:
    f.write(articleFile)
