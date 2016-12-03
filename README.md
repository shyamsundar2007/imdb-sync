# imdb_sync
Sync IMDB watchlist with autodl-irssi plugin

# Parameters
In file imdb_sync.py, update the 2 variables *autodlCfgFilePath* and *imdbWatchlistPath*. 
*autodlCfgFilePath* is the path to the autodl which contains the autodl.cfg file
*imdbWatchlistPath* is the rss link to your imdb watchlist. Note that your watchlist has to be listed publicly for the script to work.

# Running the script
The script can be run simply by calling "python imdb_sync.py". This will automatically get the IMDB watchlist and add any new movies to your autodl.cfg file. The movies will be automatically downloaded once if auto-irssi is setup properly.