# Copyright (C) 2019 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.
import glob
import os
import shutil
import subprocess
import sys

# values need to be specified by user
fpath_pyx_file = r"C:\Users\Kyaw\Desktop\New folder (16)\cython\cython1.pyx"
path_cython_exe = r"D:\Anaconda3\envs\deep_learning\Scripts\cython.exe"
fpath_vcvarsall_bat = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat'
param_arch_for_vcvarsall_bat = 'amd64'
fpath_cl_exe = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\cl.exe"
fpath_link_exe = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\link.exe"
dirs_headers_include_interpreter = [r'D:\Anaconda3\envs\deep_learning\include']
dirs_libs_link_interpreter = [r"D:\Anaconda3\envs\deep_learning\libs\python36.lib"]

# values fixed (i.e. not to be changed by user)
dir_output = os.path.dirname(fpath_pyx_file)
dir_working = os.path.join(dir_output, 'working')
desired_output_file_extensions = ['*.pyd']
extension_output_dll = 'pyd'
name_module = os.path.splitext(os.path.basename(fpath_pyx_file))[0]
name_cpp_gen_cython = name_module+'.cpp'
name_output_dll = name_module + '.' + extension_output_dll

# create the working directory inside the output folder
if not os.path.exists(dir_working):
    os.mkdir(dir_working)

# copy the pyx file to working directory
shutil.copy(fpath_pyx_file, dir_working)

# copy all the *.pxi and *.pxd files in the directory of fpath_pyx_file to working directory
dir_pyx_file = os.path.dirname(fpath_pyx_file)
fpaths_pxi_files = glob.glob(os.path.join(dir_pyx_file, '*.pxi'))
fpaths_pxd_files = glob.glob(os.path.join(dir_pyx_file, '*.pxd'))
for f in fpaths_pxi_files:
    shutil.copy(f, dir_working)
for f in fpaths_pxd_files:
    shutil.copy(f, dir_working)


# run cython
subprocess.call([path_cython_exe, '--cplus', os.path.basename(fpath_pyx_file)], cwd=dir_working, shell=False)

# build the generated cpp files using VISUAL STUDIO
str_cmd_headers_include = []
for d in dirs_headers_include_interpreter:
    str_cmd_headers_include.append('-I"{}"'.format(d))
str_cmd_headers_include = ' '.join(str_cmd_headers_include)

str_cmd_libs_link = []
for d in dirs_libs_link_interpreter:
    str_cmd_libs_link.append('"{}"'.format(d))
str_cmd_libs_link = ' '.join(str_cmd_libs_link)

fpath_compile_batch_file = os.path.join(dir_working, 'compile_commands.cmd')
with open(fpath_compile_batch_file, 'w') as fid_out:
    fid_out.write(f'''call "{fpath_vcvarsall_bat}" {param_arch_for_vcvarsall_bat}\n''')
    fid_out.write(f''' "{fpath_cl_exe}" /GS /GL /W3 /Gy /Fo"{os.path.join(dir_working, name_module+'.obj')}" /Fa"{os.path.join(dir_working, name_module+'.asm')}" /Zc:wchar_t {str_cmd_headers_include} /Zi /Gm- /O2 /sdl /Fd"vc140.pdb" /Zc:inline /fp:precise /D "NDEBUG" /D "_WINDOWS" /D "_USRDLL" /D "GENERATE_DLL_EXPORTS" /D "_WINDLL" /D "_UNICODE" /D "UNICODE" /errorReport:prompt /WX- /Zc:forScope /Gd /Oi /MD /EHsc /nologo /Fp"{name_module}.pch" {name_cpp_gen_cython} /link /OUT:"{name_output_dll}" /MANIFEST /LTCG:incremental /NXCOMPAT /DYNAMICBASE {str_cmd_libs_link} "kernel32.lib" "user32.lib" "gdi32.lib" "winspool.lib" "comdlg32.lib" "advapi32.lib" "shell32.lib" "ole32.lib" "oleaut32.lib" "uuid.lib" "odbc32.lib" "odbccp32.lib" /IMPLIB:"{name_module}.lib" /DEBUG /DLL /MACHINE:X64 /OPT:REF /INCREMENTAL:NO /SUBSYSTEM:WINDOWS /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /ManifestFile:"{name_module}.dll.intermediate.manifest" /OPT:ICF /ERRORREPORT:PROMPT /NOLOGO /TLBID:1\n''')
subprocess.call(fpath_compile_batch_file, cwd=dir_working, shell=False)

# copy the desired compiled files from working folder to output folder
for d in desired_output_file_extensions:
    fpaths_desired = glob.glob(os.path.join(dir_working, d))
    for f in fpaths_desired:
        shutil.copy(f, dir_output)

