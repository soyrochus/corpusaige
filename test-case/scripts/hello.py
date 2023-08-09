# test script


def run(corpus, *args):
    if len(args) > 0:
        if args[0] == "stop":
            raise Exception("STOP!!!!")
        else:
            print(f"Hello {args[0]}") 
    else:
        print(f"Hello {corpus.name}")


