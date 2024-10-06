import sys
import modal

app = modal.App("example-hello-world")


@app.function()
def fu(num: int) -> int:
    if num % 2 == 0:
        print("hello", num)
    else:
        print("world", num, file=sys.stderr)

    return num * num


@app.local_entrypoint()
def main():
    # run the function locally
    print(fu.local(1000))

    # run the function remotely on Modal
    print(fu.remote(1000))

    # run the function in parallel and remotely on Modal
    total = 0
    for ret in fu.map(range(200)):
        total += ret

    print(total)
