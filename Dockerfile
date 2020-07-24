FROM inqtel/coronaboard:base-latest
LABEL maintainer="JJ Ben-Joseph (jbenjoseph@iqt.org)" \
      description="This project contains a dashboard to forecast the COVID-19 outbreak. [Application Container]"
EXPOSE 8080
CMD uwsgi --http :8080 --module corona_dashboard.app:SERVER
COPY corona_dashboard /app/corona_dashboard
WORKDIR /app
