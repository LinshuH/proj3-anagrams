"""
Flask web site with vocabulary matching game
(identify vocabulary words that can be made 
from a scrambled string)
"""

import flask
import logging

# Our own modules
from letterbag import LetterBag
from vocab import Vocab
from jumble import jumbled
import config

###
# Globals
###
app = flask.Flask(__name__)

CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY  # Should allow using session variables

#
# One shared 'Vocab' object, read-only after initialization,
# shared by all threads and instances.  Otherwise we would have to
# store it in the browser and transmit it on each request/response cycle,
# or else read it from the file on each request/responce cycle,
# neither of which would be suitable for responding keystroke by keystroke.

WORDS = Vocab(CONFIG.VOCAB)

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    """The main page of the application"""
    flask.g.vocab = WORDS.as_list()
    flask.session["target_count"] = min(
        len(flask.g.vocab), CONFIG.SUCCESS_AT_COUNT)
    flask.session["jumble"] = jumbled(
        flask.g.vocab, flask.session["target_count"])
    flask.session["matches"] = []
    app.logger.debug("Session variables have been set")
    assert flask.session["matches"] == []
    assert flask.session["target_count"] > 0
    app.logger.debug("At least one seems to be set correctly")
    return flask.render_template('vocab.html')


@app.route("/keep_going")
def keep_going():
    """
    After initial use of index, we keep the same scrambled
    word and try to get more matches
    """
    flask.g.vocab = WORDS.as_list()
    return flask.render_template('vocab.html')


@app.route("/success")
def success():
    return flask.render_template('success.html')

#######################
# Form handler.
# CIS 322 note:
#   You'll need to change this to a
#   a JSON request handler
#######################


@app.route("/_check", methods=["POST"])
def check():
    """
    User has submitted the form with a word ('attempt')
    that should be formed from the jumble and on the
    vocabulary list.  We respond depending on whether
    the word is on the vocab list (therefore correctly spelled),
    made only from the jumble letters, and not a word they
    already found.
    """
    # 3 things to check: 1, in_jumble: letter from anagram? 2, mached: input word in WORDS?
    # 3, matches: input already been tested before?
    app.logger.debug("Entering check")

    # The data we need, from form and from cookie
    text = flask.request.args.get("text", type=str) # get the user input
    ## text = flask.request.form["attempt"]
    jumble = flask.session["jumble"]
    matches = flask.session.get("matches", [])  # Default to empty list
    
    
    # Is it good?
    in_jumble = LetterBag(jumble).contains(text)
    matched = WORDS.has(text)
    # matched should be call from Vocab
    #matched = Vocab

    # Respond appropriately
    if matched and in_jumble and not (text in matches):
        # Cool, they found a new word
        matches.append(text)
        flask.session["matches"] = matches
        #JSON Code:
        # count the number of success, if the lenght is >= 2(target_count), pass to the html.
        # join_matches: if not in matches: true; else: false; in_WORDS(mached):in:True, not in False;
        # in_jumble: in: True, not in False;
        if len(matches) >= flask.session["target_count"]:
            rslt = {"join_matches": False, "in_WORDS":True, "in_jumble":True}
        else:
            rslt = {"join_matches": True, "in_WORDS":True, "in_jumble":True}
        
    elif text in matches:
        flask.flash("You already found {}".format(text))  #Words in matches
        rslt = {"joinin_matches": False, "in_WORDS": True, "in_jumble": True} 
    elif not matched:
        flask.flash("{} isn't in the list of words".format(text))   #Words in WORDS?
        rslt = {"join_matches": True, "in_WORDS": False, "in_jumble": True}
    elif not in_jumble:
        flask.flash(
            '"{}" can\'t be made from the letters {}'.format(text, jumble))
        rslt = {"join_matches":True, "in_WORDS": True, "in_jumble": False}
    else:
        app.logger.debug("This case shouldn't happen!")
        assert False  # Raises AssertionError
        rslt = {"join_matches":False, "in_WORDS": False, "in_jumble": False}
    return flask.jsonify(result=rslt)


    # Q: Where to use jumble.py(create anagram) and Vocab.py(determine whether the word is in WORDS?

###############
# AJAX request handlers
#   These return JSON, rather than rendering pages.
###############


@app.route("/_example")
def example():
    """
    Example ajax request handler
    """
    app.logger.debug("Got a JSON request")
    rslt = {"key": "value"}
    return flask.jsonify(result=rslt)


#################
# Functions used within the templates
#################

@app.template_filter('filt')
def format_filt(something):
    """
    Example of a filter that can be used within
    the Jinja2 code
    """
    return "Not what you asked for"

###################
#   Error handlers
###################


@app.errorhandler(404)
def error_404(e):
    app.logger.warning("++ 404 error: {}".format(e))
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def error_500(e):
    app.logger.warning("++ 500 error: {}".format(e))
    assert not True  # I want to invoke the debugger
    return flask.render_template('500.html'), 500


@app.errorhandler(403)
def error_403(e):
    app.logger.warning("++ 403 error: {}".format(e))
    return flask.render_template('403.html'), 403


####

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        app.logger.info(
            "Opening for global access on port {}".format(CONFIG.PORT))
        app.run(port=CONFIG.PORT, host="0.0.0.0")
