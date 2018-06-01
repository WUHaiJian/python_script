import sys
import os
import subprocess
import shutil
import re
current_dir = os.path.dirname(os.path.realpath(__file__))
MainTrunk_dir = "%s/%s" % (current_dir, "../../../")
GIT_FILE_0 = MainTrunk_dir + "sdk/source/core/enroll_verify/src/egis_fp_algmodule.c"
GIT_FILE_1 = MainTrunk_dir + "sdk/source/flow/egis_rbs_api.c"
GIT_FILE_0_old = "%s.old" % GIT_FILE_0
GIT_FILE_1_old = "%s.old" % GIT_FILE_1

SUPPORTED_PLATFORMS = ["normal", "trustonic", "teei", "qsee"]
fd = 0
PLATFORM = SUPPORTED_PLATFORMS[0]
SUPPORT_SAVE_IMAGE = "true"

def remove(file):
    os.remove(file)
    fd = open(file, "w+")

def config_macro(argv):
    #1. 
    remove("config.mk")
    #2. argv[1:]
    len = len(argv)
    if len == 1:
        #fd.write("PLATFORM=normal")
        #fd.write("SUPPORT_SAVE_IMAGE=true")
        pass
    elif len == 2 and argv[1] in SUPPORTED_PLATFORMS:
        PLATFORM = argv[1]
    elif len == 3 and argv[1] in SUPPORTED_PLATFORMS and argv[2] in ["true", "false"]:
        PLATFORM = argv[1]
        SUPPORT_SAVE_IMAGE = argv[2]
    
    fd.writelines("PLATFORM = %s", PLATFORM)
    fd.writelines("SUPPORT_SAVE_IMAGE = %s", SUPPORT_SAVE_IMAGE)
    fd.close()

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'])

def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short','HEAD'])

def get_git_branch_name():
    return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref','HEAD'])

def update_sha_to_log():
    id = get_git_revision_short_hash()
    name = get_git_branch_name()
    s_name = re.sub('[\r\n]', '', name)
    s_id = re.sub('[\r\n]', '', id)
    ver_ref = "%s-%s" % (s_name, s_id)
    print ver_ref
    
    r_s = r'"GIT_SHA1 = UNKNOWN");'
    r_d = r'"GIT_SHA1 = %s");' % ver_ref
    GIT_FILE_0_temp = "%s.temp" % GIT_FILE_0
    GIT_FILE_1_temp = "%s.temp" % GIT_FILE_1

    fd_0_temp = open(GIT_FILE_0_temp, "w+")
    fd_1_temp = open(GIT_FILE_1_temp, "w+")
    fd_0 = open(GIT_FILE_0)
    fd_1 = open(GIT_FILE_1)
    lines_0 = fd_0.readlines()
    lines_1 = fd_1.readlines()
    for s in lines_0:
        if r_s in s:
            fd_0_temp.writelines(s.replace(r_s, r_d))
        else:
            fd_0_temp.write(s)
    for it in lines_1:
        if r_s in it:
            fd_1_temp.writelines(it.replace(r_s, r_d))
        else:
            fd_1_temp.write(it);
    fd_0.close()
    fd_1.close()
    fd_0_temp.close()
    fd_1_temp.close()

    shutil.move(GIT_FILE_0, GIT_FILE_0_old)
    shutil.move(GIT_FILE_1, GIT_FILE_1_old)
    shutil.move(GIT_FILE_0_temp, GIT_FILE_0)
    shutil.move(GIT_FILE_1_temp, GIT_FILE_1)

def checkout_file(mode):
    if mode == True:
        check_0 = "git checkout %s" % (GIT_FILE_0)
        check_1 = "git checkout %s" % (GIT_FILE_1)
        os.system(check_0)
        os.system(check_1)
    else:
        shutil.move(GIT_FILE_0_old, GIT_FILE_0)
        shutil.move(GIT_FILE_1_old, GIT_FILE_1)

def build():
    build_cmd = "ndk-build \
    -B \
    NDK_DEBUG=1 \
    NDK_PROJECT_PATH=. \
    NDK_APPLICATION_MK=Application.mk \
    NDK_APP_OUT=Out/_build \
    APP_BUILD_SCRIPT=Android_flow.mk \
    APP_ABI=arm64-v8a"
    
    os.system(build_cmd)
    
#build()
    
if __name__ == '__main__':
    update_sha_to_log()
    build()
    checkout_file(False)
    #name = get_git_branch_name()
    #s = re.sub('[\r\n]', '', name)
    #print list(s)

    