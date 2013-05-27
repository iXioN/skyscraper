skyscraper
==========
SkyScrapper is SkyScanner scraper based on django

Setup
==========

    #clone the git repo
    $ git clone https://github.com/iXioN/skyscraper.git
    $ cd skyscraper/
    #download the requirements
    $ make bootstrap
    #then activate the venv
    $ source bin/activate


Search flights
================
Only one command allow to search flight

the usage is :
    
    $ ./manage.py search --help
    Usage: ./manage.py search [options] 
    Search a flight on skyscanner website
    -f FROM_CITY, --from=FROM_CITY
                                            The origin city name
      -t DESTINATION_CITY, --to=DESTINATION_CITY
                                            The city where you want to go
      -d DEPART_DATE, --depart=DEPART_DATE
                                            the date you want to go, format (month/day/year) ex:
                                            05/27/13
      -r RETURN_DATE, --return=RETURN_DATE
                                            the date you want to return, format (month/day/year)
                                            ex: 05/27/13
      -l PRINT_LIMIT, --limit=PRINT_LIMIT
                                            The number of flight o print

Exemple
========

here is some exemple of searchs:
    
search flights from Nantes(FR) to Edinburg(UK) between the 28th May and 30th May 2013

    ./manage.py search -f nantes -t edinburg -d 05/28/13 -r 05/30/13
    ---------------------------------------------------------
    search on SkyScanner from Nantes(NTE) to Édimbourg(EDI)
    Tue 28 May 2013 - Thu 30 May 2013
    ---------------------------------------------------------
    409 € on Flybe via Logitravel
    outbound : 12:50(NTE) - 17:05(EDI) stops 1 (MAN) 05h15
    inbound : 05:50(EDI) - 12:25(NTE) stops 1 (MAN) 05h35
    -------------------------------
    418 € on Flybe via Opodo
    outbound : 12:50(NTE) - 17:05(EDI) stops 1 (MAN) 05h15
    inbound : 09:45(EDI) - 11:55(NTE) stops 1 (SOU) 01h10
    ....

search one way flights from Atlanta(US) to Berlin(GER) on 21th September 2013

    ./manage.py search -f Atlanta -t Berlin -d 09/21/13
    ---------------------------------------------------------
    search on SkyScanner from Atlanta Hartsfield-Jackson ATL(ATL) to Berlin(BERL)
    one way from Sat 21 Sep 2013
    ---------------------------------------------------------
    1869 € on Air France via Air France
    outbound : 19:45(ATL) - 13:15(TXL) stops 1 (CDG) 11h30
    -------------------------------
    1869 € on Air France via Air France
    outbound : 16:50(ATL) - 10:50(TXL) stops 1 (CDG) 12h00
    ...