from optparse import OptionParser
import sys

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "-n",
        "--nogui",
        action="store_true",
        dest="nogui",
        help="Run without GUI",
        default=False,
    )
    (options, args) = parser.parse_args()

    if options.nogui:
        from pywitch_client_nogui import PyWitchClientNoGui
        pywitch_client_app = PyWitchClientNoGui()
        sys.exit(pywitch_client_app.start())
    else:
        from pywitch_client_window import PyWitchClientApp

        pywitch_client_app = PyWitchClientApp()
        sys.exit(pywitch_client_app.app.exec_())
