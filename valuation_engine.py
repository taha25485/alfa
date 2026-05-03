"""Valuation Engine Module"""
import logging

logger = logging.getLogger(__name__)

class ValuationEngine:
    GAME_DATABASE = {
        "elden ring": 950, "zelda": 920, "baldur's gate 3": 900,
        "minecraft": 1000, "fortnite": 950, "valorant": 900,
        "league of legends": 950, "gta 6": 950, "skyrim": 950,
        "witcher 3": 920, "dark souls": 900,
    }
    
    def __init__(self):
        self.max_score = 1000
    
    def score_content(self, game_name: str, metadata: dict) -> int:
        """Score content from metadata dict"""
        return self.calculate_score(
            duration=metadata.get('duration', 0),
            file_size_mb=metadata.get('file_size_mb', 0),
            resolution=metadata.get('resolution', 'Unknown'),
            codec=metadata.get('codec', 'Unknown'),
            game_name=game_name
        )
    
    def calculate_score(self, duration: float, file_size_mb: float, resolution: str, codec: str, game_name: str, existing_sales: int = 0, popularity_rating: float = 0.5) -> int:
        try:
            score = 0
            
            duration_score = min(150, int((duration / 7200) * 150))
            score += duration_score
            logger.info(f"Duration score: {duration_score}/150")
            
            file_size_score = min(150, int((file_size_mb / 10240) * 150))
            score += file_size_score
            logger.info(f"File size score: {file_size_score}/150")
            
            resolution_score = self._score_resolution(resolution)
            score += resolution_score
            logger.info(f"Resolution score: {resolution_score}/200")
            
            codec_score = self._score_codec(codec)
            score += codec_score
            logger.info(f"Codec score: {codec_score}/100")
            
            game_score = self._score_game_popularity(game_name)
            score += game_score
            logger.info(f"Game score: {game_score}/200")
            
            sales_score = min(200, int((existing_sales / 100) * 200))
            score += sales_score
            
            popularity_bonus = int(popularity_rating * 200)
            final_score = min(self.max_score, score + popularity_bonus)
            
            logger.info(f"Final score: {final_score}/1000")
            return final_score
        except Exception as e:
            logger.error(f"Score error: {e}")
            return 500
    
    def _score_resolution(self, resolution: str) -> int:
        r = resolution.lower()
        if "4k" in r or "2160" in r:
            return 200
        elif "1440" in r:
            return 150
        elif "1080" in r:
            return 100
        elif "720" in r:
            return 50
        return 25
    
    def _score_codec(self, codec: str) -> int:
        c = codec.lower() if codec else "unknown"
        if "hevc" in c or "h265" in c:
            return 100
        elif "av1" in c:
            return 95
        elif "h264" in c or "avc" in c:
            return 50
        elif "vp9" in c:
            return 75
        return 25
    
    def _score_game_popularity(self, game_name: str) -> int:
        g = game_name.lower().strip()
        for key, pop in self.GAME_DATABASE.items():
            if key in g or g in key:
                return int((pop / 1000) * 200)
        return 80
    
    def estimate_token_reward(self, score: int) -> float:
        return (score / 1000) * 1_000_000

