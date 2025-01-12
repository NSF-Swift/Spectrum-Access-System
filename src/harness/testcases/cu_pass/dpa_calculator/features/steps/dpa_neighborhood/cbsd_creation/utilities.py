from testcases.cu_pass.dpa_calculator.features.steps.dpa_neighborhood.cbsd_creation.common_steps.cbsd_creation import \
    ContextCbsdCreation
from testcases.cu_pass.dpa_calculator.features.steps.dpa_neighborhood.environment.contexts.context_cbsd_deployment_options import \
    get_current_cbsd_deployment_options

ARBITRARY_LARGE_POPULATION = 1000000


def set_large_simulation_population(context: ContextCbsdCreation) -> None:
    cbsd_deployment_options = get_current_cbsd_deployment_options(context=context)
    cbsd_deployment_options.population_override = ARBITRARY_LARGE_POPULATION
