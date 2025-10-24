#!/usr/bin/env python3

import getopt
import os
import os.path
import shutil
import subprocess
import sys
import math

from glob import glob
from tempfile import NamedTemporaryFile

import ui
from ui import OK, WARNING, ERROR
import hints
import clean
from util import delete_file, change_extension
from run import run_solution
from tex import build_pdf
from languages import get_compile_command

if sys.platform == "linux" or sys.platform == "linux2":
    # linux
    DEVNULL = 'null'
elif sys.platform == "darwin":
    # MAC OS X
    DEVNULL = 'null'
elif sys.platform == "win32":
    # Windows
    DEVNULL = 'nul'
elif sys.platform == "win64":
    # Windows 64-bit
    DEVNULL = 'nul'

def program_available(program):
    u"Check if `program` is available in the system PATH."
    with open(os.path.join('/','dev',DEVNULL), 'w') as dev_null:
        return subprocess.call(['which', program], stdout = dev_null) == 0

def box_build_package(pkg):
    u"Build Boca package."

    curdir=os.getcwd()
    if pkg=='contest':
        print('\nBuilding packages for contest session...')
        os.chdir(os.path.join('..','boca','contest'))
        try:
            shutil.rmtree(os.path.join('..','..','packages','contest'))
        except:
            pass
    else:
        print('\nBuilding packages for warmup session...')
        os.chdir('../boca/warmup')
        try:
            shutil.rmtree(os.path.join('..', '..', 'packages', 'warmup'))
        except:
            pass
    if subprocess.call('..','bin','build_packages.py', shell = True) == 0:
        ui.end_task('OK')
    else:
        ui.end_task('failed!')
    print('\nChecking...')
    if subprocess.call('.','diff.sh', shell = True) == 0:
        try:
            os.mkdir(os.path.join('..', '..', 'packages'))
        except:
            pass
        if pkg=='contest':
            shutil.copytree('packages',os.path.join('..','..','packages','contest'))
        else:
            shutil.copytree('packages',os.path.join('..','..','packages','warmup'))
        ui.end_task('OK')
    else:
        ui.end_task('failed!')
    os.chdir(curdir)

def build_binaries(directory):
    u"Build all source code in `directory`."
    def build_binary(src_fn):
        u"Build the binary for `src_fn`."
        ui.start_task(src_fn)

        exe_fn = change_extension(src_fn, 'exe')
        cmd_line, error_msg = get_compile_command(src_fn, exe_fn)
        if error_msg:
            ui.show_message('Error', 'Unknown extension for source file.', ERROR)
            ui.end_task('failed')

        if subprocess.call(cmd_line, shell = True) == 0:
            ui.end_task('OK')
        else:
            ui.end_task('failed')

    for src_fn in sorted(glob(os.path.join(directory, '*.c'))):
        build_binary(src_fn)
    for src_fn in sorted(glob(os.path.join(directory, '*.cpp'))):
        build_binary(src_fn)
    for src_fn in sorted(glob(os.path.join(directory, '*.java'))):
        build_binary(src_fn)
    for src_fn in sorted(glob(os.path.join(directory, '*.py'))):
        build_binary(src_fn)
    for src_fn in sorted(glob(os.path.join(directory, '*.pas'))):
        build_binary(src_fn)
    for src_fn in sorted(glob(os.path.join(directory, '*.js'))):
        build_binary(src_fn)

def mycomp(a,b):
    'compares two test file names based on the case group and case number'
    a,tmp=os.path.split(a)
    atestnum,tmp = os.path.splitext(tmp)
    tmp,acasenum = os.path.split(a)
    b,tmp=os.path.split(b)
    btestnum,tmp = os.path.splitext(tmp)
    tmp,bcasenum = os.path.split(b)
    if int(acasenum)>int(bcasenum):
        return 1
    elif int(acasenum)<int(bcasenum):
        return -1
    else:
        if int(atestnum)>int(btestnum):
            return 1
        elif int(atestnum)<int(btestnum):
            return -1
        else:
            return 0

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

