"""
This class orchestrate the video editing process based on the provided arguments.
"""
import argparse
import os

from features.concatenate import Concatenate
from features.generate_subtitles import GenerateSubtitles
from features.j_cut import JCut
from features.preprocess_videos import PreprocessVideos
from features.remove_silence import RemoveSilence

from entities.timeline import Timeline


class Orchestrator:
    def __init__(self):
        self.args = None
        self.input_folder = None
        self.input_video = None
        self.subtitles_video = None

        # Features
        self.preprocess_feat: PreprocessVideos = None
        self.remove_silence_feat: RemoveSilence = None
        self.generate_subtitles_feat: GenerateSubtitles = None
        self.jcut_feat: JCut = None

        # Entities
        self.timeline = None

    def parse_arguments(self):
        """
        Parse the arguments.
        """
        # Get arguments
        parser = argparse.ArgumentParser(description='Create FCPXML file.')
        parser.add_argument('input', type=str, help='Folder with the video files to be edited or a specific file.')
        parser.add_argument('--skip-preprocess', '-sp', action='store_true', help='Skip the preprocessing step.')
        parser.add_argument('--already-preprocessed', '-ap', action='store_true', help='Use this flag if the videos are already preprocessed.')
        parser.add_argument('--just-subtitles', '-js', action='store_true', help='Just add subtitles to video.')
        parser.add_argument('--skip-subtitles', '-ss', action='store_true', help='Skip the subtitles step.')
        parser.add_argument('--skip-jcut', '-sj', action='store_true', help='Skip the J-Cut step.')

        # Parse the arguments
        self.args = parser.parse_args()
    
    def preprocess_videos(self):
        """
        Preprocess the videos.
        """
        if self.args.just_subtitles: return
        if self.args.skip_preprocess: return 

        if self.args.already_preprocessed:
            self.preprocess_feat = PreprocessVideos(self.args.input)
            return

        self.preprocess_feat.preprocess_all_videos_in_folder()
    
    def determine_input_folder(self):
        """
        Determine the input folder.
        """
        if self.args.just_subtitles:
            self.input_folder = os.path.dirname(self.args.input)
            self.input_video = self.args.input
            return

        self.input_folder = self.preprocess_feat.preprocessed_folder if self.args.already_preprocessed else self.args.input

    def create_timeline(self):
        """
        Create the Timeline object.
        """
        if self.args.just_subtitles: return

        self.timeline = Timeline(self.input_folder)
    
    def concatenate_files(self):
        """
        Concatenate files.
        """
        if self.args.just_subtitles: return

        self.concatenate_feat = Concatenate(self.timeline, self.input_folder)
        self.concatenate_feat.concatenate_video_files()
        
    def remove_silence(self):
        """
        Remove silent parts.
        """
        if self.args.just_subtitles: return

        self.remove_silence_feat = RemoveSilence(self.timeline, self.input_folder)
        self.remove_silence_feat.remove_silence_from_videos()
    
    def jcut_timeline(self):
        """
        Apply J-Cut to the timeline.
        """
        if self.args.skip_jcut: return
        if self.args.just_subtitles: return

        self.jcut_feat = JCut(self.timeline)
        self.jcut_feat.jcut_timeline()
    
    def determine_subtitles_video(self):
        """
        Determine the video to add subtitles.
        """
        if self.args.just_subtitles:
            self.subtitles_video = self.input_video
            return

        self.subtitles_video = self.remove_silence_feat.preview_final_video
    
    def add_subtitles(self):
        """
        Add subtitles.
        """
        """
        NOTE:
            - Subtitles to a jcutted video is not implemented yet. To add subtitles to a jcutted video, you need to
              generate the final final video in the video editor and then run the program with the --just-subtitles flag.
        """
        if not self.args.skip_jcut: return
        if self.args.skip_subtitles: return

        if not self.args.just_subtitles:
            self.remove_silence_feat.generate_final_preview_video()

        self.generate_subtitles_feat = GenerateSubtitles(self.input_folder, self.subtitles_video)
        self.generate_subtitles_feat.generate_subtitles()
    
    def generate_fcpxml_file(self):
        """
        Create the FCPXML file.
        """
        if self.args.just_subtitles: return

        self.timeline.generate_fcpxml_file()
