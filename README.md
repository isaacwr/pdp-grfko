# PDP / GRFKO / Working Title

First, a quick overview of what is here. This is a rudimentary implementation for a Google App Engine web-based authorization and access portal that includes functionality for creating user data such as profiles, projects, and links to Overlayers maps. Currently the app is running at http://isaactest-999.appspot.com

This project has two main objectives: to move imagery and analytics deliveries away from GME and onto Maps API, and to simplify and streamline the process for preparing and delivering data.

#####TL;DR: Couldn't load private GeoJson files, ran out of time.

#####Using the app
1. Click Login
2. Enter auth code. '221293' and '1234' are currently set up; you will only have to do this once.
2. To create new data, either go to '/admin' or go to the developers console and create new entities in the datastore

#####Design story
Rather than design from scratch, we used an app built by the Candid Resale team in New York, called Overlayers. Overlayers is a single web page app that has simple button functinality for adding layers and saving the map. All data requests are made through Maps API from cient side JavaScript. The challeges we faced the Overlayers app were: (1) restricting access to the maps, (2) having private data, and (3) displaying more than one image and analysis bundle per map.

#####Access to Overlayers
The first problem remains only partially solved. We built an authentication portal to restrict access to the direct links to the Overlayers maps. However, the maps are hosted at public URLs, and even though they are long and random, it feels undercooked to hide them in such a way. I would prefer a more sophisticated access system, though that won't happen unless we integrate a modified copy of Overlayers with an authentication / authorization portal.

#####Private Data
Private data is a stumbling block. Although hosting and serving private image layers is rather simple, we haven't had success with private vector layers. The image layers are added by specifying a web address pointing at the root of a image tile pyramid. Because all of our data is stored on GCS, we can keep the images ACL'd and use a GCS specific URL that uses cookies to detirmine which Google Account is trying to access the data and check that against the control list. That URL is https://storage.cloud.google.com/BUCKET/PATH/TO/IMAGE/{z}/{x}/{y}.png. This means that we have private images protected by an ACL wall that can only be loaded by authorized users. This is what we want, but we couldn't replicate this for vector layers.

The analytics layers are Maps API Data layers, which take GeoJson files as input. When we try to load a GeoJson file, the server responds with an Error 405, saying that no 'Access-Control-Allow-Origin' is present on the response header. This looks like a CORS issue, but so far as we can tell, the CORS definition is correct for the GCS bucket where our data is stored. For some reason we could not load the GeoJson data from GCS, and so we thought that maybe using the cookie based auth was the issue. So we worked on using an OAuth2 access token instead. However, this resulted in the same error. This is the template URL we used for the access token: https://console.developers.google.com/m/cloudstorage/b/BUCKET/o/FILE, and then we put an 'Authorization: Bearer TOKEN' header on the request. The access token tests were done on a separate test bed and not through the Overlayers app. It's worth noting that we can download the GeoJson file by specifying both the cookies based (storage.cloud.google) and OAuth2 based (console.developers.google) URLs in a browser window. 

#####Overlayers interface
The restriction of one image and analytics pair was done by design for Overlayers. The use case for the Candid Resale team is different than for our pilot deliveries, and so this is only an issue for us, and another reason why starting fresh might have been benificial. Because we could not load private GeoJson files, we never actually used this to deliver data and so we never had to make a decision about the rigid nature of Overlayers. Theoretically we could have a link for each delivery for each location in something of a grid with each location being a column and each row being a delivery date, or we could keep a single link for each location and then keep updating that with extra layers. The problem with adding too many layers to a single map is that the layers are controlled with a rudimentary single level toggle switches, so it is impossible to group them or make them heirarichacal.

It might make more sense to make this look and act like (actually be?) a dashbaord. The Skybox/Google Satellites/Unnamed product is moving towards dashboards so it makes sense to create a unified customer experience. Also I think a dashboard style interface is more intuitive for this type of delivery. Another reason why it might have made more sense to build ground up or borrow functionality from the WIV and hide it all behind a login curtain.

#####Where to from here
Moving forward there are still a few things. The first thing that needs to be done is to decide whether we are going to actually make deliveries using Overlayers, or if we are going to make a dashboard out of it, or something else. If we are going to use Overlayers as a base, we first need to solve the private GeoJson file problem, and then we need to integrate the login system with the map system so everything is contained in one site. Part of that integration would involve hiding the AddLayer and Save&GetURL buttons from users, and then create a complete front end design.

A lot of this information is written in a small slide deck called 'Pilot Delivery Project Update 8/7'. Andy Hock should have these slides. We spent two weeks working on the private GeoJson issue with no success. I've contacted the author of the Overlayers app, Sean Wohltmann, and he wasn't able to solve it with his availible bandwith, and he referred me to two solutions engineers, neither of which have had time. However, the feeling I get working on this is that the solution either doesn't exist on purporse or is trivially simple and I don't see it.

#####Also
There is a Cloud Platfom project called isaactest-999 that has all of the data and is hosting the app.