# Works if problem has at most 15 subtasks
def input_files_sub(name):
    ret = []
    for i in range(1,15):
        tmp=glob('{}/build/tests/{}/*.in'.format(name,i))
        tmp.sort(key=cmp_to_key(mycomp))
        ret.append(tmp)
    while(len(ret) > 0 and len(ret[-1]) == 0):
        ret.pop()
    return ret

def input_files(name):
    tmp=glob('%s/build/tests/*/*.in' % name)
    tmp.sort(key=cmp_to_key(mycomp))
    return tmp

def sample_input_files(name):
    tmp=glob('%s/documents/sample-*.in' % name)
    tmp.sort()
    return tmp

def output_files(name):
    tmp=glob('%s/build/tests/*/*.sol' % name)
    tmp.sort(key=cmp_to_key(mycomp))
    return tmp

def sample_output_files(name):
    tmp=glob('%s/documents/sample-*.sol' % name)
    tmp.sort()
    return tmp

def box_new(name):
    u"Create a blank tree for a new problem."
    shutil.copytree('.box/skel/', '%s/' % name, symlinks = True)

def box_build_pdf(name):
    u"Compile PDFs for all documents of problem `name`."
    ui.task_header(name, 'Compiling documents...')
    if not program_available('pdflatex'):
        ui.show_message('Error', 'Could not find `pdflatex`.', ERROR)
        hints.give_hint('pdflatex')
        return
    for tex_fn in glob('%s/documents/*.tex' % name):
        basename = os.path.basename(tex_fn)
        if basename.find('explain-') == 0 or basename.find('header.tex') == 0:
            continue
        pdf_fn = change_extension(tex_fn, 'pdf')
        build_pdf(pdf_fn, tex_fn)

def box_build_input(name):
    u"Build the input file for problem `name`."
    ui.task_header(name, 'Building generators...')
    build_binaries('%s/attic/' % name)
    ui.task_header(name, 'Generating input files...')

    clean.clean_build(name)
    if not os.path.exists('%s/build/' % name):
        os.mkdir('%s/build/' % name)
    if not os.path.exists('%s/build/tests/' % name):
        os.mkdir('%s/build/tests/' % name)
    ui.start_task('%s/attic/build-tests' % name)
    OK_msg,failed_msg,short='OK','failed',None
    my_env = os.environ.copy()
    my_env['ROOT'] = '%s' % name
    with NamedTemporaryFile('w') as error_file:
        error_file.write('test')
        try:
            res_proc = subprocess.check_call(['%s/attic/build-tests' % name],
                                         env = my_env, stderr = error_file)
            if res_proc == 0:
                ui.end_task(OK_msg,OK,short)
            else:
                ui.end_task(failed_msg,ERROR,short)
                print('\nError messages:\n---------------',file=sys.stderr)
                with open(error_file.name,'r') as efile:
                    print(efile.read(), file=sys.stderr)
                print('---------------', file=sys.stderr)
        except:
            ui.end_task(failed_msg,ERROR,short)
            print('\nError messages:\n---------------', file=sys.stderr)
            with open(error_file.name,'r') as efile:
                print(efile.read(), file=sys.stderr)
            print('---------------', file=sys.stderr)

    size=0
    for i in input_files(name):
        size+=os.path.getsize(i)
    print(' %d tests built (%s)' % (len(input_files(name)),sizeof_fmt(size)))

        
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def box_check_input(name):
    u"Check the input file for problem `name`."
    global short_mode

    def run_checker(checker_fn):
        u"Run a single checker program against the input file."
        ui.task_header(name, 'Validating input with %s...' % os.path.basename(checker_fn))
        if not os.access(checker_fn, os.X_OK):
            ui.show_message('Warning', '%s is not an executable.' % checker_fn, WARNING)
            return
        for input_fn in sample_input_files(name):
            if not short_mode:
                ui.start_task(input_fn)
            with open(input_fn, 'r') as input_file:
                with open('/dev/null', 'w') as dev_null:
                    if subprocess.call(checker_fn,
                                       stdin = input_file,
                                       stdout = dev_null,
                                       stderr = dev_null) != 0:
                        ui.end_task(failed_msg,ERROR,short)
                    else:
                        ui.end_task(OK_msg,OK,short)
        print(' (samples)')
        #ui.end_task(" (sample)\n",OK,short)
        ct = 0
        for test_group in input_files_sub(name):
            ct+=1
            print('Subtask {}: '.format(ct), end='')
            if(not short_mode):
                print()
            for input_fn in test_group:
                if not short_mode:
                    ui.start_task(input_fn)
                with open(input_fn, 'r') as input_file:
                    with open('/dev/null', 'w') as dev_null:
                        if subprocess.call(checker_fn,
                                        stdin = input_file,
                                        stdout = dev_null,
                                        stderr = dev_null) != 0:
                            ui.end_task(failed_msg,ERROR,short)
                        else:
                            ui.end_task(OK_msg,OK,short)
            if(short_mode):
                print()
        print('(tests)')
        #ui.end_task(" (tests)",OK,short)

    if short_mode:
        OK_msg,failed_msg,short='.','X','short'
    else:
        OK_msg,failed_msg,short='OK','failed',None
    ui.task_header(name, 'Building checkers...')
    build_binaries('%s/checkers/' % name)
    input_checkers = glob('%s/checkers/*.*exe' % name)
    input_checkers.sort()
    if not input_checkers:
        ui.show_message('Warning', 'No input checkers available.', WARNING)
        return
    for checker_fn in input_checkers:
        if checker_fn.find("output")>0:
            continue
        run_checker(checker_fn)
    if short: print()


