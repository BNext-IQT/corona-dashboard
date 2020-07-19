import importlib
from fire import Fire
from corona_dashboard.forecast import Hyperparameters

class Controller:
    def up(self, debug=False):
        """
        Run the web application and build the cache if needed.
        """
        import corona_dashboard.app as app

        app.main(debug)
    
    def cache(self, hp=None):
        """
        Just cache the data. It doesn't run the web app.
        """
        from corona_dashboard.forecast import process_data
        
        if hp:
            print(f"Hyperparameters: {hp}")
            hp = Hyperparameters.from_dict(hp)
            process_data(hp=hp)
        else:
            process_data()

    if importlib.util.find_spec('sigopt'):
        def new_experiment(self, apikey):
            """
            Create a new SigOpt experiment.
            """
            from corona_dashboard.extras.optim import create_experiment

            print(create_experiment(apikey))
        
        def continue_experiment(self, apikey, exp_id):
            """
            Continue running a SigOpt experiment.
            """
            from corona_dashboard.extras.optim import continue_experiment

            continue_experiment(apikey, exp_id)

def main():
    Fire(Controller)
