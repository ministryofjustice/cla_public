from django import template


register = template.Library()


class StyleFormNode(template.Node):
    def __init__(self, form):
        self.form = template.Variable(form)

    def render(self, context):
        try:
            form = self.form.resolve(context)
            for field in form.fields:
                name = form.fields[field].widget.__class__.__name__.lower()
                if not name.startswith("radio") and not name.startswith("checkbox"):
                    form.fields[field].widget.attrs["class"] = " form-control"
        except template.VariableDoesNotExist:
            pass
        return ''


@register.tag(name="style_form")
def style_form(parser, token):
    try:
        tag_name, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one arguments" % token.contents.split()[0])
    return StyleFormNode(form)
