import os
import rospkg
import rospy
import rosbag
import vlc
import sys

from rqt_bag import TopicMessageView
from python_qt_binding import QT_BINDING_MODULES
if (
    not QT_BINDING_MODULES['QtCore'].__name__.startswith('PyQt5') and
    'PyQt5' in sys.modules
):
    sys.modules['PyQt5'] = None

from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QFileDialog

class AnnotatorPlugin(TopicMessageView):
    """
    Popup annotator tool viewer
    """
    name = 'Annotator'
    
    def __init__(self, timeline, parent, topic):
        super(AnnotatorPlugin, self).__init__(timeline, parent, topic)
        rp = rospkg.RosPack()
        self._timeline=timeline
        self._message_stamp = None
        self._bag = None
        self.msg = None
        self._topic = None
        self._annotator_widget = QWidget()
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.isPaused = False
        
        ui_file = os.path.join(rp.get_path('rqt_bag_meri_annotator'), 'resource', 'MeriPlugin.ui')
        loadUi(ui_file, self._annotator_widget)
        self._annotator_widget.setObjectName('MeriPluginUi')
        self._annotator_widget.BtnAnnotator1.clicked.connect(self.btnClicked)
        parent.layout().addWidget(self._annotator_widget)

    def btnClicked(self):
        tmp_path=os.path.join(os.path.expanduser('~'), "Documents", "hg_rosbag","test_files")
        filename = QFileDialog.getOpenFileName(self._annotator_widget, "Open File", tmp_path)
        bag = rosbag.Bag(filename[0])
        self._timeline.add_bag(bag)    
        #self.OpenFile()
        print self._message_stamp
            
    def message_viewed(self, bag, msg_details):
        """
        refreshes the image
        """
        super(AnnotatorPlugin, self).message_viewed(bag, msg_details)
        self._topic, self.msg, _ = msg_details
        if not self.msg:
            self.set_message('no message')
        else:
            self.set_message()
            
    def put_message_into_file(self):
        if self._message_stamp:
            print('Running') #self._message_stamp
            
    def OpenFile(self, filename=None):
          """Open a media file in a MediaPlayer
          """
          if filename is None:
              tmp_path=os.path.join(os.path.expanduser('~'), "Documents", "hg_rosbag","audios")
              filename = QFileDialog.getOpenFileName(self._annotator_widget, "Open File", tmp_path)
          if not filename:
              return
          # create the media
          print filename
          self.media = self.instance.media_new(filename[0])
          # put the media in the media player
          self.mediaplayer.set_media(self.media)
          self.mediaplayer.play()        
            
    def set_message(self):
        self._message_stamp = self.msg.header.stamp
        self.put_message_into_file()
        
    def message_cleared(self):
        pass
