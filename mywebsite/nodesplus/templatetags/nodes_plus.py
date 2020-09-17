import json
from django.template import Library, Node
from django.template.base import token_kwargs
from django.template.defaultfilters import stringfilter
from django.template.exceptions import TemplateSyntaxError
from django.utils.html import format_html, format_html_join, urlize
from django.utils.safestring import SafeData, SafeString, mark_safe

register = Library()


class MacroNode(Node):
    def __init__(self, items, extra_context=None):
        self.items = items
        self.extra_context = extra_context or {}

    def render(self, context):
        values = {
            key: value.resolve(context) 
                for key, value in self.extra_context.items()
        }
        context.push(**values)
        return ''


class NavbarNode(Node):
    def __init__(self, views, links, for_authenticated=False):
        self.views = views
        self.for_authenticated = for_authenticated
        self.base_views = links

    def render(self, context):
        from django.urls import reverse, NoReverseMatch
        user = context['user']

        output = ''
        icon_html = """
        <ul class="navbar-nav mr-auto">
            <li class="nav-item">
                <a href="{}" class="nav-link">
                    <i class="fa fa-{}"></i>
                </a>
            </li>
        </ul>
        """
        base_structure = """
        <ul class="navbar-nav mr-auto">
            {links}
        </ul>
        """
        text_html = """
        <li class="nav-item">
            <a href="{}" class="nav-link">
                {}
            </a>
        </li> 
        """
        constructed_links = ''
        for view in self.base_views:
            try:
                url = reverse(view[0])
            except:
                raise NoReverseMatch(f"For reverse for '{view[0]}'")
            else:
                constructed_links += format_html(
                    text_html, url, view[1]['verbose_name']
                )
        
        nav_item = mark_safe(base_structure.format(links=constructed_links))

        if user.is_authenticated:
            if user.is_admin or user.is_staff:
                nav_item = format_html(
                    nav_item,
                    '/admin', 'Admin'
                )
        output += nav_item
        return output


@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def price_to_text(price, currency=None, autoescape=True):
    currencies = ['$', '£', '€']
    if currency is None:
        currency = '€'
    if currency not in currencies:
        raise TemplateSyntaxError(f"Currency is not valid: {currency}")
    if currency != '€':
        return f"{currency}{price}"
    return f"{price}{currency}"


@register.filter(is_safe=True)
@stringfilter
def number_to_percentage(value):
    return f"{value}%"


@register.tag
def template_variable(parser, token):
    bits = token.split_contents()
    remaining_bits = bits[1:]
    extra_context = token_kwargs(remaining_bits, parser, support_legacy=False)
    if not extra_context:
        raise TemplateSyntaxError(
            f"'{bits[0]}' expects at least one key word variable"
        )
    return MacroNode(remaining_bits, extra_context=extra_context)


@register.tag
def authenticated_navbar_links(parser, token):
    views = token.split_contents()[1:]
    authenticated_views = [
        ('accounts:profile:home', {'icon': 'user', 'verbose_name': 'Profile'}),
        ('accounts:logout', {'icon': 'sign-out', 'verbose_name': 'Logout'})
    ]
    return NavbarNode(views, authenticated_views, for_authenticated=True)


@register.tag
def non_authenticated_navbar_links(parser, token):
    views = token.split_contents()[1:]
    links = [
        ('accounts:login', {'icon': 'sign-in', 'verbose_name': 'Login'}),
        ('accounts:signup', {'icon': 'signup', 'verbose_name': 'Signup'})
    ]
    return NavbarNode(views, links, for_authenticated=False)