# Copyright 2012-2017 The Meson development team

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path, subprocess

from ..mesonlib import EnvironmentException

from .cpp import CPPCompiler
from .compilers import ClangCompiler, GnuCompiler

class ObjCPPCompiler(CPPCompiler):
    def __init__(self, exelist, version, is_cross, exe_wrap):
        self.language = 'objcpp'
        CPPCompiler.__init__(self, exelist, version, is_cross, exe_wrap)

    def get_display_language(self):
        return 'Objective-C++'

    def sanity_check(self, work_dir, environment):
        # TODO try to use sanity_check_impl instead of duplicated code
        source_name = os.path.join(work_dir, 'sanitycheckobjcpp.mm')
        binary_name = os.path.join(work_dir, 'sanitycheckobjcpp')
        with open(source_name, 'w') as ofile:
            ofile.write('#import<stdio.h>\n'
                        'class MyClass;'
                        'int main(int argc, char **argv) { return 0; }\n')
        pc = subprocess.Popen(self.exelist + [source_name, '-o', binary_name])
        pc.wait()
        if pc.returncode != 0:
            raise EnvironmentException('ObjC++ compiler %s can not compile programs.' % self.name_string())
        if self.is_cross:
            # Can't check if the binaries run so we have to assume they do
            return
        pe = subprocess.Popen(binary_name)
        pe.wait()
        if pe.returncode != 0:
            raise EnvironmentException('Executables created by ObjC++ compiler %s are not runnable.' % self.name_string())


class GnuObjCPPCompiler(GnuCompiler, ObjCPPCompiler):
    def __init__(self, exelist, version, compiler_type, is_cross, exe_wrapper=None, defines=None):
        ObjCPPCompiler.__init__(self, exelist, version, is_cross, exe_wrapper)
        GnuCompiler.__init__(self, compiler_type, defines)
        default_warn_args = ['-Wall', '-Winvalid-pch', '-Wnon-virtual-dtor']
        self.warn_args = {'0': [],
                          '1': default_warn_args,
                          '2': default_warn_args + ['-Wextra'],
                          '3': default_warn_args + ['-Wextra', '-Wpedantic']}


class ClangObjCPPCompiler(ClangCompiler, ObjCPPCompiler):
    def __init__(self, exelist, version, compiler_type, is_cross, exe_wrapper=None):
        ObjCPPCompiler.__init__(self, exelist, version, is_cross, exe_wrapper)
        ClangCompiler.__init__(self, compiler_type)
        default_warn_args = ['-Wall', '-Winvalid-pch', '-Wnon-virtual-dtor']
        self.warn_args = {'0': [],
                          '1': default_warn_args,
                          '2': default_warn_args + ['-Wextra'],
                          '3': default_warn_args + ['-Wextra', '-Wpedantic']}
        self.base_options = ['b_pch', 'b_lto', 'b_pgo', 'b_sanitize', 'b_coverage']