def box_check_output(name):
    u"Check the output file for problem `name`."
    global short_mode

    def run_checker(checker_fn):
        u"Run a single checker program against the input file."
        ui.task_header(name, 'Validating output with %s...' % os.path.basename(checker_fn))
        if not os.access(checker_fn, os.X_OK):
            ui.show_message('Warning', '%s is not an executable.' % checker_fn, WARNING)
            return
        for output_fn in sample_output_files(name)+output_files(name):
            if not short_mode:
                ui.start_task(output_fn)
            with open(output_fn, 'r') as output_file:
                with open('/dev/null', 'w') as dev_null:
                    if subprocess.call(checker_fn,
                                       stdin = output_file,
                                       stdout = dev_null,
                                       stderr = dev_null) != 0:
                        ui.end_task(failed_msg,ERROR,short)
                    else:
                        ui.end_task(OK_msg,OK,short)

    if short_mode:
        OK_msg,failed_msg,short='.','X','short'
    else:
        OK_msg,failed_msg,short='OK','failed',None
    ui.task_header(name, 'Building checkers...')
    build_binaries('%s/checkers/' % name)
    output_checkers = glob('%s/checkers/*output*.*exe' % name)
    if not output_checkers:
        ui.show_message('Warning', 'No output checkers available.', WARNING)
        return
    for checker_fn in output_checkers:
        
        run_checker(checker_fn)
    if short: print()


def box_build_good_solutions(name):
    u"Compile all good solutions for problem `name`."
    ui.task_header(name, 'Building solutions...')
    build_binaries('%s/solutions/good/' % name)
    build_binaries('%s/solutions/pass/' % name)
    build_binaries('%s/solutions/checker/' % name)

def box_build_solutions(name):
    u"Compile all solutions for problem `name`."
    ui.task_header(name, 'Building solutions...')
    build_binaries('%s/solutions/good/' % name)
    build_binaries('%s/solutions/pass/' % name)
    build_binaries('%s/solutions/slow/' % name)
    build_binaries('%s/solutions/wrong/' % name)
    build_binaries('%s/solutions/checker/' % name)

def reference_solution(name):
    good_solutions = [solution for solution, status in solutions(name)
                      if status == 'AC']
    if not good_solutions:
        return None
    for s in good_solutions:
        if s.find('reference')>=0:
            return s
    return good_solutions[0]

def build_one_output(name, input_fn):
    output_fn = change_extension(input_fn, 'sol')
    delete_file(output_fn)

    checker_exec_file = os.path.join(name,'judge','judge.exe')
    checker = 'diff'
    if os.path.exists(checker_exec_file):
        checker = checker_exec_file                
    
    result = run_solution(reference_solution(name), input_fn, output_fn, checker=checker)

    return result.status == 'OK'

