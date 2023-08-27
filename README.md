# Zoneminder Camera Motion Detection
Use your cameras' motion detection engine instead of burning server cycles.

ZoneMinder has some nice motion detection features, they are clever and very configurable but there are two big issues.

First, it takes time to understand and set up a working system, and if you are porting an already configured system from other platforms then you may not wish to spend this time reoptimising.

Second, it doesn't scale. If you have to buy/rent or otherwise sacrifice 10 times the processing power of the camera hardware on a server each time you add a camera then that's a bad system solution. Hardware acceleration built into the cameras will never be as comprehensive as a complex server side analysis system but for 90% of situations it's enough to satisfy the application.

This script is a nice, simple and adaptable solution to bridging between the ZoneMinder app and your cameras' motion detection engine. It uses the zmtrigger.pl facility which needs to be enabled on the settings page of the ZoneMinder app. Other than that you only need to set a few things in the script to customise it for your set up.

This script is currently set up for Reolink cameras. Other manufacturers have slightly different commands or API systems and so you will need to research how your camera can be interogated for the motion result. I've left the coding style as very open and avoided density  which should make it quicker to customise.



