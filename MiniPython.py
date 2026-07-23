import keyword
import builtins
import re
import multiprocessing
import queue

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings


# =========================
# SETTINGS
# =========================

sandbox_enabled = False


COMMANDS = [
    "exit",
    "help",
    "vars",
    "clear",
    "toggle_sandbox"
]


# =========================
# AUTOCOMPLETE
# =========================

class PythonCompleter(Completer):

    def __init__(self, namespace):
        self.namespace = namespace


    def get_completions(self, document, complete_event):

        text = document.text_before_cursor


        match = re.search(
            r"(\w+)\.(\w*)$",
            text
        )


        if match:

            obj_name = match.group(1)
            partial = match.group(2)

            try:

                obj = eval(
                    obj_name,
                    self.namespace
                )

                for item in dir(obj):

                    if item.startswith(partial):

                        yield Completion(
                            item,
                            start_position=-len(partial)
                        )

            except:

                pass


        else:

            words = set()

            words.update(
                keyword.kwlist
            )

            words.update(
                dir(builtins)
            )

            words.update(
                self.namespace.keys()
            )

            words.update(
                COMMANDS
            )


            current = (
                document
                .get_word_before_cursor()
            )


            for word in words:

                if word.startswith(current):

                    yield Completion(
                        word,
                        start_position=-len(current)
                    )



# =========================
# SANDBOX
# =========================

def sandbox_execute(code, output):

    safe_builtins = {

        "print": print,
        "len": len,
        "range": range,
        "str": str,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "bool": bool,
        "enumerate": enumerate

    }


    env = {
        "__builtins__": safe_builtins
    }


    try:

        exec(
            code,
            env
        )


    except Exception as e:

        output.put(
            "Error: " + str(e)
        )



# =========================
# EXECUTOR
# =========================

def execute(code):

    if sandbox_enabled:

        result = multiprocessing.Queue()


        process = multiprocessing.Process(
            target=sandbox_execute,
            args=(
                code,
                result
            )
        )


        process.start()

        process.join(3)


        if process.is_alive():

            process.terminate()

            print(
                "Execution stopped: timeout"
            )


        else:

            try:

                print(
                    result.get_nowait()
                )


            except queue.Empty:

                pass



    else:

        try:

            try:

                result = eval(
                    code,
                    variables
                )


                if result is not None:

                    print(result)


            except SyntaxError:

                exec(
                    code,
                    variables
                )


        except Exception as e:

            print(
                "Error:",
                e
            )



# =========================
# KEYBINDS
# =========================

kb = KeyBindings()


@kb.add(
    "escape",
    "enter"
)
def submit(event):

    event.current_buffer.validate_and_handle()



# =========================
# MINI PYTHON
# =========================

variables = {}


session = PromptSession(

    multiline=True,

    key_bindings=kb,

    completer=PythonCompleter(
        variables
    )

)



print("======================")
print("     MiniPython")
print("======================")

print()

print(
    "Sandbox:",
    "ON" if sandbox_enabled else "OFF"
)

print()

print("Commands:")
print("exit              - quit")
print("help              - commands")
print("vars              - show variables")
print("clear             - clear variables")
print("toggle_sandbox    - switch sandbox mode")

print()

print("Run code:")
print("ESC + ENTER")

print()



while True:

    try:

        code = session.prompt(
            ">>> "
        )


    except KeyboardInterrupt:

        print("^C")

        continue


    except EOFError:

        break



    command = code.strip()



    if command == "exit":

        break



    if command == "help":

        print(
            ", ".join(COMMANDS)
        )

        continue



    if command == "vars":

        for key, value in variables.items():

            if not key.startswith("__"):

                print(
                    key,
                    "=",
                    value
                )

        continue



    if command == "clear":

        variables.clear()

        print(
            "Variables cleared"
        )

        continue



    if command == "toggle_sandbox":

        sandbox_enabled = not sandbox_enabled

        print(
            "Sandbox:",
            "ON" if sandbox_enabled else "OFF"
        )

        continue



    if not command:

        continue



    execute(
        code
    )



print("Goodbye!")
