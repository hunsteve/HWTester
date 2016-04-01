import json
import shutil
import os
import time
from connection_hfportal import get_new_submissions, get_submission_file, post_result
from prepare_hw import unzip, java_compile, run_firejail_java, java_compile_all, clean_dir, find_java_class_with_package


with open('config.json') as config_file:  
    config = json.load(config_file)
    hw_data = config['homeworkData']
    WORKING_DIR = config['workingDir']
    EXTRACT_DIR = config['extractDirPrefix']    
    CORRECTOR_NAME = config['appName']
    MESSAGE_MAX_LENGTH = config['messageMaxLength']
    break_on_first_error = config['breakOnFirstError']    
    log_to_html = config['logToHTML']
    enable_write_to_database = config['enableWriteToDatabase']


def truncate(s):
    if len(s) > MESSAGE_MAX_LENGTH:
        return "[...]%s" % s[-MESSAGE_MAX_LENGTH:]
    else:
        return s

def log_output(log, input, target_output, output, stderr):
    if "result" not in log:
        log["result"] = []    
    if "good" not in log:
        log["good"] = 0
    if "bad" not in log:
        log["bad"] = []   
    log["result"].append({'input':input,'target_output':target_output,'output':output, 'error':stderr})
    index = len(log["result"])-1
    
    stdout_lines = stdout.split("\n")
    target_output_lines = target_output.split("\n")    
    if "partbad" not in log:
        log["partbad"] = []
        for i in range(len(target_output_lines)):
            log["partbad"].append([])

    if stdout != target_output or stderr:
        for i in range(len(target_output_lines)):
            if len(stdout_lines) <= i or stdout_lines[i] != target_output_lines[i]:                
                log["partbad"][i].append(index)        
        log["bad"].append(index)
    else:
        log["good"] += 1

def response_message_from_log(log):
    if not log["bad"]:
        return "Passed all tests."
    errtext = []   
    lasterrindex = -1     
    for errlineindex in range(len(log["partbad"])):
        if not log["partbad"][errlineindex]:
            continue
        errindex = log["partbad"][errlineindex][0]
        if lasterrindex == errindex:
            continue
        err = log['result'][errindex]
        errtext.append("Wrong answer in line %d of output: \n%s\n\nfor input #%d: \n%s\n" % (errlineindex+1, truncate(err['output']), errindex, err['input']))
        lasterrindex = errindex
        
    return "".join(errtext)

def score_from_log(log, scorelimits):    
    print(log['partbad'])
    score = 0
    for i in range(len(log['partbad'])):
        score += sum([ratio <= float(len(log['result'])-len(log['partbad'][i])) / len(log['result']) for ratio in scorelimits[i]])    
    return score

def check_log_for_errors(log):
    for res in log["result"]:
        if res['error']:
            return (res['error'], res['input'])
    return (None, None)

    

def log2html(log):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open("logs/log_%s.html"%log["id"],"w") as file:
        file.write("<b>ID:</b> %d <br>" % (log["id"]))

        if "compile_error" in log:
            file.write("<b>COMPILE ERROR:</b> %s <br>" % (log["compile_error"]))            
        else:   
            file.write("<b>MAIN CLASS:</b> %s <br>" % (log["classname"]))
            file.write("<b>GOOD RATIO:</b> %d/%d <br>" % (log["good"], len(log["result"])))
            file.write("<b>TEST DURATIOn:</b> %f s<br>" % (log["endtime"] - log["starttime"]))
            
            file.write('<table border="1">')
            file.write("<tr>")
            file.write("<th>INPUT</th><th>TARGET_OUTPUT</th><th>OUTPUT</th><th>ERROR</th>")
            file.write("</tr>")
            for badindex in log["bad"]:
                row = log['result'][badindex]
                file.write("<tr>")                
                file.write("<td>")
                file.write(row['input'].replace("\n","<br>"))
                file.write("</td>")
                file.write("<td>")
                file.write(row['target_output'].replace("\n","<br>"))
                file.write("</td>")
                file.write("<td>")
                file.write(row['output'].replace("\n","<br>"))
                file.write("</td>")
                file.write("<td>")
                file.write(row['error'].replace("\n","<br>"))
                file.write("</td>")
                file.write("</tr>")
            file.write("</table>")

for hw_id, hw_details in hw_data.iteritems():
    if isinstance(hw_details['testcases'], basestring):
        with open(hw_details['testcases'],"r") as data_file:        
            hw_details['testcases'] = json.load(data_file)

    for submission_id in get_new_submissions(hw_id):
        print("Testing submission: %d" % submission_id)

        log = {}
        log["id"] = submission_id

        data = get_submission_file(submission_id)
        
        src_dir = EXTRACT_DIR + str(submission_id)

        clean_dir(src_dir)
        clean_dir(WORKING_DIR)

        try:
            unzip(data, src_dir)
            (stdout, stderr) = java_compile_all(src_dir, WORKING_DIR)
            if stderr:
                log["compile_error"] = stderr   
        except Exception as e:
            log["compile_error"] = e                            

        if "compile_error" not in log:
            target = find_java_class_with_package(hw_details['classname'], WORKING_DIR)       
            log["classname"] = target            

            testcntr = 0
            log["starttime"] = time.clock()
            for data in hw_details['testcases']:            
                input = data[0]
                target_output = data[1]

                testcntr += 1
                if (testcntr > hw_details["max testcount"]):
                    break
                (stdout, stderr, extraerr) = run_firejail_java(target,input,hw_details['firejail profile'], timeout = hw_details['timeout'])
                stdout = stdout.strip()
                target_output = target_output.strip()

                log_output(log, input, target_output, stdout, stderr or extraerr)               
                
                if break_on_first_error and (stderr or extraerr):                
                    break                                            
                
            log["endtime"] = time.clock()

            if enable_write_to_database:
                (err, errinp) = check_log_for_errors(log)
                if err and errinp:
                    errtext = "Runtime error occured \n%s\nfor input: \n%s" % (truncate(err), errinp)
                    post_result(submission_id, CORRECTOR_NAME, 9, 0, errtext)
                else:
                    post_result(submission_id, CORRECTOR_NAME, 7, score_from_log(log, hw_details['scorelimits']), response_message_from_log(log))
        else:
            if enable_write_to_database:
                post_result(submission_id, CORRECTOR_NAME, 9, 0, truncate(log["compile_error"]))            
        if log_to_html:
            log2html(log)    


       
