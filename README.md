Basic Shelly smart-plug watcher.

Originally developed to remotely turn on/off and monitor a plug that drove an espresso machine. This data's fetched by an android app (not released) in order to call the plug, as well as monitor the power usage to figure out when the boiler has finished heating (current drops)

You'll need an .env file with the key "switch_url" e.g. ```switch_url=192.168.1.10``` if your switch's IP is 192.168.1.10.


To install and run the debug build with the following

0. Setup venv if you want with ```$ python -m venv venv```
1. Install dependencies ```$ pip install -r requirements.txt```
2. Run with ```$ python main.py```

The flask app runs on main run, no need to export any env variables for that
Host it with something if you want, you could point this towards the open web, but as of time of the init commit, there's no security on this API.
