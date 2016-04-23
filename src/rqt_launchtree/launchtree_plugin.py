#!/usr/bin/env python
from rqt_gui_py.plugin import Plugin

from python_qt_binding.QtCore import Qt
from python_qt_binding.QtGui import QInputDialog

from rqt_launchtree.launchtree_widget import LaunchtreeWidget


class LaunchtreePlugin(Plugin):

    def __init__(self, context):
        super(LaunchtreePlugin, self).__init__(context)

        self._widget = LaunchtreeWidget(context)
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() +
                                        (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

    def shutdown_plugin(self):
        self._widget.shutdown()

    def save_settings(self, plugin_settings, instance_settings):
        instance_settings.set_value('editor', self._widget.editor)

    def restore_settings(self, plugin_settings, instance_settings):
        self._widget.editor = instance_settings.value('editor', 'gedit')

    def trigger_configuration(self):
        (text, ok) = QInputDialog.getText(self._widget,
            'Settings for %s' % self._widget.windowTitle(),
            'Command to edit launch files (vim, gedit, ...), can accept args:',
            text = self._widget.editor
        )
        if ok:
            self._widget.editor = text