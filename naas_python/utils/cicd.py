from jinja2 import Environment, FileSystemLoader


class Job:
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps


class Workflow:
    def __init__(self, name, jobs):
        self.name = name
        self.jobs = jobs

    def generate_yaml(self, template_path):
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template(template_path)
        return template.render(workflow=self)


class Pipeline:
    def __init__(self, name):
        self.name = name
        self.extra_steps = []
        self._workflow_template_path = "workflow_template.j2"

    def add_job(self, name, steps):
        job = Job(name, steps)
        self.extra_steps.append(job)

    def _generate_base_steps(self):
        # Checkout step Job
        _checkout_step = Job(
            name="Checkout Code",
            steps=["uses: actions/checkout@v2"],
        )
        _install_dependencies_step = Job(
            name="Install Dependencies",
            steps=["run: pip install -r requirements.txt"],
        )
        return [_checkout_step, _install_dependencies_step]

    def render(self):
        # Create a list to store all jobs (base and optional steps)
        all_jobs = [*self._generate_base_steps(), *self.extra_steps]

        # Create a Workflow with all jobs
        workflow = Workflow(
            name=self.name,
            jobs=all_jobs,
        )

        # Generate the YAML content using the template
        return workflow.generate_yaml(self._workflow_template_path)
