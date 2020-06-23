from fire import Fire

class Controller:
    def up(self, debug=False):
        """
        Run the web application and build the cache if needed.
        """
        import corona_dashboard.app as app

        app.main(debug)
    
    def cache(self):
        """
        Just cache the data. It doesn't run the web app.
        """
        from corona_dashboard.forecast import process_data
        
        process_data()


def main():
    Fire(Controller)
