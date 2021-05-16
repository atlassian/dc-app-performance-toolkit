from subprocess import check_output


try:
    print("Git version: {}".format(check_output(["git", "--version"])))
except Exception:
    raise Exception("Please check if git installed and available from command line.")
