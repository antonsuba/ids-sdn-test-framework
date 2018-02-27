import inspect
import pkgutil
import sys
# from network import ids_test_topo
# from ml_ids import ids_classifier
# from ml_ids import classifier_validation
import lib.cli_commands

def main():
    # Generate dictionary of command drivers
    def __load_class(module):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            return name, obj

    commands = dict()
    package = lib.cli_commands

    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        module = importer.find_module(modname).load_module(modname)
        cmd_name, cmd_class = __load_class(module)
        commands[cmd_class.trigger] = cmd_class

    # Extract command driver based on cli arg
    cmd_arg = sys.argv[1]
    
    try:
        cmd_class = commands[cmd_arg]

        cmd_driver = cmd_class()
        cmd_driver.run()
    except KeyError:
        print 'Command not found'

if __name__ == "__main__":
    main()