def box_build_output(name):
    u"Build output file for problem `name`."
    global short_mode
    if short_mode:
        OK_msg,failed_msg,short='.','X','short'
    else:
        OK_msg,failed_msg,short='OK','failed',None

    if reference_solution(name) is None:
        ui.task_header(name, 'Generating problem output...')
        ui.show_message('Error', 'No good solutions available.', ERROR)
        hints.give_hint('output-good-solutions')
        return False
    else:
        ui.task_header(name, 'Generating problem output with %s...' % os.path.basename(reference_solution(name)))
    for input_fn in input_files(name):
        output_fn = change_extension(input_fn, 'sol')
        if not short_mode:
            ui.start_task(output_fn)
        if build_one_output(name, input_fn):
            ui.end_task(OK_msg,OK,short)
        else:
            ui.end_task(failed_msg,ERROR,short)
    if short: print()
    return True


def box_report(name):
    def print_time_summary(lang,rtype,min_time_array,max_time_array,total_time_array):
        
        if rtype == 'primary':
            print('**** %s ****' % lang)
            if len(max_time_array)==0:
                print('No solutions')
                return 0
            time_limit=timelimit(max_time_array, lang)
            print('Number of solutions: %d' % len(max_time_array))
            #if time_limit > 2*math.ceil(max(1,4*min(max_time_array))):
            if max(max_time_array) > 4*min(max_time_array):
                print('Time limit calculated: %5.2fs (ATTENTION: significant differences in execution times!)' % time_limit)
            else:
                print('Time limit calculated: %5.2fs' % time_limit)
            print('Max. min. time: %5.2fs' % (max(min_time_array)) )
            print('Min. max. time: %5.2fs' % (min(max_time_array)) )
            print('Max. max. time: %5.2fs' % (max(max_time_array)))
            print('Min. tot. time: %5.2fs' % (min(total_time_array)))
            print('Max. tot. time: %5.2fs' % (max(total_time_array)))
            return len(max_time_array)
        else:
            time_limit=timelimit(max_time_array, lang)
            print('Time limit calculated using C/C++: %5.2fs' % time_limit)
            return 0
    
    context={}
    with open(os.path.join(f'{name}','attic','problem.desc'), "r") as f:
        exec(f.read(),context)
    print("\nSUMMARY - %s" % name)
    nsol = print_time_summary("C/C++",'primary',context['C'][0],context['C'][1],context['C'][2])
    if nsol == 0:
        print('For computing time limits you must provide at least one C/C++ correct solution')
    nsol = print_time_summary("Java",'primary',context['Java'][0],context['Java'][1],context['Java'][2])
    if nsol == 0:
        print_time_summary("Java",'secondary',context['C'][0],context['C'][1],context['C'][2])
    nsol = print_time_summary("Javascript",'primary',context['Javascript'][0],context['Javascript'][1],context['Javascript'][2])
    if nsol == 0:
        print_time_summary("Javascript",'secondary',context['C'][0],context['C'][1],context['C'][2])
    nsol = print_time_summary("Python",'primary',context['Python'][0],context['Python'][1],context['Python'][2])
    if nsol == 0:
        print_time_summary("Python",'secondary',context['C'][0],context['C'][1],context['C'][2])

def solutions(name,sol_groups=["good","pass","slow","wrong"]):
    if "good" in sol_groups:
        for sol_fn in sorted(glob('%s/solutions/good/*.*exe' % name)):
            yield sol_fn, 'AC'
    if "pass" in sol_groups:
        for sol_fn in sorted(glob('%s/solutions/pass/*.*exe' % name)):
            yield sol_fn, 'AC'
    if "wrong" in sol_groups:
        for sol_fn in sorted(glob('%s/solutions/wrong/*.*exe' % name)):
            yield sol_fn, 'WA'
    if "slow" in sol_groups:
        for sol_fn in sorted(glob('%s/solutions/slow/*.*exe' % name)):
            yield sol_fn, 'TLE'

