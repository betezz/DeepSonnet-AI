def get_poem(poem_title):
    if poem_title == "wildpeace":
        poem_text = """
            Not the peace of a cease-fire,
            not even the vision of the wolf and the lamb,
            but rather
            as in the heart when the excitement is over
            and you can talk only about a great weariness.
            I know that I know how to kill,
            that makes me an adult.
            And my son plays with a toy gun that knows
            how to open and close its eyes and say Mama.
            A peace
            without the big noise of beating swords into ploughshares,
            without words, without
            the thud of the heavy rubber stamp: let it be
            light, floating, like lazy white foam.
            A little rest for the wounds—
            who speaks of healing?
            (And the howl of the orphans is passed from one generation
            to the next, as in a relay race:
            the baton never falls.)

            Let it come
            like wildflowers,
            suddenly, because the field
            must have it: wildpeace.
            """
    elif poem_title == "hope is the thing with feathers":
        poem_text = """
            “Hope” is the thing with feathers -
            That perches in the soul -
            And sings the tune without the words -
            And never stops - at all -

            And sweetest - in the Gale - is heard -
            And sore must be the storm -
            That could abash the little Bird
            That kept so many warm -

            I’ve heard it in the chillest land -
            And on the strangest Sea -
            Yet - never - in Extremity,
            It asked a crumb - of me.
            """
    elif poem_title == "the road not taken":
        poem_text = """
            Two roads diverged in a yellow wood,
            And sorry I could not travel both
            And be one traveler, long I stood
            And looked down one as far as I could
            To where it bent in the undergrowth;

            Then took the other, as just as fair,
            And having perhaps the better claim,
            Because it was grassy and wanted wear;
            Though as for that the passing there
            Had worn them really about the same,

            And both that morning equally lay
            In leaves no step had trodden black.
            Oh, I kept the first for another day!
            Yet knowing how way leads on to way,
            I doubted if I should ever come back.

            I shall be telling this with a sigh
            Somewhere ages and ages hence:
            Two roads diverged in a wood, and I—
            I took the one less traveled by,
            And that has made all the difference.
            """
    elif poem_title == "sonnet 18":
        poem_text = """
            Shall I compare thee to a summer's day?
            Thou art more lovely and more temperate:
            Rough winds do shake the darling buds of May,
            And summer's lease hath all too short a date:
            Sometime too hot the eye of heaven shines,
            And often is his gold complexion dimmed;
            And every fair from fair sometime declines,
            By chance, or nature's changing course, untrimmed;
            But thy eternal summer shall not fade,
            Nor lose possession of that fair thou owest;
            Nor shall Death brag thou wanderest in his shade,
            When in eternal lines to time thou growest:
            So long as men can breathe or eyes can see,
            So long lives this, and this gives life to thee.
            """
    else:
        poem_text = ""

    return poem_title, poem_text

