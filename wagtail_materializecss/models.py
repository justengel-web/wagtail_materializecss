from __future__ import unicode_literals

from django.db import models
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel, FieldRowPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from .grid import Row, Col, h1, h2, h3, h4, h5, h6, make_row_col_blocks
from .components import LinkBlock, Badge, Button, FAB, Breadcrumb, Card, Collection, Icon, Preloader


__all__ = ['HEADINGS', 'FOOTER_BLOCKS', 'Navbar', 'Footer', 'MaterializePage']


HEADINGS = [('h1', h1()), ('h2', h2()), ('h3', h3()), ('h4', h4()), ('h5', h5()), ('h6', h6())]


FOOTER_BLOCKS = [('h1', h1()), ('h2', h2()), ('h3', h3()), ('h4', h4()), ('h5', h5()), ('h6', h6()),
                 ('Link', LinkBlock()), ('Badge', Badge()), ('Button', Button()), ('FAB', FAB()),
                 ('Collection', Collection()), ('icon', Icon())]
# FOOTER_BLOCKS.extend(make_row_col_blocks(FOOTER_BLOCKS))


class Navbar(models.Model):
    class Meta:
        abstract = True

    TITLE_POSITION = [
        ('', 'Inherit'),
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
        ]
    title_position = models.CharField(max_length=6, choices=TITLE_POSITION, default=TITLE_POSITION[0][0], blank=True,
                                      help_text='Title position')

    navbar_color = models.CharField(max_length=25, default='', blank=True,
                                    help_text='Navbar Color (Uses Parent Page if blank)')
    navbar_links = StreamField([('links', LinkBlock())], blank=True,
                               help_text='Navbar navigation links (Uses Parent Page if blank)')
    sidebar_links = StreamField([('links', LinkBlock())], blank=True,
                                help_text="Sidebar navigation links (Uses Navbar links if blank).")

    content_panels = [
        MultiFieldPanel([
            FieldRowPanel([FieldPanel('title_position'), FieldPanel('navbar_color')]),
            StreamFieldPanel('navbar_links'),
            ], heading='Navbar Fields', classname='collapsible collapsed'),
        MultiFieldPanel([
            StreamFieldPanel('sidebar_links'),
            ], heading='Sidebar (Mobile) Links', classname='collapsible collapsed'),
        ]

    def title_pos(self):
        if self.title_position:
            return self.title_position
        try:
            return self.get_parent().specific.title_pos()
        except:
            return self.title_position or 'center'

    def color(self):
        if self.navbar_color:
            return self.navbar_color
        try:
            return self.get_parent().specific.color()
        except:
            return self.navbar_color

    def nav_links(self):
        if self.navbar_links:
            return self.navbar_links
        try:
            return self.get_parent().specific.nav_links()
        except AttributeError:
            return []

    def sidenav_links(self):
        if self.sidebar_links:
            return self.sidebar_links
        try:
            parent = self.get_parent().specific
            if parent.sidebar_links:
                return parent.sidebar_links
        except AttributeError:
            pass
        return self.nav_links()


class Footer(models.Model):
    class Meta:
        abstract = True

    show_footer = models.BooleanField(default=False)
    footer_items = StreamField(FOOTER_BLOCKS, blank=True)
    footer_copyright = StreamField(FOOTER_BLOCKS, blank=True)

    content_panels = [
        MultiFieldPanel([
            FieldPanel('show_footer'),
            StreamFieldPanel('footer_items'),
            StreamFieldPanel('footer_copyright'),
            ], heading='Footer (Optional)', classname='collapsible collapsed'),
        ]

    def footer(self):
        if self.footer_items:
            return self.footer_items
        try:
            parent = self.get_parent().specific
            if parent.footer_items:
                return parent.footer_items
        except AttributeError:
            pass
        return []


class MaterializePage(Page, Navbar, Footer):
    class Meta:
        abstract = True

    content_panels = Page.content_panels + Navbar.content_panels + Footer.content_panels
