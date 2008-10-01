""" 
A class that holds a list of 

PREREQUISITES,
  usually of the form "input file X required", or

POSTREQUISITES,
  usually of the form "output file Y completed" 
  
Each requisite is in a state of "satisfied" or "not satisfied".  

All prerequisites must be matched by someone else's postrequisites, but
there may be extra postrequisites, to be used for monitoring progress.
"""

import sys
import re

class requisites:

    def __init__( self, reqs ):
        self.satisfied = {}
        self.ordered_list = reqs  
        for req in reqs:
            self.satisfied[req] = False

    def all_satisfied( self ):
        if False in self.satisfied.values(): 
            return False
        else:
            return True

    def is_satisfied( self, req ):
        if self.satisfied[ req ]:
            return True
        else:
            return False

    def set_satisfied( self, req ):
        if req in self.ordered_list:
            self.satisfied[ req ] = True
        else:
            print "ERROR: unknown requisite: " + req
            sys.exit(1)

    def requisite_exists( self, req ):
        if req in self.ordered_list:
            return True
        else:
            return False

    def set_all_satisfied( self ):
        for req in self.ordered_list:
            self.satisfied[ req ] = True

    def get_list( self ):
        return self.ordered_list

    def get_requisites( self ):
        return self.satisfied

    def satisfy_me( self, postreqs ):
        # can another's completed postreqs satisfy any of my prequisites?
        for prereq in self.satisfied.keys():
            # for each of my prerequisites
            if not self.satisfied[ prereq ]:
                # if my prerequisite is not already satisfied
                for postreq in postreqs.satisfied.keys():
                    # compare it with each of the other's postreqs
                    if postreq == prereq and postreqs.satisfied[postreq]:
                        # if they match, my prereq has been satisfied
                        self.set_satisfied( prereq )

    #def will_satisfy_me( self, postreqs ):
    #DISABLED: NOT USEFUL UNDER ABDICATION TASK MANAGEMENT
    #    # will another's postreqs, when completed, satisfy any of my prequisites?
    #    for prereq in self.satisfied.keys():
    #        # for each of my prerequisites
    #        if not self.satisfied[ prereq ]:
    #            # if my prerequisite is not already satisfied
    #            for postreq in postreqs.satisfied.keys():
    #                # compare it with each of the other's postreqs
    #                if postreq == prereq:
    #                    # if they match, my prereq has been satisfied
    #                    self.set_satisfied( prereq )


class fuzzy_requisites( requisites ):

    # for reference-time based prerequisites of the form 
    # "more recent than or equal to this reference time"

    def __init__( self, reqs ):
        requisites.__init__( self, reqs ) 

    def satisfy_me( self, postreqs ):
        # can another's completed postreqs satisfy any of my prequisites?
        for prereq in self.satisfied.keys():
            # for each of my prerequisites
            if not self.satisfied[ prereq ]:
                # if my prerequisite is not already satisfied

                # extract reference time from my prerequisite
                m = re.compile( "^(.*)(\d{10})(.*)$").match( prereq )
                if not m:
                    print "FAILED TO MATCH REF TIME IN " + prereq
                    sys.exit(1)

                [ my_start, my_reftime, my_end ] = m.groups()

                for postreq in postreqs.satisfied.keys():

                    if postreqs.satisfied[postreq]:
                        # extract reference time from other's postrequisite
                        m = re.compile( "^(.*)(\d{10})(.*)$").match( postreq )
                        if not m:
                            print "FAILED TO MATCH REF TIME IN " + postreq
                            sys.exit(1)

                        [ other_start, other_reftime, other_end ] = m.groups()

                        if other_start == my_start and other_end == my_end:
                            if other_reftime >= my_reftime:
                                print "FUZZY PREREQ: " + prereq
                                print "SATISFIED BY: " + postreq
                                self.set_satisfied( prereq )
