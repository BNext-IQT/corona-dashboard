from sigopt import Connection
from sigopt.exception import ApiException
from corona_dashboard.forecast import forecast, get_counties_data, Hyperparameters

def create_experiment(apikey):
    conn = Connection(client_token=apikey)
    experiment = conn.experiments().create(
        name="Coronaboard -- AutoARIMA",
        parameters=[
            dict(
                name="start_p",
                bounds=dict(
                    min=2,
                    max=3
                ),
                type="int"
            ),
            dict(
                name="max_p",
                bounds=dict(
                    min=3,
                    max=18
                ),
                type="int"
            ),
            dict(
                name="start_q",
                bounds=dict(
                    min=2,
                    max=3
                ),
                type="int"
            ),
            dict(
                name="max_q",
                bounds=dict(
                    min=3,
                    max=18
                ),
                type="int"
            ),
            dict(
                name="max_d",
                bounds=dict(
                    min=2,
                    max=5
                ),
                type="int"
            ),
            dict(
                name="maxiter",
                bounds=dict(
                    min=20,
                    max=200
                ),
                type="int"
            ),
            dict(
                name="method",
                categorical_values=[
                    dict(
                        name="newton"
                    ),
                    dict(
                        name="nm"
                    ),
                    dict(
                        name="bfgs"
                    ),
                    dict(
                        name="lbfgs"
                    ),
                    dict(
                        name="powell"
                    ),
                    dict(
                        name="cg"
                    ),
                    dict(
                        name="ncg"
                    ),
                    dict(
                        name="basinhopping"
                    ),
                ],
                type="categorical"
            ),
            dict(
                name="scoring",
                categorical_values=[
                    dict(
                        name="mse"
                    ),
                    dict(
                        name="mae"
                    )
                ],
                type="categorical"
            )
        ],
        metrics=[dict(
            name="SMAPE",
            objective="minimize",
            threshold=None
        )],
        metadata=dict(
            template="dashboard"
        ),
        observation_budget=300,
        parallel_bandwidth=10,
        project="dashboard-dev"
        
    )
    return experiment.id

def continue_experiment(apikey, exp_id):
    us_counties = get_counties_data()
    conn = Connection(client_token=apikey)
    experiment = conn.experiments(exp_id).fetch()
    for _ in range(experiment.observation_budget):
        try:
            suggestion = conn.experiments(exp_id).suggestions().create()
        except ApiException:
            suggestion = conn.experiments(exp_id).suggestions().delete()
            suggestion = conn.experiments(exp_id).suggestions().create()
        assignments = Hyperparameters.from_dict(suggestion.assignments)
        print(f"Hyperpameters: {assignments.__dict__}")
        try:
            _, _, metrics = forecast(us_counties, log_metrics=True, hp=assignments)
            mean = sum(metrics.values()) / len(metrics)
        except:
            mean = 0.9999
        finally:
            conn.experiments(exp_id).observations().create(
                suggestion=suggestion.id,
                value=mean
            )
