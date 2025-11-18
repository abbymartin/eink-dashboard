# E-ink Weather Dashboard

Weather forecast display for modded Kindle e-ink tablet. Experimenting with developing for my [jailbroken kindle](https://kindlemodding.org/jailbreaking/). Custom Flask server updates dashboard images based on weather and MBTA transit API. Since this Kindle model requires 600x800px png/jpg, the image is created by modifying an svg template and converting to png using ImageMagick. Kindle runs bash script to fetch new image from server every minute and update display with weather forecast and predicted train times for a specific station.

![eink dashboard showing weather and train predictions](https://github.com/abbymartin/eink-dashboard/blob/main/server/static/dash.png)
