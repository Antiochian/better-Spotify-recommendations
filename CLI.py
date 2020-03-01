# -*- coding: utf-8 -*- python3
"""
Created on Sun Mar  1 14:45:11 2020
Crude user interface for the main Diving Bell file
@author: Antiochian
"""
from random import shuffle
import time
import Diving_Bell
from Diving_Bell import NUM_OF_RECCS

############## VISUAL DISPLAY ##################

def print_header():
    print("""
            
         .                                                            .
         . ...... .. .    -\ SPOTIFY MUSIC RECOMMENDER V2 /-  .   ... |
         .                                                            |
      .::: :::::: :: : : __               ___       __       ::  :::: |::.
         |              |__) \ /    |__| |__  |\ | |__) \ /           |
   .:::::| :::::: :: :  |__)  |     |  | |___ | \| |  \  | : :  ::::: |:::::.
         |           .                                    .           |
 `:::::::| :::::: :: : :. :::::::::::::::::::::::::::::: .: :: :::::: |:::::::'
   `::.  |           |                                    |    |      |  .::'
     `::.`--- - .    | ----------- - - - - - ---------- - |    | - ---'.::'
     . `::.     |    |       ..       _   _      ..       |    |     .::' .
     |   `::.   |    |               ((___))              |    |   .::'   |
     |     `::._|    |_      ..      [ x x ]     ..      _|    |_.::'     |
    _|       `:\      /      ..       \   /              \      /:'       |_
    \          `\    /       ::       (' ')      ..       \    /'          /
     \           \  /.       ..        (U)       ..       .\  /           /
      \   _ .  /\ \/`::.  `:::'                  `:::'  .::'\/ /\  . _   /
       \ (_\ \/  \  . `::.  `::.      ..        .::'  .::' .  /  \/ /_) /
        \         \/    `::.  `::.    .. ..   .::'  .::'    \/         /
         `-.._ __ _ __ _  `::.  `::.  :: .. .::'  .::'  _ __ _ __ _..-'
                        ``-.`::.  `::.:: ::::'  .::'.-''
                            `.`::.  `::: ::'  .::'.'
                               .`::.  `: '  .::'.
                                 .`::.    .::'.
                                   .`::. ::'.
                                     .`::'.
                                       .:.
                                        . 					""")
    return

def print_info(spotify,IDs,cutoff=False):
    """Prints a list of track_IDs"""
    if type(IDs) == str:
        IDs = [IDs]
    elif IDs == []:
        print("No results.")
    elif cutoff:
        IDs = list(IDs)[:cutoff] #trim results if needed
    toprint = []
    for ID in IDs:
        artist = spotify.artist(ID)
        genres = artist['genres']
        if len(genres):
            genre = genres[0]
        else:
            genre = 'unknown'
        toprint.append(artist['name'] + " - "+genre)
    print("\n".join(toprint))
    return

################ MENUS/CRUDE GUIs ##################

def menu_CLI(startup=True):
    spotify = Diving_Bell.setup()
    if startup:
        print_header()
        username = spotify.me()['id']
        print("\n",username," logged in (Q to quit).")
    choice = input("1: Grow/make database\n2: Get recommendations\n\t> ")
    if choice == '1':
        Diving_Bell.make_database()
        choice = input("\t1: Stochastic Growth (faster)\n\t2: Targeted Growth\n\t3: Deep-Dive (very slow!)\n\t> ")
        if choice == '1':
            print("Hit Ctrl-C to exit at any time")
            Diving_Bell.idle_scraper()
            menu_CLI(False)
        elif choice == '2':
            targeted_scraper(10,3)
            menu_CLI(False)
        elif choice == '3':
            targeted_scraper(10,4)
            menu_CLI(False)
    elif choice == '2':
        recc_CLI(spotify)
    elif choice.lower() == "q":
        print("Quitting...") 
        return
    else:
        print("Invalid response.")
        menu_CLI(False)
    return

def recc_CLI(spotify):
    print("ARTIST SEARCH")
    search_term = input("\tEnter search term: ")
    if search_term.lower() == "q":
        print("Quitting...")
        return
    target_ID = CL_search(spotify,search_term)
    print("\tGetting reccs...")
    t0 = time.time()
    DEFAULT = Diving_Bell.default_reccs(spotify,target_ID,5)
    REVERSE = Diving_Bell.reverse_reccs(spotify,target_ID,5)
    print("Search complete. Total time: ",time.time()-t0)
    print("-"*10)
    print("\n RESULTS FOR SEARCH: ",search_term)
    #timing data
    print("\nSPOTIFY RECCS:")
    print_info(spotify, DEFAULT)
    print("\n(MY) REVERSE RECCS:")
    print_info(spotify, REVERSE)
    choice = input("\n\tSave Playlist Based On Reccs? (Y/N): ")
    if choice.lower() == "y":
        DEFAULT_tracks = Diving_Bell.artists_to_tracks(spotify,DEFAULT)
        REVERSE_tracks = Diving_Bell.artists_to_tracks(spotify,REVERSE)
        save_playlist(spotify,DEFAULT_tracks+REVERSE_tracks,target_ID)
    menu_CLI(False)
    return

def CL_search(spotify, search_term):
    results = spotify.search(q=search_term, type='artist',limit=10) #"album"+
    index = 1
    opt_dict = {}
    for item in results['artists']['items']:
        name = item['name']
        all_genres = item['genres']
        if len(all_genres):
            genre = all_genres[0]
        else:
            genre = "unknown"
        track_id = item['id']
        opt_dict[index] = track_id
        print("\t",index,": ",name," - ",genre )
        index +=1
    choice = input("Enter choice (Q to cancel): ")
    if choice.lower() != "q":
        return opt_dict[int(choice)] #ID value of choice
    else:
        return 0

############### MAKE PLAYLIST ##################

def save_playlist(spotify,list_of_tracks,target_ID):
    """Converts list of track IDs to a saved playlist"""
    list_of_IDs = [track['id'] for track in list_of_tracks]
    shuffle(list_of_IDs)
    playlist_name = "Auto-Reccer's Auto-Playlist"
    user_ID = spotify.me()['id']
    playlist = spotify.user_playlist_create(user_ID, playlist_name, public=False, description=description())
    playlist_ID = playlist['id']
    spotify.user_playlist_add_tracks(user_ID, playlist_ID, list_of_IDs, position=None)
    return

def description():
    coredesc = "Spotify Diving Bell v2 by Antioch"
    dateinfo = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return coredesc+"\n"+dateinfo

################### MISC ########################

def targeted_scraper(width=5,depth=2,targetseed=None):
    """This scraper is much slower, and more wasteful on the API, but is
    extremely targetted towards a specific artist, and never strays too far away from it.
    Best used in small doses.
    """
    spotify=Diving_Bell.setup()
    if targetseed==None:
        targetseed=CL_search(spotify,input("Artist Search: "))
    print("Running ",width,"x",depth," search...")
    print("[Estimated runtime = ",round((NUM_OF_RECCS**depth)*width*0.025/60,3)," minutes]") #84 is experimentally determined
    t0 = time.time()
    Diving_Bell.breadthwise_launcher(targetseed,width,depth)
    Diving_Bell.estimate_database_size()
    print("\tCompleted in: ",round((time.time()-t0)/60,3)," min")
    return

if __name__ == "__main__":
    menu_CLI(True)
    
