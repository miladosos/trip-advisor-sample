from pathlib import Path

from crewai import CrewOutput
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

from .crews import CityDetailsCrew, CityDetailsCrewConfig, TripOptionsCrew, TripOptionsCrewConfig,TripPlannerCrew, TripOptionsTaskOutput, TripPlannerCrewConfig


class TripFlowConfig(BaseModel):
    country: str = Field(description="Country to visit")
    current_season: str = Field(description="Current season (Spring, Summer, Fall, Winter)")


class TripFlow(Flow):
    def __init__(self, logs_dir: Path, config: TripFlowConfig, *args, **kwargs):
        self._config = config
        self._logs_dir = logs_dir

        self._city_details_dir = logs_dir / "city_details"
        self._city_details_dir.mkdir(parents=True, exist_ok=True)

        super().__init__(*args, **kwargs)

    @start()
    def start(self):
        trip_options_crew = TripOptionsCrew(
            logs_dir=self._logs_dir,
            config=TripOptionsCrewConfig(
                country=self._config.country,
                current_season=self._config.current_season,
            ),
        )

        crew_output: CrewOutput = trip_options_crew.crew.kickoff()
        print(crew_output.tasks_output)

        return crew_output.tasks_output[0].pydantic

    @listen(start)
    def trip_options(self, city_options: TripOptionsTaskOutput):
        city_details_crew = CityDetailsCrew(
            logs_dir=self._logs_dir,
            config=CityDetailsCrewConfig(
                cities=city_options.cities,
                current_season=self._config.current_season,
                output_dir=self._city_details_dir,
            ),
        )

        city_details_crew.crew.kickoff()

    @listen(trip_options)
    def trip_planner(self):
        trip_planner_crew = TripPlannerCrew(
            logs_dir=self._logs_dir,
            config=TripPlannerCrewConfig(
                country=self._config.country,
                current_season=self._config.current_season,
                output_dir=self._city_details_dir,
                city_details_dir=self._city_details_dir,
            ),
        )

        trip_planner_crew.crew.kickoff()
