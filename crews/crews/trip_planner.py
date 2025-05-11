import os
from datetime import datetime
from functools import cached_property
from pathlib import Path

import jinja2
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import BraveSearchTool, FileReadTool, FileWriterTool
from pydantic import BaseModel, Field

from tools.list_dir_files import CustomDirectoryReadTool
from utils.utils import load_yaml


class TripPlannerCrewConfig(BaseModel):
    country: str = Field(description="Country to visit")
    output_dir: Path = Field(description="Directory to write the output file")
    current_season: str = Field(description="Current season (Spring, Summer, Fall, Winter)")
    city_details_dir: Path = Field(description="Directory to read the city details")


class TripPlannerCrew:
    def __init__(self, logs_dir: Path, config: TripPlannerCrewConfig):
        self._config = config
        self._prompts = load_yaml(Path(__file__).parent.parent / "prompts" / "trip_planner.yaml")
        self._logs_dir = logs_dir

    @cached_property
    def _llm(self) -> LLM:
        return LLM(
            model=os.environ["TRIP_PLANNER_MODEL"],
            max_tokens=8192,
            temperature=0.1,  # Slightly higher temperature for creative planning
            base_url=os.environ["TRIP_PLANNER_BASE_URL"],
            api_key=os.environ["TRIP_PLANNER_API_KEY"],
            timeout=180,
        )

    @cached_property
    def _agent(self) -> Agent:
        return Agent(
            role=self._render_prompt("agents.trip_planner.role"),
            goal=self._render_prompt("agents.trip_planner.goal"),
            backstory=self._render_prompt("agents.trip_planner.backstory"),
            llm=self._llm,
            max_iter=20,
            max_rpm=30,
            verbose=True,
            respect_context_window=True,
            tools=[
                BraveSearchTool(),
                FileWriterTool(),
                CustomDirectoryReadTool(),
                FileReadTool(),
            ],
        )

    @cached_property
    def _task(self) -> Task:
        return Task(
            name="trip_planner",
            description=self._render_prompt("tasks.trip_planner.description"),
            expected_output=self._render_prompt("tasks.trip_planner.expected_output"),
            agent=self._agent,
            output_file=f"{self._config.output_dir}/{self._config.country}_trip_plan.html",
        )

    @property
    def crew(self) -> Crew:
        log_file = self._logs_dir / f"trip_planner__{self._config.country}__{datetime.now().strftime('%H-%M-%S')}.json"

        return Crew(
            agents=[self._agent],
            tasks=[self._task],
            process=Process.sequential,
            output_log_file=str(log_file),
            verbose=True,
        )

    def _render_prompt(self, prompt_name: str) -> str:
        keys = prompt_name.split(".")
        prompt_value = self._prompts

        try:
            for key in keys:
                prompt_value = prompt_value[key]
        except (KeyError, TypeError):
            raise ValueError(f"Prompt {prompt_name} not found in prompts")

        if not isinstance(prompt_value, str):
            raise ValueError(f"Prompt {prompt_name} is not a string")

        template_vars = {
            "country": self._config.country,
            "output_dir": self._config.output_dir,
            "current_season": self._config.current_season,
            "city_details_dir": self._config.city_details_dir,
        }

        return jinja2.Template(prompt_value).render(**template_vars)
