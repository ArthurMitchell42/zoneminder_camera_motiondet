# Zoneminder Camera Motion Detection
Use your cameras' motion detection engine instead of burning server cycles.

ZoneMinder has some nice motion detection features, they are clever and very configurable but there are two big issues.

First, it takes time to understand and set up a working system, and if you are porting an already configured system from other platforms then you may not wish to spend this time reoptimising.

Second, it doesn't scale. If you have to buy/rent or otherwise sacrifice 10 times the processing power of the camera hardware on a server each time you add a camera then that's a bad system solution. Hardware acceleration built into the cameras will never be as comprehensive as a complex server side analysis system but for 90% of situations it's enough to satisfy the application.

This script is a nice, simple and adaptable solution to bridging between the ZoneMinder app and your cameras' motion detection engine. It uses the zmtrigger.pl facility which needs to be enabled on the settings page of the ZoneMinder app. Other than that you only need to set a few things in the script to customise it for your set up.

It supports multiple cameras which can be defined in the list at the top of the file. Each camera can have it's own parameters to support multiple vendors in your instalation.

This script is currently set up for Reolink cameras. Other manufacturers have slightly different commands or API systems and so you will need to research how your camera can be interogated for the motion result. I've left the coding style as very open and avoided density  which should make it quicker to customise.

You can run this sript either on the ZoneMinder machine/VM or on another machine all together. Set the server address near the top of the file. If you run it on the ZoneMinder server then I suggest you add it to the startup process by editing crontab (instructions on how to do this are in the script)

I run ZoneMinder in a Proxmox VM and the script is included on that VM. If you have issues customising the system for your cameras then set the log debug level to DEBUG to get more information.


