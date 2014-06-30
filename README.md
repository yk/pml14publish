# PML Image Summarization

## Requirements
I used scipy (incl. numpy) and flickr\_api, both should be available via pip

[Scipy](http://www.scipy.org/)
[flickr\_api](https://github.com/alexis-mignon/python-flickr-api/)

If you're on a debian system, use the "install" file to get all dependencies, simply run ```sudo ./install```.
If you're not on a debian system (why not?), just look at the "requirements.*" files and get the same libraries.
pip should be available for any distro or platform and with pip, simply run ```sudo pip install -r requirements.pip``` to automatically install the pip dependencies.

## Getting Images
getimages.py will download images from flickr
specify how you want your stuff downloaded in the ```[Download]``` section
whatever you put in the ```[Query]``` section will end up being sent to the flickr search api; consult their api docs to see which parameters you can put in

I know it is slow, maybe parallel downloads might help (?)

also, you need to provide your own flickr API key and secret, which goes into the getimages.config file

##Provided Data
our main datasets, called 4-landmarks and geocoverage_test, are available as an encrypted archive
they are encrypted using gpg with CAST5 and a password, which we will provide at request, since most images are not free to publish

## Modules

the pml module contains the central ShellMixtureMaximizer class as well as the SubmodularShell superclass

the stupidshell module shows how one can implement a simple shell
stuff to notice:

* all objects can be configured via a configuration file; by default, all config values are strings, for anything else, implement the configTypes method for the config keys that are not strings
* all values from the configuration file will be available in the object with an underscore prefix
* all data is passed around as Datum objects, which is also defined in the pml module; call meta(), image() or bwimage() on these objects to obtain the metadata (a dict) or a color / black-white image (a numpy ndarray). note that this stuff is only loaded from disk if you request it and is being held in memory from then on for subsequent calls
* when the data is loaded, each datum is passed to every shell's filter function. if any shell returns false, the datum is discarded. if not implemented, the function defaults to True. in the example, StupidShell filters specifically for images that have more than 0 tags
* shells may implement the configTypes and filter method, but must implement the prepare and evaluate methods
* the prepare method gets called once before the actual algorithm and gets all data as parameters
* all Datum objects have a member dict called ext, in which the shells can store arbitrary data about this datum during the prepare phase (e.g. the cluster which it is assigned to). please make a sub-dict with a specific name for your shell if you use this, as to not overlap with other shell data
* the evaluate method gets called whenever a set of data needs to be evaluated. it gets passed a list of Datum objects and is expected to return a single score for this specific selection of objects. the StupidShell example simply adds up the title lengths of all images to obtain the score

## Running

simplerun.py shows how to perform a simple run. it sets up a maximizer and configures it, then the same with a StupidShell. it adds the shell to the maximizer with a weight of 1.0 and then runs the maximizer. this returns a list of selected Datum objects, the IDs of which are then printed

demorun.py runs the stuff shown at the poster session

## Notes

### ipython
run
```
%load_ext autoreload
%autoreload 2
```
at the beginning of your ipython session to have the modules automatically reload on save

## Online Learning

```onlinelearn.py``` shows how it's done.
This will start a server on ```localhost:8080```, any GET request will start a new learning cascade, while the series of subsequent POST requests will train the weights, so don't F5 during training.
The weights are output after each submit.
Simply assign rewards to each picture (3 is pre-selected, 1 is the worst, 5 is the best) and submit the form. You can run this in perpetuity, have an eye on when the weights converge.
