codeman
=================

Simple script to check out and update all the repositories from an organisation.
It uses the GitHub apis to identify all the repositories belonging to 
an organisation. It checks them out if not already on the destination directory, 
otherwise it checks out master on them and pulls the origin master.

setup
-----
Duplicate [conf/config.example.yaml](conf/config.example.yaml) in the same
directory to a config.yaml file.
Customise your organisation name, the local base directory, your GitHub user email,
and the personal token to be used with it.

