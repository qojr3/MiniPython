import keyword
import builtins
import re
import multiprocessing
import queue

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.margins import NumberedMargin
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings


sandbox_enabled = False
variables = {}


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

    def get_completions(
        self,
        document,
        complete_event
    ):

        current = document.get_word_before_cursor()

        words = set()

        words.update(keyword.kwlist)
        words.update(dir(builtins))
        words.update(variables.keys())
        words.update(COMMANDS)


        for word in words:

            if word.startswith(current):

                yield Completion(
                    word,
                    start_position=-len(current)
                )



# =========================
# SANDBOX
# =========================

def sandbox_exec(code, output):

    safe = {
        "print": print,
        "len": len,
        "range": range,
        "str": str,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict
    }


    try:

        exec(
            code,
            {
                "__builtins__": safe
            }
        )


    except Exception as e:

        output.put(str(e))



def run_code(code):

    if sandbox_enabled:

        output = multiprocessing.Queue()

        process = multiprocessing.Process(
            target=sandbox_exec,
            args=(code, output)
        )


        process.start()

        process.join(3)


        if process.is_alive():

            process.terminate()

            print("Timeout")


        else:

            try:
                print(output.get_nowait())

            except queue.Empty:
                pass


    else:

        try:

            try:

                value = eval(
                    code,
                    variables
                )

                if value is not None:
                    print(value)


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
# EDITOR
# =========================

buffer = Buffer(
    multiline=True,
    completer=PythonCompleter()
)


control = BufferControl(
    buffer=buffer
)


window = Window(
    content=control,
    left_margins=[
        NumberedMargin()
    ]
)



# =========================
# KEYS
# =========================

kb = KeyBindings()


@kb.add("escape", "enter")
def execute(event):

    global sandbox_enabled


    code = buffer.text


    if code.strip() == "exit":

        event.app.exit()
        return


    if code.strip() == "toggle_sandbox":

        sandbox_enabled = not sandbox_enabled

        print(
            "Sandbox:",
            sandbox_enabled
        )

        buffer.text = ""

        return


    if code.strip() == "vars":

        print(variables)

        buffer.text = ""

        return


    if code.strip() == "clear":

        buffer.text = ""

        return


    if code.strip() == "help":

        print(COMMANDS)

        buffer.text = ""

        return


    run_code(code)

    buffer.text = ""



@kb.add("c-c")
def quit_app(event):

    event.app.exit()



# =========================
# START
# =========================

app = Application(

    layout=Layout(
        window
    ),

    key_bindings=kb,

    full_screen=True
)


app.run()