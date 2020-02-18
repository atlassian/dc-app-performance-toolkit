import os
import re
import json
from pathlib import Path
inFilename = "PyTestExecutor-1.ldjson"
outFilename = "PyTestExecutor-1.jtl"
ENV_TAURUS_ARTIFACT_DIR = 'TAURUS_ARTIFACTS_DIR'

JTL_HEADER = 'timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads,Latency,Hostname,Connect\n'
artifacts_dir: str = os.getenv(ENV_TAURUS_ARTIFACT_DIR)
if artifacts_dir is None:
    raise SystemExit(f'Error: env variable {ENV_TAURUS_ARTIFACT_DIR} is not set')

artifacts_dir_path = Path(artifacts_dir)
in_file_path = artifacts_dir_path / inFilename
out_file_path = artifacts_dir_path / outFilename

with open(in_file_path) as f:
    with open(out_file_path, "w") as f2:
        lines = f.readlines()
        first = lines[0]
        last = lines[-1]
        for line in lines:
            if line is first:
                f2.write(JTL_HEADER)
            row = json.loads(line)
            runRes = '';
            if (row["status"]=="PASSED"):
                runRes = "Success,,True"
            else:
                error_msg = row["error_msg"]
                pattern = "\\.(.*?)\: Message: "
                tmpSubstring = re.search(pattern, error_msg)
                if tmpSubstring!="" and  tmpSubstring != None:
                    print("b" + str(tmpSubstring))
                    substring = tmpSubstring.group(1)
                    substring= substring.rsplit('.', 1)[-1]
                    print("b" + substring)
                    runRes = substring + ",,False"
                else:
                    runRes = "Failed,,False"
            start_time = row["start_time"]
            if start_time>0:
                start_time = round(start_time*1000)
            f2.write(str(start_time ))
            f2.write("," )
            duration = row["duration"]
            if duration>0:
                duration = round(duration*1000)
            f2.write(str(duration))
            f2.write("," )
            f2.write(row["test_suite"] + ":" + row["test_case"] + ",,")
            f2.write(runRes + "," + "0,0,0,0,,0\n")

