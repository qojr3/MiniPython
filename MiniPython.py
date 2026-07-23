# MiniPython.py

variables = {}

print("MiniPython interpreter")
print("Multi-line support enabled")
print("Use TAB/indentation normally")
print("Empty line runs the code")
print("Type 'exit' to quit\n")


while True:
    lines = []

    while True:
        line = input(">>> ")

        if line == "":
            break

        if line == "exit":
            quit()

        # Keep indentation
        line = line.replace("    ", "\t")

        lines.append(line)

    code = "\n".join(lines)

    if not code:
        continue

    try:
        try:
            result = eval(code, {}, variables)

            if result is not None:
                print(result)

        except SyntaxError:
            exec(code, {}, variables)

    except Exception as e:
        print("Error:", e)