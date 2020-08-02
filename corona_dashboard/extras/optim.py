from sigopt import Connection
from sigopt.exception import ApiException
from corona_dashboard.forecast import forecast, get_counties_data, HYPERPARAMETERS

def create_experiment(apikey):
    conn = Connection(client_token=apikey)
    experiment = conn.experiments().create(
        name="Coronaboard -- AutoARIMA",
        parameters=[
            dict(
                name="max_p",
                bounds=dict(
                    min=14,
                    max=30
                ),
                type="int"
            ),
            dict(
                name="max_q",
                bounds=dict(
                    min=14,
                    max=30
                ),
                type="int"
            ),
            dict(
                name="max_d",
                bounds=dict(
                    min=14,
                    max=30
                ),
                type="int"
            ),
            dict(
                name="maxiter",
                bounds=dict(
                    min=140,
                    max=360
                ),
                type="int"
            ),
            dict(
                name="method",
                categorical_values=[
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
                    )
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
            ),
            dict(
                name="information_criterion",
                categorical_values=[
                    dict(
                        name="aic"
                    ),
                    dict(
                        name="bic"
                    ),
                    dict(
                        name="hqic"
                    ),
                    dict(
                        name="oob"
                    )
                ],
                type="categorical"
            )
        ],
        metrics=[dict(
            name="SMAPE",
            objective="minimize"
        )],
        metadata=dict(
            template="dashboard"
        ),
        observation_budget=400,
        parallel_bandwidth=12,
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
            conn.experiments(exp_id).suggestions().delete()
            suggestion = conn.experiments(exp_id).suggestions().create()
        assignments = suggestion.assignments
        print(f"Hyperpameters: {assignments}")
        try:
            _, _, metrics = forecast(us_counties, log_metrics=True, hp={**HYPERPARAMETERS, **assignments})
            mean = sum(metrics.values()) / len(metrics)
        except:
            print("Invalid hyperparameter combination!")
            mean = 0.9999
        finally:
            conn.experiments(exp_id).observations().create(
                suggestion=suggestion.id,
                value=mean
            )