def box_check_solutions(name, sol_groups, do_time=False, do_sample=False):
    u"Check all solutions for problem `name`."
    global short_mode

    def check_solution_language(fsolname):
        solname,ext = os.path.splitext(fsolname)
        sols = []
        if os.path.exists(solname+'.c'):
            sols.append('c/c++')
        if os.path.exists(solname+'.cpp'):
            sols.append('c/c++')
        if os.path.exists(solname+'.java'):
            sols.append('java')
        if os.path.exists(solname+'.js'):
            sols.append('javascript')
        if os.path.exists(solname+'.py'):
            sols.append('python')
        if len(sols) == 0:
            ui.show_message(name, "no solutions found for this name extension {}".format(fsolname), color = ERROR)
        elif len(sols) > 1:
            ui.show_message(name, "solutions with conflicting source name {}".format(fsolname), color = ERROR)
        else:
            return sols[0]

    def run_check(name,sol_group,checker,ctime_limit=100,jtime_limit=100,jstime_limit=100,ptime_limit=100):
        
        for sol_fn, expected in solutions(name,sol_group):
            cur_cref_solutions_time,cur_jref_solutions_time,cur_jsref_solutions_time,cur_pref_solutions_time=[],[],[],[]
            cur_cref_solutions_totaltime,cur_jref_solutions_totaltime,cur_jsref_solutions_totaltime,cur_pref_solutions_totaltime=[],[],[],[]
            solution_language=check_solution_language(sol_fn)
            basename, extension = os.path.splitext(sol_fn)
            mem_limit = 1024
            file_limit = 32 # mateus changed from 1 GB to 32 MB to avoid workers running out of disk space
            time_limit=ctime_limit

            if solution_language=='java':
                time_limit=jtime_limit
                mem_limit = 2048
            elif solution_language=='python':
                time_limit=ptime_limit
            if solution_language=='javascript':
                time_limit=jstime_limit

            if ctime_limit==100 and jtime_limit==100 and ptime_limit==100:
                # no time limit defined yet
                ui.task_header(name, 'Testing %s [%s,%s] on REAL input...' % (os.path.basename(sol_fn),sol_group,solution_language))
            else:
                ui.task_header(name, 'Testing %s [%s,%s] on REAL input (Time limit: %2.2f)...' % (os.path.basename(sol_fn),sol_group,solution_language, time_limit))

            ct = 0
            for test_group in input_files_sub(name):
                ct+=1
                print("Subtask {}: ".format(ct), end='')
                if(not short_mode):
                    print()
                for input_fn in test_group:

                    if not short_mode:
                        ui.start_task(input_fn)

                    result = run_solution(sol_fn, input_fn,
                                        reference_fn = change_extension(input_fn, 'sol'),
                                        checker = checker,
                                        time_limit=time_limit,mem_limit=mem_limit,file_limit=file_limit)
                    if result.status == 'RE':
                        msg = exec_msg
                        color = ERROR
                    elif result.status == 'TLE':
                        msg = timeout_msg
                        color = [WARNING, OK][expected == result.status]
                    elif result.status == 'WA':
                        msg = wrong_msg
                        color = [ERROR, OK][expected == 'WA']
                    elif result.status == 'AC':
                        color = [ERROR, OK][expected == 'AC']
                        msg = OK_msg
                    if do_time:
                        ui.end_task('%4.2fs ' % result.running_time, color, short)
                    else:
                        ui.end_task(msg, color, short)

                    if expected == 'AC':
                        if solution_language=='java':
                            cur_jref_solutions_time.append(result.running_time)
                        elif solution_language=='javascript':
                            cur_jsref_solutions_time.append(result.running_time)
                        elif solution_language=='python':
                            cur_pref_solutions_time.append(result.running_time)
                        else: # lang is c/c++
                            cur_cref_solutions_time.append(result.running_time)
                if(short_mode):
                    print()

            if len(cur_cref_solutions_time)!=0:
                cref_solutions_maxtime.append(max(cur_cref_solutions_time))
                cref_solutions_mintime.append(min(cur_cref_solutions_time))
                cref_solutions_totaltime.append(sum(cur_cref_solutions_time))
                print('Total time: %.2fs  (worst case: %.2fs)' %  (sum(cur_cref_solutions_time),max(cur_cref_solutions_time)))
            if len(cur_jref_solutions_time)!=0:
                jref_solutions_maxtime.append(max(cur_jref_solutions_time))
                jref_solutions_mintime.append(min(cur_jref_solutions_time))
                jref_solutions_totaltime.append(sum(cur_jref_solutions_time))
                print('Total time: %.2fs  (worst case: %.2fs)' %  (sum(cur_jref_solutions_time),max(cur_jref_solutions_time)))
            if len(cur_jsref_solutions_time)!=0:
                jsref_solutions_maxtime.append(max(cur_jsref_solutions_time))
                jsref_solutions_mintime.append(min(cur_jsref_solutions_time))
                jsref_solutions_totaltime.append(sum(cur_jsref_solutions_time))
                print('Total time: %.2fs  (worst case: %.2fs)' %  (sum(cur_jsref_solutions_time),max(cur_jsref_solutions_time)))
            if len(cur_pref_solutions_time)!=0:
                pref_solutions_maxtime.append(max(cur_pref_solutions_time))
                pref_solutions_mintime.append(min(cur_pref_solutions_time))
                pref_solutions_totaltime.append(sum(cur_pref_solutions_time))
                print('Total time: %.2fs  (worst case: %.2fs)' %  (sum(cur_pref_solutions_time),max(cur_pref_solutions_time)))

        return

    if short_mode:
        OK_msg,timeout_msg,wrong_msg,exec_msg,short='.','T','W','X','short'
    else:
        OK_msg,timeout_msg,wrong_msg,exec_msg,short='OK','timeout','wrong','failed',None
    # problem specs, to be read or calculated
    # using this only for the sample
    jtime_limit = 60
    jstime_limit = 60
    ctime_limit = 60
    ptime_limit = 60

    checker_exec_file = os.path.join(name,'judge','judge.exe')
    checker = 'diff'
    if os.path.exists(checker_exec_file):
        checker = checker_exec_file                


    
    if do_sample:
        for sol_fn, expected in solutions(name,"good"):
            solution_language=check_solution_language(sol_fn)
            ui.task_header(name, 'Testing %s [%s,%s] on sample input...' % (os.path.basename(sol_fn), "good", solution_language))
            for input_fn in sample_input_files(name):
                if not short_mode:
                    ui.start_task(input_fn)
                basename, extension = os.path.splitext(sol_fn)
                mem_limit = 1024
                file_limit = 1024
                if solution_language=='java':
                    time_limit=jtime_limit
                    mem_limit = 2048
                elif solution_language=='javascript':
                    time_limit=jstime_limit
                elif solution_language=='python':
                    time_limit=ptime_limit
                else:
                    time_limit=ctime_limit

                result = run_solution(sol_fn, input_fn,
                                  reference_fn = change_extension(input_fn, 'sol'),
                                      checker = checker,
                                  time_limit=time_limit,mem_limit=mem_limit,file_limit=file_limit)
                if result.status == 'RE':
                    #ui.end_task(exec_msg, ERROR, short)
                    ui.end_task(result.detail, ERROR, short)
                elif result.status == 'TLE':
                    color = [WARNING, OK][expected == result.status]
                    ui.end_task(timeout_msg, color, short)
                elif result.status == 'WA':
                    color = [ERROR, OK][expected == 'WA']
                    ui.end_task(wrong_msg, color, short)
                    hints.give_hint('solution-wrong-sample')
                elif result.status == 'AC':
                    color = [ERROR, OK][expected == 'AC']
                    ui.end_task(OK_msg, color, short)
                else:
                    assert False

    cref_solutions_maxtime,cref_solutions_mintime,cref_solutions_totaltime=[],[],[]
    jref_solutions_maxtime,jref_solutions_mintime,jref_solutions_totaltime=[],[],[]
    jsref_solutions_maxtime,jsref_solutions_mintime,jsref_solutions_totaltime=[],[],[]
    pref_solutions_maxtime,pref_solutions_mintime,pref_solutions_totaltime=[],[],[]
    if "good" in sol_groups:
        # will calculate time limits
        run_check(name,'good',checker)
        if short_mode: print()
        if len(cref_solutions_maxtime)==0: # no C solutions
            ui.show_message("Must have at least one C solution to calculate time limits!", ERROR)
        ctime_limit=timelimit(cref_solutions_maxtime, "C/C++")
        if len(jref_solutions_maxtime)==0: # no Java solutions
            jtime_limit=timelimit(cref_solutions_maxtime)
        else:
            jtime_limit=timelimit(jref_solutions_maxtime, "Java")
        if len(pref_solutions_maxtime)==0: # no Python solutions
            ptime_limit=timelimit(cref_solutions_maxtime)
        else:
            ptime_limit=timelimit(pref_solutions_maxtime, "Python")
        if len(jsref_solutions_maxtime)==0: # no Javascript solutions
            jstime_limit=timelimit(cref_solutions_maxtime)
        else:
            jstime_limit=timelimit(jsref_solutions_maxtime, "Javascript")

        # write time limits in file attic/problem.desc
        try:
            os.mkdir('%s/attic' % name)
        except:
            pass
        with open('%s/attic/problem.desc' % name, 'w') as desc_fn:
            desc_fn.write('time_limit_c=%2.2f\ntime_limit_java=%2.2f\ntime_limit_javascript=%2.2f\ntime_limit_python=%2.2f\n' % (ctime_limit, jtime_limit, jstime_limit,ptime_limit))
            desc_fn.write("C=(%s,%s,%s)\n" % (str(cref_solutions_mintime),str(cref_solutions_maxtime),str(cref_solutions_totaltime)))
            desc_fn.write("Java=(%s,%s,%s)\n" % (str(jref_solutions_mintime),str(jref_solutions_maxtime),str(jref_solutions_totaltime)))
            desc_fn.write("Javascript=(%s,%s,%s)\n" % (str(jsref_solutions_mintime),str(jsref_solutions_maxtime),str(jsref_solutions_totaltime)))
            desc_fn.write("Python=(%s,%s,%s)\n" % (str(pref_solutions_mintime),str(pref_solutions_maxtime),str(pref_solutions_totaltime)))
        box_report(name)
    
    # read time_limits from file attic/problem.desc if "good" not in sol_groups
    if not os.path.isfile('%s/attic/problem.desc' % name):
        ui.show_message('Error', 'Please run check-solutions-good before to calculate time limits.', ERROR)
        return
    context = {}
    with open(os.path.join(f'{name}','attic','problem.desc'), "r") as f:
        exec(f.read(),context)
    ct,jt,jst,pt = context['time_limit_c'],context['time_limit_java'],context['time_limit_javascript'],context['time_limit_python']

    if "pass" in sol_groups:
        run_check(name,'pass',checker,ct,jt,jst,pt)
        if short_mode: print()
    if "wrong" in sol_groups:
        run_check(name,'wrong',checker,ct,jt,jst,pt)
        if short_mode: print()
    if "slow" in sol_groups:
        run_check(name,'slow',checker,ct,jt,jst,pt)
        if short_mode: print()

