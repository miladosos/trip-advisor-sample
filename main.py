from datetime import datetime
import logging
from pathlib import Path

from crews.flow import TripFlow, TripFlowConfig

from dotenv import load_dotenv
from utils.custom_logger import CustomLogger
from utils.event_listener import LLMEventListener

load_dotenv()

llm_event_listener = LLMEventListener()

if __name__ == "__main__":
    
    country = "Finland"
    current_season = "Spring"

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs") / f"{country}__{current_season}___{datetime.now().strftime('%Y-%m-%d')}"
    logs_dir.mkdir(parents=True, exist_ok=True)

    CustomLogger.init(logs_dir, file_level=logging.INFO, console_level=logging.WARNING)

    flow = TripFlow(
        logs_dir=logs_dir,
        config=TripFlowConfig(
            country=country,
            current_season=current_season,
        ),
    )

    flow.kickoff()
