import os
import rospy
import rospkg
import argparse

from qt_gui.plugin import Plugin
from .annotator_widget import AnnotatorWidget
from rqt_bag.bag import Bag

class MeriPlugin(Plugin):

    def __init__(self,context):
        super(MeriPlugin, self).__init__(context)
        self.setObjectName('AnnotatorPlugin')
        
        parser = argparse.ArgumentParser(prog='rqt_annotator', add_help=False)
        MeriPlugin.add_arguments(parser)
        # Add argument(s) to the parser.
        args =parser.parse_args(context.argv())
        
        # Create QWidget
        self.bag_plugin=Bag(context)
        self._widget = AnnotatorWidget(context, self.bag_plugin._widget,args.clock)
        if context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)
            
    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group('Options for Annotator_bag plugin')
        group.add_argument('--clock', action='store_true', help='publish the clock time')
        group.add_argument('bagfiles', type=lambda x: Bag._isfile(parser, x), nargs='*', default=[], help='Bagfiles to load')    
        
    def shutdown_plugin(self):
        self._widget.shutdown_all()

    def save_settings(self, plugin_settings, instance_settings):
        # TODO implement saving
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO implement restoring
        # v = instance_settings.value(k)
        pass
