"""
Multi-modal model for generating images using OpenAI's DALL-E model.
"""

import os

from openai import Client, OpenAIError
from requests import get

from readmeai.cli.options import ImageOptions
from readmeai.config.settings import ConfigLoader
from readmeai.core.logger import Logger


class DalleHandler:
    """Generates and downloads images using OpenAI's DALL-E model."""

    def __init__(self, config: ConfigLoader) -> None:
        """Initialize the ImageGenerator class."""
        self.client = Client(api_key=os.getenv("OPENAI_API_KEY"))
        self.conf = config
        self._logger = Logger(__name__)
        self._model_settings()

    def _model_settings(self) -> None:
        """Initializes the DALL-E settings."""
        self.model = "dall-e-3"
        self.size = "1792x1024"
        self.quality = "standard"
        self.n = 1

    def _build_payload(self) -> str:
        """Formats the prompt string using configuration data."""
        return {
            "prompt": self.conf.prompts["prompts"]["logo"].format(
                project_name=self.conf.config.git.name,
                project_slogan=self.conf.config.md.slogan,
            ),
            "model": self.model,
            "size": self.size,
            "quality": self.quality,
            "n": self.n,
        }

    def run(self) -> str:
        """Generates an image and returns its URL."""
        try:
            payload = self._build_payload()
            response = self.client.images.generate(**payload)
            if response is not None:
                return response.data[0].url
            else:
                self._logger.error(
                    f"Failed to generate {self.model.upper()} image: {response}"
                )
                return ImageOptions.BLUE.value

        except (Exception, OpenAIError) as exc:
            self._logger.error(
                f"{self.model.upper()} image generation error: {exc}"
            )
            return ImageOptions.BLUE.value

    def download(self, image_url) -> str:
        """Downloads an image from the given URL."""
        filename = f"{self.conf.config.git.name}.png"
        try:
            response = get(image_url)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                return filename
            else:
                self._logger.error(
                    f"Failed to download image: {response.status_code}"
                )
                return ImageOptions.BLUE.value

        except Exception as exc:
            self._logger.error(f"Failed to download image: {exc}")
            return ImageOptions.BLUE.value
