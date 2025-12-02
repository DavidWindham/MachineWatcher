Basic Shelly smart-plug watcher.

Originally developed to remotely turn on/off and monitor a plug that drove an espresso machine. This data's fetched by an android app (not released) in order to call the plug, as well as monitor the power usage to figure out when the boiler has finished heating (current drops)

You'll need an .env file with the key "switch_url" e.g. ```switch_url=192.168.1.10``` if your switch's IP is 192.168.1.10.


To install and run the debug build with the following

0. Setup venv if you want with ```$ python -m venv venv``` and soruce it with ```$ source venv/bin/activate```
1. Install dependencies ```$ pip install -r requirements.txt```
2. Run with ```$ python main.py```

The flask app runs on main run, no need to export any env variables for that
Host it with something if you want, you could point this towards the open web, but as of time of the init commit, there's no security on this API.

## Docker Deployment on TrueNAS Scale

To deploy this application using Docker on TrueNAS Scale, follow these steps:

1. Build the Docker image:
   ```
   docker build . -t <app_name>:<version>
   ```

2. Save the image to a tar file:
   ```
   docker save -o <app_name>.tar <app_name>:<version>
   ```

3. Upload the `<app_name>.tar` file to an SMB shared folder on your NAS.

4. SSH into your TrueNAS Scale system and escalate to root privileges.

5. Navigate to the directory where you uploaded the tar file and load the image:
   ```
   docker load < <app_name>.tar
   ```

6. In the TrueNAS Scale web interface, go to Apps and update the version to the one you just uploaded.
