from subprocess import check_output


try:
    print("Git version: {}".format(check_output(["git", "--version"])))
except Exception as e:
    raise Exception("Please check if git installed and available from command line.")