def timelimit(times, lang = ""):
    try:
        maxtime=max(times)
        mintime=min(times)
    except:
        maxtime=0
        mintime=0
        return 0
    #return math.ceil(max(1, 3*mintime, 1.5*maxtime))
    #return max(0.1, 3*mintime, 2*maxtime)
    # for OBI, full disclosure
    # if len(times) > 1:
    #     tmp = max(0.01, 3.0*mintime, 2.5*maxtime)
    # else:
    #     tmp = max(0.01, 2.5*maxtime)
    # tmp = int(10*tmp)
    # tmp = tmp/10
    # return max(0.1, tmp)


    if lang == "Java":
        # when multiplying, ignore constant 0.3s needed just
        # to initialize the program
        maxtime = max(0.01, maxtime - 0.15)

    # new version to protect our infrastructure
    # and following what most olympiads do (2.5x slowest model sol)
    tl = math.ceil(maxtime * 25) / 10

    if tl > 4.0:
        if lang == "C/C++":
            ui.show_message("******", "Time limit in C++ cannot be above 4 seconds", color = ERROR)
        else:
            # lower multiplier to 1.4x for problems with runtime dominated by I/O
            tl = max(4.0, math.ceil(maxtime * 15) / 10)

    if lang == "Java":
        # Java has a lot of overhead, so using a different default
        # to be safe
        tl = max(0.4, tl)
    else:
        tl = max(0.2, tl)

    return tl

