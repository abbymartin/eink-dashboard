# E-ink Weather Dashboard

Display for modded Kindle e-ink tablet showing daily weather forecast and train arrival times. Made this to experiment with development for my [jailbroken kindle](https://kindlemodding.org/jailbreaking/). The display updates once per minute after fetching an image from a server hosted locally on a Raspberry Pi.

## Server

A custom Flask server retrieves weather forecast data and train arrival time predictions from public APIs ([Open Meteo](https://open-meteo.com/) and [MBTA v3](https://www.mbta.com/developers/v3-api)) to update the fields in the dashboard template stored in /server/static/template.svg. Since this Kindle model can only display greyscale images size 600x800px, the svg2png.py script converts the updates svg into a png image. The dashboard image is served via the /dash endpoint on the server and updated once every 20 seconds.

## Kindle

The Kindle tablet runs /kindle/dash.sh as a [scriptlet](https://kindlemodding.org/kindle-dev/scriptlets.html) and retrieves the image from the server once per minute and displays using the [fbink](https://github.com/NiLuJe/FBInk) tool. The tablet must be plugged in to avoid switching to the screensaver after a few minutes of inactivity.

![eink dashboard image example](https://github.com/abbymartin/eink-dashboard/blob/main/server/static/dash.png)

![eink dashboard on physical tablet](https://github.com/abbymartin/eink-dashboard/blob/main/kindle_dashboard.jpg)
