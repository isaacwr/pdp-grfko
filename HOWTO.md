#HOWTO.md

###Overview
All of the user data (not the imagery and analytics) is stored in the Datastore, currently the datastore for isaactest-999. There are three types of entites that we store, a KnownUser class, which keeps track of a user and which pilot project they are associated with, a PilotProject class, which keeps track of a unique ID that a user has to enter in order to gain access to a project, and then a Map class, which store information about which pilot project they belong to, which location they are, and the link to an Overlayers page.

#####New User
First, a new users access the site and clicks 'Login'. If they are not already logged in, it will take  them to a Google Accounds login page. Once they are logged in for the first time it will bring them to a page with a link for creating a new Pilot Project and entering an auth ID. The link for a new pilot project is there for the special case when no pilot projects already exists. Optimally the user would only see the Authentication ID input box. The input for the auth ID will then link the users account with a pilot project (for instance '1234' links to the project 'Project1-hosted'). Once the user inputs an auth ID, a KnownUser entity is automatically created using their UserID as reference. This way, whenever the user logs in again, she will be brought directly to the home page for her pilot project.

#####The Home Page
The user is then brought to the home page. This page has basic information about what project and user is being served, and then will have a link for every Map entity associated with the pilot project.

#####Creating new Maps
There are two ways to make a Map entity. The first is go to http://isaactest-999.appspot.com/admin and click 'new Map', or to go to the Developers Console and click Storage > Datastore > Query and click 'Create New Entity' and select 'Map'. The Map entity will have a link to an Overlayers page, so at this point the Overlayers map should be created and the short link saved and input into the Map entity. Populating data for a pilot project consists of creating more and more Maps or editing the existing ones. 

#####Also
The only way to delete an entity is through the Developers Console graphical interface.