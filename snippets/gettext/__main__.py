import gettext

gettext.bindtextdomain("test_gettext", "locales")
gettext.textdomain("test_gettext")

_ = gettext.gettext

def print_stuff():
    print(_("Hello world"))
    print(_("This is a translatable string"))

if __name__=="__main__":
    print_stuff()
