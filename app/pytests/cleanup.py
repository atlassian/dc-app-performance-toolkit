import os
os.system('pytest -sq delete.py')
os.system('cp projects projectsOLD')
os.system('rm projects')
os.system('cp deleteCreatedObjects deleteCreatedObjectsOLD')
os.system('rm deleteCreatedObjects')