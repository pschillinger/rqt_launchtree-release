#!/usr/bin/env python
import rospy
from roslaunch.config import ROSLaunchConfig

class LaunchtreeArg(object):
	def __init__(self, name, default=None, value=None, doc=None):
		self.name = name
		self.default = default
		self.value = value
		self.doc = doc
	def merge(self, other):
		if self.default is None and other.default is not None:
			self.default = other.default
		if self.value is None and other.value is not None:
			self.value = other.value
		if self.doc is None and other.doc is not None:
			self.doc = other.doc

class LaunchtreeRemap(object):
	def __init__(self, from_topic, to_topic):
		self.from_topic = from_topic
		self.to_topic = to_topic

class LaunchtreeConfig(ROSLaunchConfig):

	def __init__(self):
		super(LaunchtreeConfig, self).__init__()

		self._tree_stack = list()
		self.tree = dict()
		self.idx = 0

	def push_level(self, tree_level, unique=False):
		if unique:
			tree_level += ':%d' % self.idx
			self.idx += 1
		self._tree_stack.append(tree_level)

	def pop_level(self):
		return self._tree_stack.pop()

	def _add_to_tree(self, key, instance):
		level = self.tree
		for launch in self._tree_stack:
			if not launch in level:
				level[launch] = dict()
			level = level[launch]
		if level.has_key(key):
			if isinstance(level[key], dict):
				level[key]['_root'] = instance
			if isinstance(level[key], LaunchtreeArg):
				level[key].merge(instance)
		else:
			level[key] = instance

	def add_executable(self, exe):
		result = super(LaunchtreeConfig, self).add_executable(exe)
		self._add_to_tree(exe.command, exe)
		return result

	def add_param(self, p, filename=None, verbose=True):
		p.inconsistent = False
		if p.key in self.params and (p.value != self.params[p.key].value or self.params[p.key].inconsistent):
			p.inconsistent = True
			self.params[p.key].inconsistent = True
			rospy.logwarn('Inconsistent param: %s\n  - %s: %s\n  - %s: %s' % 
				(p.key, p.key, str(p.value), self.params[p.key].key, str(self.params[p.key].value)))
		result = super(LaunchtreeConfig, self).add_param(p, filename, verbose)
		self._add_to_tree(p.key, p)
		return result

	def add_machine(self, m, verbose=True):
		result = super(LaunchtreeConfig, self).add_machine(m, verbose)
		self._add_to_tree(m.name, m)
		return result

	def add_test(self, test, verbose=True):
		result = super(LaunchtreeConfig, self).add_test(test, verbose)
		self._add_to_tree(test.name, test)
		return result

	def add_node(self, node, core=False, verbose=True):
		result = super(LaunchtreeConfig, self).add_node(node, core, verbose)
		self._add_to_tree(node.name, node)
		return result

	def add_arg(self, name, default=None, value=None, doc=None):
		self._add_to_tree(name, LaunchtreeArg(name, default, value, doc))

	def add_remap(self, from_topic, to_topic):
		self._add_to_tree(from_topic, LaunchtreeRemap(from_topic, to_topic))