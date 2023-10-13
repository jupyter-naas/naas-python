import os
from rich.progress import Progress, SpinnerColumn, TextColumn
from naas_python.domains.space.adaptors.primary.utils import update_progress


def build_and_push_docker_image(
    registry_name: str,
    image: str = None,
    image_tag: str = "latest",
    dockerfile_path: str = "Dockerfile",
    docker_context: str = ".",
    skip_build: bool = False,
):
    """
    Build a Docker image and push it to a Docker registry.

    Args:
        registry_name (str): The name of the Docker registry to push the image to.
        image (str, optional): The name of the Docker image. Defaults to `None`.
        image_tag (str): The tag for the Docker image. Defaults to `latest`.
        dockerfile_path (str): The path to the Dockerfile. Not needed if `image` is provided. Defaults to `Dockerfile`.
        docker_context (str): The path to the Docker context. Defaults to `.`. Not needed if `image` is provided.
        skip_build (bool, optional): Whether to skip the build process. Defaults to False.
        mode (str, optional): The mode to determine how to display progress:
            - "plain": Print progress information as plain text.
            - "rich": Use rich progress bars for displaying progress. Defaults to "plain".

    Returns:
        None
    """

    image = image if image else f"naas-myspace-image:{image_tag}"

    # with Progress(
    #     SpinnerColumn(),
    #     TextColumn("[progress.description]{task.description}"),
    #     transient=True,
    # ) as progress:
    # build_task = progress.add_task("[cyan] Docker Image Build and Push...", total=1)
    # if not skip_build:
    #     update_progress(
    #         build_task, advance=0, description="Building Docker Image...", mode=mode
    #     )
    #     os.system(f"docker build -t {image} -f {dockerfile_path} {docker_context}")

    # update_progress(
    #     build_task, advance=0.5, description="Tagging Docker Image...", mode=mode
    # )
    # os.system(f"docker tag {image} {registry_name}:{image_tag}")

    # update_progress(
    #     build_task, advance=0.75, description="Pushing Docker Image...", mode=mode
    # )
    # os.system(f"docker push {registry_name}:{image_tag}")