def oldtimelimit(times):
    try:
        maxtime=max(times)
    except:
        maxtime=0
    return max(math.floor(3*maxtime+0.8),1)


def parse_arguments():
    global short_mode
    short_mode=True
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'l:v')
    for flag, arg in optlist:
        if flag == '-l':
            sys.stdout.dumb_taps.append(open(arg, 'w'))
        if flag == '-v':
            short_mode=False
    last_dir = None
    while not os.path.exists('.box'):
        head, tail = os.getcwd(), None
        while not tail:
            head, tail = os.path.split(head)
        last_dir = tail
        os.chdir('..')
        if os.getcwd() == '/':
            ui.show_message('Error', 'Could not find .box/ directory.', ERROR)
            ui.usage()
    if last_dir:
        args.append(last_dir)
    try:
        cmd = args.pop(0)
    except IndexError:
        ui.usage()
    if args:
        targets = [arg.rstrip('/') for arg in args]
    else:
        targets = [directory.rstrip('/') for directory in glob('*/')]
    targets=sorted(targets)
    return cmd, targets

def _main():
    global short_mode
    cmd, targets = parse_arguments()

    if cmd == 'version':
        with open('.box/VERSION') as version_file:
            print('box %s' % (version_file.read(), ))
            sys.exit(0)

    if cmd == 'build-packages':
        box_build_package('warmup')
        box_build_package('contest')
        sys.exit(0)
    elif cmd == 'build-package-warmup':
        box_build_package('warmup')
        sys.exit(0)
    elif cmd == 'build-package-contest':
        box_build_package('contest')
        sys.exit(0)
    else:        
      for target in targets:
        clean.clean_backups(target)
        if cmd == 'new':
            box_new(target)
        elif cmd == 'build-pdf':
            box_build_pdf(target)
        elif cmd == 'build-input':
            box_build_input(target)
        elif cmd == 'build-output':
            box_build_output(target)
        elif cmd == 'build-solutions':
            box_build_solutions(target)
        elif cmd == 'check-solutions':
            box_check_solutions(target,["good","pass","slow","wrong"],do_sample=True)
        elif cmd == 'check-solutions-good':
            box_check_solutions(target,["good"],do_sample=True)
        elif cmd == 'check-solutions-pass':
            box_check_solutions(target,["pass"],do_sample=False)
        elif cmd == 'check-solutions-wrong':
            box_check_solutions(target,["wrong"],do_sample=False)
        elif cmd == 'check-solutions-slow':
            box_check_solutions(target,["slow"],do_sample=False)
        elif cmd == 'check-input':
            box_check_input(target)
        elif cmd == 'check-output':
            box_check_output(target)
        elif cmd == 'build':
            box_build_pdf(target)
            box_build_input(target)
            box_build_solutions(target)
            box_build_output(target)
        elif cmd == 'check':
            box_build_pdf(target)
            box_build_input(target)
            box_check_input(target)
            box_build_solutions(target)
            box_build_output(target)
            box_check_output(target)
            box_check_solutions(target,["good","pass","slow","wrong"],do_sample=True)
        elif cmd == 'check-good':
            box_build_pdf(target)
            box_build_input(target)
            box_check_input(target)
            box_build_solutions(target)
            box_build_output(target)
            box_check_output(target)
            box_check_solutions(target,["good"],do_sample=True)
        elif cmd == 'clean':
            clean.box_clean(target)
        elif cmd == 'report':
            box_report(target)
        elif cmd == 'time':
            box_check_solutions(target,["good","pass","slow"],do_time=True)
        elif cmd == 'time-good':
            box_check_solutions(target,["good"],do_time=True)
        elif cmd == 'time-pass':
            box_check_solutions(target,["pass"],do_time=True)
        elif cmd == 'time-slow':
            box_check_solutions(target,["slow"],do_time=True)
        elif cmd == 'time-wrong':
            box_check_solutions(target,["wrong"],do_time=True)
        elif cmd == 'build-fast':
            box_build_pdf(target)
            box_build_input(target)
            box_build_solutions(target)
            box_build_output(target)
            box_check_solutions(target,["good"],do_sample=True)
        elif cmd in ('commit', 'push', 'pull') and program_available('sl'):
            os.system('sl')
            sys.exit(1)
        else:
            ui.usage()
        hints.show_hints()

if __name__ == '__main__':
    _main()
