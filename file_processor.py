"""File Processor Module"""
import subprocess
import os
import json
import logging
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class FileProcessor:
    SUPPORTED_FORMATS = {'.mp4', '.mkv', '.mov', '.webm', '.avi', '.flv', '.wmv'}
    
    def __init__(self):
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            logger.info("FFmpeg found and available")
        except:
            raise RuntimeError("FFmpeg not found")
    
    def extract_metadata(self, file_path: str) -> Dict:
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            probe_data = json.loads(result.stdout)
            metadata = self._parse_probe_data(probe_data, file_path)
            logger.info(f"Metadata extracted for {file_path}")
            return metadata
        except Exception as e:
            logger.error(f"Metadata extraction error: {str(e)}")
            return {"duration": 0, "file_size_mb": os.path.getsize(file_path) / (1024 * 1024), "resolution": "Unknown", "codec": "Unknown"}
    
    def _parse_probe_data(self, probe_data: dict, file_path: str) -> Dict:
        metadata = {"file_size_mb": os.path.getsize(file_path) / (1024 * 1024), "duration": 0, "resolution": "Unknown", "codec": "Unknown"}
        
        if 'format' in probe_data:
            metadata['duration'] = float(probe_data['format'].get('duration', 0))
        
        if 'streams' in probe_data:
            for stream in probe_data['streams']:
                if stream.get('codec_type') == 'video':
                    metadata['codec'] = stream.get('codec_name', 'Unknown').upper()
                    height = stream.get('height', 0)
                    if height >= 2160:
                        metadata['resolution'] = '4K'
                    elif height >= 1440:
                        metadata['resolution'] = '1440p'
                    elif height >= 1080:
                        metadata['resolution'] = '1080p'
                    elif height >= 720:
                        metadata['resolution'] = '720p'
        
        return metadata
    
    def convert_to_mkv(self, input_path: str):
        output_path = input_path.replace('.mp4', '.mkv').replace('.mov', '.mkv').replace('.avi', '.mkv')
        if output_path == input_path:
            output_path = input_path + '.mkv'
        
        try:
            logger.info(f"Converting {input_path} to MKV...")
            cmd = ['ffmpeg', '-i', input_path, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-y', output_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"MKV conversion successful: {output_path}")
                return output_path
            else:
                logger.error(f"MKV conversion failed")
                return input_path
        except Exception as e:
            logger.error(f"MKV conversion error: {str(e)}")
            return input_path
    
    def get_file_size_mb(self, file_path: str) -> float:
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def validate_video_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS

