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
