import subprocess

pathToTextileBucket = '' #example 'storage/'

def hubBucketPush():
    result = subprocess.run(["pathToHub/hub", "buck", "push", "-y"], 
                             capture_output=False, cwd = pathToTextileBucket)

def callHub(command):
    result = subprocess.run(["pathToHub/hub", "buck", command], 

                            capture_output=True, cwd = pathToTextileBucket)
    #print(result.stdout)
    #return(result.stdout.decode('utf-8'))