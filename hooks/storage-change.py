import subprocess

print(subprocess.check_output('snap run rocketchat.storage-change', shell=True))
