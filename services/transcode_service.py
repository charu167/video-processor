import ffmpeg


class Transcode:
    def __init__(self) -> None:
        pass

    def convert_to_360p(self, input_path, output_path):
        ffmpeg.input(input_path).output(output_path, vf="scale=640:360").run()

    def convert_to_480p(self, input_path, output_path):
        ffmpeg.input(input_path).output(output_path, vf="scale=854:480").run()

    def convert_to_720p(self, input_path, output_path):
        ffmpeg.input(input_path).output(output_path, vf="scale=1280:720").run()

    def convert_to_1080p(self, input_path, output_path):
        ffmpeg.input(input_path).output(output_path, vf="scale=1920:1080").run()


import ffmpeg

class Transcode:
    def __init__(self) -> None:
        pass

    def convert_resolution(self, input_path: str, output_path: str, width: int, height: int) -> None:
        """
        Transcodes the input video to the specified width and height.
        
        :param input_path: Path to the input video
        :param output_path: Path for the transcoded output
        :param width: Target width
        :param height: Target height
        """
        ffmpeg.input(input_path).output(output_path, vf=f"scale={width}:{height}").run()
