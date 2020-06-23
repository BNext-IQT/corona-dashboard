from fire import Fire
import corona_dashboard.app as app
from corona_dashboard.forecast import process_data

class Controller:
    def up(self, debug=False):
        """
        Run the web application and build the cache if needed.
        """
        app.main(debug)
    
    def cache(self):
        """
        Just cache the data. It doesn't run the web app.
        """
        process_data()


def main():
    Fire(Controller)
