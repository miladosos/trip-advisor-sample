import os
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import List

import jinja2
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import BraveSearchTool, FirecrawlScrapeWebsiteTool
from pydantic import BaseModel, Field


from utils.utils import load_yaml


class TripOptionsCrewConfig(BaseModel):
    country: str = Field(description="Country to visit")
    current_season: str = Field(description="Current season (Spring, Summer, Fall, Winter)")


class TripOptionsTaskOutput(BaseModel):
    cities: List[str] = Field(description="List of cities to visit")


class TripOptionsCrew:
    def __init__(self, logs_dir: Path, config: TripOptionsCrewConfig):
        self._config = config
        self._prompts = load_yaml(Path(__file__).parent.parent / "prompts" / "trip_options.yaml")

        self._logs_dir = logs_dir

    @cached_property
    def _llm(self) -> LLM:
        return LLM(
            model=os.environ["TRIP_OPTIONS_MODEL"],
            max_tokens=8192,
            temperature=0.0,
            base_url=os.environ["TRIP_OPTIONS_BASE_URL"],
            api_key=os.environ["TRIP_OPTIONS_API_KEY"],
            timeout=180,
        )

    @cached_property
    def _agent(self) -> Agent:
        return Agent(
            role=self._render_prompt("agents.trip_options.role"),
            goal=self._render_prompt("agents.trip_options.goal"),
            backstory=self._render_prompt("agents.trip_options.backstory"),
            llm=self._llm,
            max_iter=50,
            max_rpm=30,
            verbose=True,
            allow_code_execution=False,
            respect_context_window=True,
            tools=[
                BraveSearchTool(),
                FirecrawlScrapeWebsiteTool(),
            ],
        )

    @cached_property
    def _task(self) -> Task:
        return Task(
            name="trip_options",
            description=self._render_prompt("tasks.trip_options.description"),
            expected_output=self._render_prompt("tasks.trip_options.expected_output"),
            agent=self._agent,
            output_pydantic=TripOptionsTaskOutput,
        )

    @property
    def crew(self) -> Crew:
        log_file = self._logs_dir / f"trip_options__{self._config.country}__{datetime.now().strftime('%H-%M-%S')}.json"

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
            "current_season": self._config.current_season,
        }

        return jinja2.Template(prompt_value).render(**template_vars)
