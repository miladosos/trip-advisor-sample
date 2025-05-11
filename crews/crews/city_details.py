import os
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import List

import jinja2
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import BraveSearchTool, FileWriterTool, SeleniumScrapingTool, FirecrawlScrapeWebsiteTool
from pydantic import BaseModel, Field

from utils.utils import load_yaml

class CityDetailsCrewConfig(BaseModel):
    cities: List[str] = Field(description="Cities to visit")
    output_dir: Path = Field(description="Directory to write the output file")
    current_season: str = Field(description="Current season (Spring, Summer, Fall, Winter)")


class CityDetailsCrew:
    def __init__(self, logs_dir: Path, config: CityDetailsCrewConfig):
        self._config = config
        self._prompts = load_yaml(Path(__file__).parent.parent / "prompts" / "city_details.yaml")

        self._logs_dir = logs_dir

    @cached_property
    def _llm(self) -> LLM:
        return LLM(
            model=os.environ["CITY_DETAILS_MODEL"],
            max_tokens=8192,
            temperature=0.0,
            base_url=os.environ["CITY_DETAILS_BASE_URL"],
            api_key=os.environ["CITY_DETAILS_API_KEY"],
            timeout=180,
        )

    @cached_property
    def _agent(self) -> Agent:
        return Agent(
            role=self._render_prompt("agents.city_details.role"),
            goal=self._render_prompt("agents.city_details.goal"),
            backstory=self._render_prompt("agents.city_details.backstory"),
            llm=self._llm,
            max_iter=10,
            max_rpm=30,
            verbose=True,
            allow_code_execution=False,
            respect_context_window=True,
            tools=[
                SeleniumScrapingTool(),
                # FirecrawlScrapeWebsiteTool(),
                BraveSearchTool(),
                FileWriterTool(),
            ],
        )

    def _create_task(self, city: str) -> Task:
        return Task(
            name="city_details",
            description=self._render_prompt("tasks.city_details.description", city=city),
            expected_output=self._render_prompt("tasks.city_details.expected_output", city=city),
            agent=self._agent,
        )

    @property
    def crew(self) -> Crew:
        log_file = self._logs_dir / f"city_details__{datetime.now().strftime('%H-%M-%S')}.json"
        tasks = [self._create_task(city) for city in self._config.cities]

        return Crew(
            agents=[self._agent],
            tasks=tasks,
            process=Process.sequential,
            output_log_file=str(log_file),
            verbose=True,
        )

    def _render_prompt(self, prompt_name: str, **kwargs) -> str:
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
            "output_dir": self._config.output_dir,
            "current_season": self._config.current_season,
            **kwargs,
        }

        return jinja2.Template(prompt_value).render(**template_vars)
