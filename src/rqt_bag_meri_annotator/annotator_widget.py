import os
import rospkg
import rospy
import rosbag
import vlc
import sys
import json

from python_qt_binding import QT_BINDING_MODULES
if (
    not QT_BINDING_MODULES['QtCore'].__name__.startswith('PyQt5') and
    'PyQt5' in sys.modules
):
    sys.modules['PyQt5'] = None

from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QFileDialog,  QGraphicsView, QMessageBox
from python_qt_binding.QtCore import qDebug, Qt, qWarning, Signal, QSettings
from python_qt_binding.QtGui import QIcon

from rqt_bag.bag_timeline import BagTimeline

class AnnotatorGraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super(AnnotatorGraphicsView, self).__init__()

class AnnotatorWidget(QWidget):
    """
    Annotator tool viewer
    """
    #name = 'Annotator'
    set_status_text = Signal(str)
    
    def __init__(self, context, bag_widget,publish_clock):
        super(AnnotatorWidget, self).__init__()
        rp = rospkg.RosPack()
        ui_file = os.path.join(rp.get_path('rqt_bag_meri_annotator'), 'resource', 'MeriPlugin.ui')
        loadUi(ui_file, self, {'AnnotatorGraphicsView': AnnotatorGraphicsView})
        self.setObjectName('AnnotatorWidget')
        self.setMouseTracking(True)
        self.annotation_data=list()
        self.interaction_time=120.0
        
        self.bag_widget=bag_widget
        self.bagtimeline=self.bag_widget._timeline
        self._child_index=0
        self.settings = QSettings("UFES","MERI Annotator Widget")
        #self.settings.setValue("Last_child_index",self._child_index)
        
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.isPaused = False
        self.msgBox=QMessageBox()
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setWindowTitle('Annotator Interface Information')
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        
        
        self.BtnSaveJson.clicked.connect(self.BtnSaveJsonClicked)       
        self.BtnLoadJson.clicked.connect(self.BtnLoadJsonClicked)
        self.BtnNext.clicked.connect(self.BtnNextClicked)
        self.BtnSetupBag.clicked.connect(self.BtnSetupBagClicked)
        self.BtnPrevious.clicked.connect(self.BtnPreviousClicked)
        self.BtnZero.clicked.connect(self.BtnZeroClicked)
        self.BtnOne.clicked.connect(self.BtnOneClicked)
        self.BtnTwo.clicked.connect(self.BtnTwoClicked)
        self.BtnAimLess.clicked.connect(self.BtnAimLessClicked)
        self.BtnGoalOriented.clicked.connect(self.BtnGoalOrientedClicked)
        self.BtnRobotStarted.clicked.connect(self.BtnRobotStartedClicked)
        self.BtnPointing.clicked.connect(self.BtnPointingClicked)
        self.BtnFollowLor.clicked.connect(self.BtnFollowLorClicked)
        self.BtnAdultSeek.clicked.connect(self.BtnAdultSeekClicked)
        self.BtnECTwC.clicked.connect(self.BtnECTwCClicked)
        self.BtnECTwR.clicked.connect(self.BtnECTwRClicked)
        self.BtnECTwT.clicked.connect(self.BtnECTwTClicked)
        self.BtnPlay.clicked.connect(self.BtnPlayClicked)
        self.BtnPause.clicked.connect(self.BtnPauseClicked)
        self.BtnStop.clicked.connect(self.BtnStopClicked)
        
        self.BtnPlay.setIcon(QIcon.fromTheme('media-playback-start'))
        self.BtnPause.setIcon(QIcon.fromTheme('media-playback-pause'))
        self.BtnLoadJson.setIcon(QIcon.fromTheme('document-open'))
        self.BtnSaveJson.setIcon(QIcon.fromTheme('document-save'))
        self.BtnStop.setIcon(QIcon.fromTheme('media-playback-stop'))
        self.BtnNext.setIcon(QIcon.fromTheme('go-next'))
        self.BtnSetupBag.setIcon(QIcon.fromTheme('document-properties'))
        self.BtnPrevious.setIcon(QIcon.fromTheme('go-previous'))

    def BtnSaveJsonClicked(self):
        if self.SpecialistName.text()=="":
            self.msgBox.setText('Please register your name in the <html><b> Specialist_Name </b></html> box')
            retval=self.msgBox.exec_()
        else:
            if len(self.annotation_data)==0:
                self.msgBox.setText('No annotation has been recorded')
                retval=self.msgBox.exec_()
            else:    
                annotationfile=[self.SpecialistName.text()+"_annotation_"+self._child_data[self._child_index]['ID']+".json"]
                annotationfile_path = os.path.join(os.path.expanduser('~'), 'Documents','Annotation_files', annotationfile[0])
                if os.path.exists(annotationfile_path):
                    self.msgBox.setText('<html><b>'+self.SpecialistName.text()+'</b></html> already recorder annotations for child: <html><b>' + self._child_data[self._child_index]['ID']+'</b></html>')
                    retval=self.msgBox.exec_()
                else:
                    with open(annotationfile_path, "w") as write_file:
                        json.dump(self.annotation_data, write_file)
                    self.msgBox.setText('Annotation File:  <html><b>' + annotationfile[0] + '</b></html> Saved!')
                    retval=self.msgBox.exec_()
    
    def BtnLoadJsonClicked(self):
        self._child_data=None
        json_path = self.settings.value("Last_path")
        if json_path == "":
            json_path = os.path.join(os.path.expanduser('~'), 'Documents')
        json_file = QFileDialog.getOpenFileName(self, "Open JSON File", json_path)
        self.settings.setValue("Last_path",json_file[0])
        with open(json_file[0]) as f:
            self._child_data=json.load(f)
        if self.settings.value("Last_child_index") is not None:
            self._child_index=int(self.settings.value("Last_child_index"))
        if self._child_index > len(self._child_data)-1:
            self._child_index=0
        self.LineChildId.setText(self._child_data[self._child_index]['ID'])
        self.msgBox.setText('Json Data of <html><b>' + str(len(self._child_data)) + '</b></html> Children were loaded')
        retval=self.msgBox.exec_()
        
        
    def BtnNextClicked(self):
        if self._child_index < len(self._child_data)-1:
            self._child_index=self._child_index+1
            self.LineChildId.setText(self._child_data[self._child_index]['ID'])
            self.settings.setValue("Last_child_index",self._child_index)
            
        
    def BtnPreviousClicked(self):
        if self._child_index > 0:
            self._child_index=self._child_index-1
            self.LineChildId.setText(self._child_data[self._child_index]['ID'])
            self.settings.setValue("Last_child_index",self._child_index)
        
    def BtnSetupBagClicked(self):
        kinect2_a_bag_name='image_kinect2_a_'+self._child_data[self._child_index]['Kinect_a']
        kinect2_b_bag_name='image_kinect2_b_'+self._child_data[self._child_index]['Kinect_b']
        focus_bag_name='focus_data_'+self._child_data[self._child_index]['Focus']
        
        k2a_bag_file=os.path.join(os.path.expanduser('~'), "Documents", "hg_rosbag","test_files",kinect2_a_bag_name)
        k2b_bag_file=os.path.join(os.path.expanduser('~'), "Documents", "hg_rosbag","test_files",kinect2_b_bag_name)
        focus_bag_file=os.path.join(os.path.expanduser('~'), "Documents", "hg_rosbag","test_files",focus_bag_name)
        
        self.bag_widget.load_bag(k2a_bag_file)
        self.bag_widget.load_bag(k2b_bag_file)
        #self.bag_widget.load_bag(focus_bag_file)

        audio_file_name=self._child_data[self._child_index]['Picture(jpg)/Audio(mp3)']+'.mp3'
        audio_media_file=os.path.join(os.path.expanduser('~'), "Documents", "hg_rosbag","audios",audio_file_name)
        self.OpenAudioMedia(audio_media_file)
        
        if self.checkCutBag.isChecked() == True:
            last_path=self.settings.value("Last_path")
            acronym_file=last_path[len(last_path)-9:len(last_path)-5]
            if acronym_file[0] == "s":
                config_name = ["cwa"+acronym_file+"_rs.json"]
            elif acronym_file[0] == "o":
                config_name = ["cw"+acronym_file+"_rs.json"]
            config_path = os.path.join(os.path.expanduser('~'), 'Documents',config_name[0])
            with open(config_path) as f:
                bag_config=json.load(f)
        
            if float(bag_config[self._child_index]['Sec']) > self.interaction_time:
                self.bagtimeline._timeline_frame._start_stamp=self.bagtimeline._timeline_frame._start_stamp+rospy.Duration.from_sec(float(bag_config[self._child_index]['Sec'])-self.interaction_time)
                self.annotation_data.append({'key':'Robot Started','time_stamp': 0, 'Sec':self.interaction_time})
            else:
                self.annotation_data.append({'key':'Robot Started','time_stamp': 0, 'Sec':float(bag_config[self._child_index]['Sec'])})
            if (self.bagtimeline._timeline_frame._end_stamp - self.bagtimeline._timeline_frame._start_stamp) > rospy.Duration.from_sec(self.interaction_time*2):
                self.bagtimeline._timeline_frame._end_stamp= self.bagtimeline._timeline_frame._start_stamp + rospy.Duration.from_sec(self.interaction_time*2)

    def BtnZeroClicked(self):
        task=self.ComBoxTask.currentText() + " 0 pts"
        self.AnnotationYamlCreator(task)
        
    def BtnOneClicked(self):
        task=self.ComBoxTask.currentText() + " 1 pts"
        self.AnnotationYamlCreator(task)
        
    def BtnTwoClicked(self):
        task=self.ComBoxTask.currentText() + " 2 pts"
        self.AnnotationYamlCreator(task)
        
    def BtnAimLessClicked(self):
        self.AnnotationYamlCreator('AimLess')   
        
    def BtnGoalOrientedClicked(self):
        self.AnnotationYamlCreator('Goal Oriented')     
        
    def BtnRobotStartedClicked(self):
        self.AnnotationYamlCreator('Robot Started') 
        
    def BtnPointingClicked(self):
        self.AnnotationYamlCreator('Pointing') 
        
    def BtnFollowLorClicked(self):
        self.AnnotationYamlCreator('Following LoR') 
        
    def BtnAdultSeekClicked(self):
        self.AnnotationYamlCreator('AdultSeek') 
        
    def BtnECTwCClicked(self):
        self.AnnotationYamlCreator('Eye Contact TwC') 
        
    def BtnECTwRClicked(self):
        self.AnnotationYamlCreator('Eye Contact TwR') 
        
    def BtnECTwTClicked(self):
        self.AnnotationYamlCreator('Eye Contact TwT')
        
    def BtnPlayClicked(self):
        self.bag_widget.play_button.setChecked(True)
        self.bag_widget.play_button.setIcon(self.bag_widget.pause_icon)
        self.bagtimeline.navigate_play()
        self.mediaplayer.play()
        
    def BtnPauseClicked(self):
        self.bag_widget.play_button.setChecked(False)
        self.bag_widget.play_button.setIcon(self.bag_widget.play_icon)
        self.bagtimeline.navigate_stop()
        self.mediaplayer.pause()
        
    def BtnStopClicked(self):
        self.bag_widget.play_button.setChecked(False)
        self.bag_widget.play_button.setIcon(self.bag_widget.play_icon)
        self.bagtimeline.navigate_stop()
        self.bagtimeline.navigate_start()
        self.mediaplayer.stop()             
                                            
    def AnnotationYamlCreator(self,Annotation):
        playhead_time=self.bagtimeline._timeline_frame.playhead
        self.annotation_data.append({'key':Annotation,'time_stamp': playhead_time.to_nsec(), 'Sec':(playhead_time - self.bagtimeline._timeline_frame.start_stamp).to_sec()})
            
    def OpenAudioMedia(self, filename=None):
          """Open a media file in a MediaPlayer
          """
          self.media = self.instance.media_new(filename)
          # put the media in the media player
          self.mediaplayer.set_media(self.media)        
        
    def shutdown_all(self):
        self.bagtimeline.handle_close()
        self.mediaplayer.stop()
        pass
