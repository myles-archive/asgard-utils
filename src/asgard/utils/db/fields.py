"""
Copyright (C) 2008 Myles Braithwaite

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
	
	http://www.apache.org/licenses/LICENSE-2.0
	
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

try:
    import uuid
except ImportError:
    from asgard.utils import uuid

from django.db.models import CharField, TextField
from django.utils.html import linebreaks
from django.conf import settings

from asgard.utils.templatetags.typogrify import amp

MARKUP_CHOICES = (
	('html', 'Plain HMTL'),
	('plain', 'Plain Text'),
)

try:
	from markdown import Markdown
	MARKUP_CHOICES += (('markdown', 'Markdown'),)
except ImportError:
	pass

try:
	from textile import textile
	MARKUP_CHOICES += (('textile', 'Textile'),)
except ImportError:
	pass

try:
	from docutils.core import publish_parts
	MARKUP_CHOICES += (('rest', 'ReStructured Text'),)
except ImportError:
	pass

class MarkupTextField(TextField):
	"""
	A TextField taht automatically implements DB-cached makup translation.
	
	Supports: Markdown, Plain HTML, Plain Text, and Textile.
	"""
	def __init__(self, *args, **kwargs):
		super(MarkupTextField, self).__init__(*args, **kwargs)
	
	def contribute_to_class(self, cls, name):
		self._html_field = "%s_html" % name
		self._markup_choices = "%s_markup_choices" % name
		TextField(editable=False, blank=True, null=True).contribute_to_class(cls, self._html_field)
		CharField(choices=MARKUP_CHOICES, max_length=10, blank=True, null=True).contribute_to_class(cls, self._markup_choices)
		super(MarkupTextField, self).contribute_to_class(cls, name)
	
	def pre_save(self, model_instance, add):
		value = getattr(model_instance, self.attname)
		markup = getattr(model_instance, self._markup_choices)
		if markup == 'markdown':
			md = Markdown()
			html = md.convert(value)
		elif markup == 'plain':
			html = linebreaks(amp(value), autoescape=True)
		elif markup == 'textile':
			html = textile(value)
		elif markup == 'rest':
			from asgard.utils import rest_directives
			docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
			parts = publish_parts(source=value, writer_name="html4css1", settings_overrides=docutils_settings)
			html = parts["fragment"]
		else:
			html = value
		setattr(model_instance, self._html_field, html)
		return value
	
	def __unicode__(self):
		return self.attname

class UUIDVersionError(Exception):
	pass

class UUIDField(CharField):
	def __init__(self, verbose_name=None, name=None, auto=True, version=1, node=None, clock_seq=None, namespace=None, **kwargs):
		kwargs['max_length'] = 36
		if auto:
			kwargs['blank'] = True
			kwargs.setdefault('editable', False)
		self.version = version
		if version==1:
			self.node, self.clock_seq = node, clock_seq
		elif version==3 or version==5:
			self.namespace, self.name = namespace, name
		CharField.__init__(self, verbose_name, name, **kwargs)
	
	def get_internal_type(self):
		return CharField.__name__
	
	def create_uuid(self):
		if not self.version or self.version==4:
			return uuid.uuid4()
		elif self.version==1:
			return uuid.uuid1(self.node, self.clock_seq)
		elif self.version==2:
			raise UUIDVersionError("UUID version 2 is not supported.")
		elif self.version==3:
			return uuid.uuid3(self.namespace, self.name)
		elif self.version==5:
			return uuid.uuid5(self.namespace, self.name)
		else:
			raise UUIDVersionError("UUID version %s is not valid." % self.version)
	
	def pre_save(self, model_instance, add):
		if self.auto and add:
			value = unicode(self.create_uuid())
			setattr(model_instance, self.attname, value)
			return value
		else:
			value = super(UUIDField, self).pre_save(model_instance, add)
			if self.auto and not value:
				value = unicode(self.create_uuid())
				setattr(model_instance, self.attname, value)
		return value
