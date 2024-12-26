from django import template
import re
import markdown2

register = template.Library()

@register.filter
def highlight(text, query):
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda match: f'<strong>{match.group(0)}</strong>', text)

@register.filter
def markdown_to_html(text):
    return markdown2.markdown(text)