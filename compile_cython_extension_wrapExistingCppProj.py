# Copyright (C) 2019 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.
import glob
import os
import shutil
import subprocess
import sys
import fire

# dirs_headers_include_additional = []
# dirs_libs_link_additional = []
# fpaths_dlls_additional = []
dirs_headers_include_additional = [r"D:\OpenCV\opencv-4.0.1-vc14_vc15\opencv\build\include"]
dirs_libs_link_additional = [r"D:\OpenCV\opencv-4.0.1-vc14_vc15\opencv\build\x64\vc15\lib\opencv_world401.lib"]
fpaths_dlls_additional = [r"D:\OpenCV\opencv-4.0.1-vc14_vc15\opencv\build\x64\vc15\bin\opencv_world401.dll"]
include_numpy_dependency = False

def compile_cython_project(dir_proj):

    # values need to be specified by user
    dir_proj = r"D:\Python_Libs\kkh\computer_vision\feature_extraction\hog\hog_dollar\build"
    dirs_headers_include_additional = []
    dirs_libs_link_additional = []
    fpaths_dlls_additional = []
    dirs_headers_include_additional = [r"D:\OpenCV\opencv-4.0.1-vc14_vc15\opencv\build\include"]
    dirs_libs_link_additional = [r"D:\OpenCV\opencv-4.0.1-vc14_vc15\opencv\build\x64\vc15\lib\opencv_world401.lib"]
    fpaths_dlls_additional = [r"D:\OpenCV\opencv-4.0.1-vc14_vc15\opencv\build\x64\vc15\bin\opencv_world401.dll"]

    path_cython_exe = r"D:\Anaconda3\envs\deep_learning\Scripts\cython.exe"
    fpath_vcvarsall_bat = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat'
    param_arch_for_vcvarsall_bat = 'amd64'
    fpath_cl_exe = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\cl.exe"
    #fpath_link_exe = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\link.exe"
    dirs_headers_include_interpreter = [r'D:\Anaconda3\envs\deep_learning\include']
    dirs_libs_link_interpreter = [r"D:\Anaconda3\envs\deep_learning\libs\python36.lib"]
    if include_numpy_dependency:
        dirs_headers_include_interpreter.append(r'D:\Anaconda3\envs\deep_learning\Lib\site-packages\numpy\core\include')
        dirs_libs_link_interpreter.append(r"D:\Anaconda3\envs\deep_learning\Lib\site-packages\numpy\core\lib\npymath.lib")
    cpp_source_extensions = ['*.cpp', '*c']
    cpp_header_extensions = ['*.h', '*.hpp']
    # cpp_header_extensions = ['*.h', '*.hpp', '*.tc', '*.th']

    # values fixed (i.e. not to be changed by user)
    fpaths_pyx_files = glob.glob(os.path.join(dir_proj, '*.pyx'))
    if len(fpaths_pyx_files) != 1:
        raise ValueError('There must be exactly one pyx file in the project file')
    fpath_pyx_file = fpaths_pyx_files[0]
    dir_output = os.path.join(dir_proj, 'output')
    dir_working = os.path.join(dir_proj, 'working')
    desired_output_file_extensions = ['*.pyd']
    extension_output_dll = 'pyd'
    name_module = os.path.splitext(os.path.basename(fpath_pyx_file))[0]
    name_cpp_gen_cython = name_module+'.cpp'
    name_output_dll = name_module + '.' + extension_output_dll

    # create the working directory inside the project folder
    if not os.path.exists(dir_working):
        os.mkdir(dir_working)

    # create the output directory inside the project folder
    if not os.path.exists(dir_output):
        os.mkdir(dir_output)

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

    # copy all C/C++ source and header files in the project directory to working directory
    # for source files, will record the file names so that they can be compiled later on
    names_cpp_sources_to_compile = []
    for ext in cpp_source_extensions:
        fpaths_files = glob.glob(os.path.join(dir_proj, ext))
        for f in fpaths_files:
            names_cpp_sources_to_compile.append(os.path.basename(f))
            shutil.copy(f, dir_working)
    names_cpp_sources_to_compile = ' '.join(names_cpp_sources_to_compile)
    # for header files, just copy to the working directory
    for ext in cpp_header_extensions:
        fpaths_files = glob.glob(os.path.join(dir_proj, ext))
        for f in fpaths_files:
            shutil.copy(f, dir_working)

    # run cython
    subprocess.call([path_cython_exe, '--cplus', os.path.basename(fpath_pyx_file)], cwd=dir_working, shell=False)

    # build the generated cpp files using VISUAL STUDIO
    str_cmd_headers_include = []
    for d in dirs_headers_include_interpreter:
        str_cmd_headers_include.append('-I"{}"'.format(d))
    for d in dirs_headers_include_additional:
        str_cmd_headers_include.append('-I"{}"'.format(d))
    str_cmd_headers_include = ' '.join(str_cmd_headers_include)

    str_cmd_libs_link = []
    for d in dirs_libs_link_interpreter:
        str_cmd_libs_link.append('"{}"'.format(d))
    for d in dirs_libs_link_additional:
        str_cmd_libs_link.append('"{}"'.format(d))
    str_cmd_libs_link = ' '.join(str_cmd_libs_link)

    fpath_compile_batch_file = os.path.join(dir_working, 'compile_commands.cmd')
    with open(fpath_compile_batch_file, 'w') as fid_out:
        fid_out.write(f'''call "{fpath_vcvarsall_bat}" {param_arch_for_vcvarsall_bat}\n''')
        fid_out.write(f''' "{fpath_cl_exe}" /GS /GL /W3 /Gy /Fo"{dir_working + '/'}" /Fa"{dir_working + '/'}" /Zc:wchar_t {str_cmd_headers_include} /Zi /Gm- /O2 /sdl /Fd"vc140.pdb" /Zc:inline /fp:precise /D "NDEBUG" /D "_WINDOWS" /D "_USRDLL" /D "GENERATE_DLL_EXPORTS" /D "_WINDLL" /D "_UNICODE" /D "UNICODE" /errorReport:prompt /WX- /Zc:forScope /Gd /Oi /MD /EHsc /nologo /Fp"{name_module}.pch" {name_cpp_gen_cython} {names_cpp_sources_to_compile} /link /OUT:"{name_output_dll}" /MANIFEST /LTCG:incremental /NXCOMPAT /DYNAMICBASE {str_cmd_libs_link} "kernel32.lib" "user32.lib" "gdi32.lib" "winspool.lib" "comdlg32.lib" "advapi32.lib" "shell32.lib" "ole32.lib" "oleaut32.lib" "uuid.lib" "odbc32.lib" "odbccp32.lib" /IMPLIB:"{name_module}.lib" /DEBUG /DLL /MACHINE:X64 /OPT:REF /INCREMENTAL:NO /SUBSYSTEM:WINDOWS /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /ManifestFile:"{name_module}.dll.intermediate.manifest" /OPT:ICF /ERRORREPORT:PROMPT /NOLOGO /TLBID:1\n''')
    subprocess.call(fpath_compile_batch_file, cwd=dir_working, shell=False)

    # copy the desired compiled files from working folder to output folder
    for d in desired_output_file_extensions:
        fpaths_desired = glob.glob(os.path.join(dir_working, d))
        for f in fpaths_desired:
            shutil.copy(f, dir_output)

    # copy the necessary dlls (from linked in this project) to output directory
    for f in fpaths_dlls_additional:
        shutil.copy(f, dir_output)


if __name__ == '__main__':
    #fire.Fire(compile_cython_project)
    compile_cython_project('D:\\Python_Libs\\kkh\\computer_vision\\feature_extraction\\hog\\hog_dollar\\build')