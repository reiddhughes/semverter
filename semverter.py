import abc
import functools
import os
import pkgutil
import re
import sys
import typing
import types
import inspect
import warnings
import logging
from importlib import util

VERSION = "HELLLO123"


class Loggerator(object):

    def __init__(self):
        _current_file_name_with_extension = os.path.basename(__file__)
        self._library_name, _ = os.path.splitext(
            _current_file_name_with_extension
        )
        self._logger = None

    def log_class(self, decorated_class):
        for single_member_name, single_member_value in inspect.getmembers(
                decorated_class
        ):

            if inspect.isfunction(single_member_value):
                if re.match('^_[A-Za-z].*', single_member_name):
                    decorated_function =self._decorate_function_with_debug(
                        func=single_member_value
                    )

                    setattr(
                        decorated_class,
                        single_member_name,
                        decorated_function
                    )

                elif not single_member_name.startswith('__'):
                    decorated_function =self._decorate_function_with_info(
                        func=single_member_value
                    )

                    setattr(
                        decorated_class,
                        single_member_name,
                        decorated_function
                    )

        return decorated_class

    def _retrieve_logger(self):
        if self._logger:
            logger = self._logger
        else:
            logger = logging.getLogger(self._library_name)
            logger.addHandler(logging.NullHandler())
            self._logger = logger

        return logger

    @staticmethod
    def _assemble_args(args):
        string_args = [str(single_arg) for single_arg in args]
        joined_args = ", ".join(string_args)

        return joined_args

    @staticmethod
    def _assemble_kwargs(kwargs):
        kwarg_strings = []

        for single_name, single_value in kwargs.items():
            single_kwarg_string = str(single_name) + "=" + str(single_value)
            kwarg_strings.append(single_kwarg_string)

        joined_kwarg_strings = ", ".join(kwarg_strings)

        return joined_kwarg_strings

    def _assemble_parameters(self, args, kwargs):
        parameter_parts = []

        if args:
            assembled_args = self._assemble_args(args=args)
            parameter_parts.append(assembled_args)

        if kwargs:
            assembled_kwargs = self._assemble_kwargs(kwargs=kwargs)
            parameter_parts.append(assembled_kwargs)

        assembled_parameters = ", ".join(parameter_parts)

        return assembled_parameters

    def _create_function_call_message(self, func, args, kwargs):
        message_template = "Called {qualname}({assembled_parameters})"
        assembled_parameters = self._assemble_parameters(
            args=args,
            kwargs=kwargs
        )

        message = message_template.format(
            qualname=func.__qualname__,
            assembled_parameters=assembled_parameters
        )

        return message

    def _create_function_return_message(self, func, args, kwargs, result):
        message_template = "{qualname}({assembled_parameters}) returned {result}"
        assembled_parameters = self._assemble_parameters(
            args=args,
            kwargs=kwargs
        )

        message = message_template.format(
            qualname=func.__qualname__,
            assembled_parameters=assembled_parameters,
            result=str(result)
        )

        return message

    def _log_call(self, log_strategy, func, args, kwargs):
        call_message = self._create_function_call_message(
            func=func,
            args=args,
            kwargs=kwargs
        )

        log_strategy(call_message)

    def _log_return(self, log_strategy, func, args, kwargs, result):
        return_message = self._create_function_return_message(
            func=func,
            args=args,
            kwargs=kwargs,
            result=result
        )

        log_strategy(return_message)

    def _decorate_function_with_info(self, func):

        @functools.wraps(func)
        def _log_info(*args, **kwargs):
            args_without_self = args[1:]
            logger = self._retrieve_logger()
            self._log_call(
                log_strategy=logger.info,
                func=func,
                args=args_without_self,
                kwargs=kwargs
            )

            signature = inspect.signature(func)

            if len(signature.parameters) < len(args) + len(kwargs):
                result = func(*args_without_self, **kwargs)
            else:
                result = func(*args, **kwargs)

            self._log_return(
                log_strategy=logger.info,
                func=func,
                args=args_without_self,
                kwargs=kwargs,
                result=result
            )

            return result

        return _log_info

    def _decorate_function_with_debug(self, func):

        @functools.wraps(func)
        def _debug_info(*args, **kwargs):
            args_without_self = args[1:]
            logger = self._retrieve_logger()
            self._log_call(
                log_strategy=logger.debug,
                func=func,
                args=args_without_self,
                kwargs=kwargs
            )

            signature = inspect.signature(func)

            if len(signature.parameters) < len(args) + len(kwargs):
                result = func(*args_without_self, **kwargs)
            else:
                result = func(*args, **kwargs)

            self._log_return(
                log_strategy=logger.debug,
                func=func,
                args=args_without_self,
                kwargs=kwargs,
                result=result
            )

            return result

        return _debug_info


_T = typing.TypeVar('_T')
PUBLIC_PATTERN = re.compile('^[A-Za-z].*')
_loggerator = Loggerator()


@_loggerator.log_class
class MagicMethods(object):
    _MAGIC_METHODS = {
        '__abs__',
        '__add__',
        '__and__',
        '__call__',
        '__class__',
        '__cmp__',
        '__coerce__',
        '__complex__',
        '__contains__',
        '__del__',
        '__delattr__',
        '__delete__',
        '__delitem__',
        '__delslice__',
        '__dict__',
        '__div__',
        '__divmod__',
        '__eq__',
        '__float__',
        '__floordiv__',
        '__ge__',
        '__get__',
        '__getattr__',
        '__getattribute__',
        '__getitem__',
        '__getslice__',
        '__gt__',
        '__hash__',
        '__hex__',
        '__iadd__',
        '__iand__',
        '__idiv__',
        '__ifloordiv__',
        '__ilshift__',
        '__imod__',
        '__imul__',
        '__index__',
        '__init__',
        '__instancecheck__',
        '__int__',
        '__invert__',
        '__ior__',
        '__ipow__',
        '__irshift__',
        '__isub__',
        '__iter__',
        '__itruediv__',
        '__ixor__',
        '__le__',
        '__len__',
        '__long__',
        '__lshift__',
        '__lt__',
        '__metaclass__',
        '__mod__',
        '__mro__',
        '__mul__',
        '__ne__',
        '__neg__',
        '__new__',
        '__nonzero__',
        '__oct__',
        '__or__',
        '__pos__',
        '__pow__',
        '__radd__',
        '__rand__',
        '__rcmp__',
        '__rdiv__',
        '__rdivmod__',
        '__repr__',
        '__reversed__',
        '__rfloordiv__',
        '__rlshift__',
        '__rmod__',
        '__rmul__',
        '__ror__',
        '__rpow__',
        '__rrshift__',
        '__rshift__',
        '__rsub__',
        '__rtruediv__',
        '__rxor__',
        '__set__',
        '__setattr__',
        '__setitem__',
        '__setslice__',
        '__slots__',
        '__str__',
        '__sub__',
        '__subclasscheck__',
        '__truediv__',
        '__unicode__',
        '__weakref__',
        '__xor__'
    }

    @classmethod
    def check_if_is_magic_method(cls, name):
        is_magic_method = name in cls._MAGIC_METHODS

        return is_magic_method


MAGIC_METHODS = MagicMethods()

@_loggerator.log_class
class LanguageModules(object):

    def __init__(self):
        self._all_language_modules = self._import_all_language_modules()

    @staticmethod
    def _import_all_language_modules() -> typing.Set[types.ModuleType]:
        # Not including __main__ because it is a module that should be explored.
        language_module_names = [
            "__future__",
            "_dummy_thread",
            "_thread",
            "abc",
            "aifc",
            "argparse",
            "array",
            "ast",
            "asynchat",
            "asyncio",
            "asyncore",
            "atexit",
            "audioop",
            "base64",
            "bdb",
            "binascii",
            "binhex",
            "bisect",
            "builtins",
            "bz2",
            "calendar",
            "cgi",
            "cgitb",
            "chunk",
            "cmath",
            "cmd",
            "code",
            "codecs",
            "codeop",
            "collections",
            "collections.abc",
            "colorsys",
            "compileall",
            "concurrent",
            "concurrent.futures",
            "configparser",
            "contextlib",
            "contextvars",
            "copy",
            "copyreg",
            "cProfile",
            "crypt",
            "csv",
            "ctypes",
            "curses",
            "curses.ascii",
            "curses.panel",
            "curses.textpad",
            "dataclasses",
            "datetime",
            "dbm",
            "dbm.dumb",
            "dbm.gnu",
            "dbm.ndbm",
            "decimal",
            "difflib",
            "dis",
            "distutils",
            "distutils.archive_util",
            "distutils.bcppcompiler",
            "distutils.ccompiler",
            "distutils.cmd",
            "distutils.command",
            "distutils.command.bdist",
            "distutils.command.bdist_dumb",
            "distutils.command.bdist_msi",
            "distutils.command.bdist_packager",
            "distutils.command.bdist_rpm",
            "distutils.command.bdist_wininst",
            "distutils.command.build",
            "distutils.command.build_clib",
            "distutils.command.build_ext",
            "distutils.command.build_py",
            "distutils.command.build_scripts",
            "distutils.command.check",
            "distutils.command.clean",
            "distutils.command.config",
            "distutils.command.install",
            "distutils.command.install_data",
            "distutils.command.install_headers",
            "distutils.command.install_lib",
            "distutils.command.install_scripts",
            "distutils.command.register",
            "distutils.command.sdist",
            "distutils.core",
            "distutils.cygwinccompiler",
            "distutils.debug",
            "distutils.dep_util",
            "distutils.dir_util",
            "distutils.dist",
            "distutils.errors",
            "distutils.extension",
            "distutils.fancy_getopt",
            "distutils.file_util",
            "distutils.filelist",
            "distutils.log",
            "distutils.msvccompiler",
            "distutils.spawn",
            "distutils.sysconfig",
            "distutils.text_file",
            "distutils.unixccompiler",
            "distutils.util",
            "distutils.version",
            "doctest",
            "dummy_threading",
            "email",
            "email.charset",
            "email.contentmanager",
            "email.encoders",
            "email.errors",
            "email.generator",
            "email.header",
            "email.headerregistry",
            "email.iterators",
            "email.message",
            "email.mime",
            "email.parser",
            "email.policy",
            "email.utils",
            "encodings",
            "encodings.idna",
            "encodings.mbcs",
            "encodings.utf_8_sig",
            "ensurepip",
            "enum",
            "errno",
            "faulthandler",
            "fcntl",
            "filecmp",
            "fileinput",
            "fnmatch",
            "formatter",
            "fractions",
            "ftplib",
            "functools",
            "gc",
            "getopt",
            "getpass",
            "gettext",
            "glob",
            "grp",
            "gzip",
            "hashlib",
            "heapq",
            "hmac",
            "html",
            "html.entities",
            "html.parser",
            "http",
            "http.client",
            "http.cookiejar",
            "http.cookies",
            "http.server",
            "imaplib",
            "imghdr",
            "imp",
            "importlib",
            "importlib.abc",
            "importlib.machinery",
            "importlib.resources",
            "importlib.util",
            "inspect",
            "io",
            "ipaddress",
            "itertools",
            "json",
            "json.tool",
            "keyword",
            "lib2to3",
            "linecache",
            "locale",
            "logging",
            "logging.config",
            "logging.handlers",
            "lzma",
            "macpath",
            "mailbox",
            "mailcap",
            "marshal",
            "math",
            "mimetypes",
            "mmap",
            "modulefinder",
            "msilib",
            "msvcrt",
            "multiprocessing",
            "multiprocessing.connection",
            "multiprocessing.dummy",
            "multiprocessing.managers",
            "multiprocessing.pool",
            "multiprocessing.sharedctypes",
            "netrc",
            "nis",
            "nntplib",
            "numbers",
            "operator",
            "optparse",
            "os",
            "os.path",
            "ossaudiodev",
            "parser",
            "pathlib",
            "pdb",
            "pickle",
            "pickletools",
            "pipes",
            "pkgutil",
            "platform",
            "plistlib",
            "poplib",
            "posix",
            "pprint",
            "profile",
            "pstats",
            "pty",
            "pwd",
            "py_compile",
            "pyclbr",
            "pydoc",
            "queue",
            "quopri",
            "random",
            "re",
            "readline",
            "reprlib",
            "resource",
            "rlcompleter",
            "runpy",
            "sched",
            "secrets",
            "select",
            "selectors",
            "shelve",
            "shlex",
            "shutil",
            "signal",
            "site",
            "smtpd",
            "smtplib",
            "sndhdr",
            "socket",
            "socketserver",
            "spwd",
            "sqlite3",
            "ssl",
            "stat",
            "statistics",
            "string",
            "stringprep",
            "struct",
            "subprocess",
            "sunau",
            "symbol",
            "symtable",
            "sys",
            "sysconfig",
            "syslog",
            "tabnanny",
            "tarfile",
            "telnetlib",
            "tempfile",
            "termios",
            "test",
            "test.support",
            "test.support.script_helper",
            "textwrap",
            "threading",
            "time",
            "timeit",
            "tkinter",
            "tkinter.scrolledtext",
            "tkinter.tix",
            "tkinter.ttk",
            "token",
            "tokenize",
            "trace",
            "traceback",
            "tracemalloc",
            "tty",
            "turtle",
            "turtledemo",
            "types",
            "typing",
            "unicodedata",
            "unittest",
            "unittest.mock",
            "urllib",
            "urllib.error",
            "urllib.parse",
            "urllib.request",
            "urllib.response",
            "urllib.robotparser",
            "uu",
            "uuid",
            "venv",
            "warnings",
            "wave",
            "weakref",
            "webbrowser",
            "winreg",
            "winsound",
            "wsgiref",
            "wsgiref.handlers",
            "wsgiref.headers",
            "wsgiref.simple_server",
            "wsgiref.util",
            "wsgiref.validate",
            "xdrlib",
            "xml",
            "xml.dom",
            "xml.dom.minidom",
            "xml.dom.pulldom",
            "xml.etree.ElementTree",
            "xml.parsers.expat",
            "xml.parsers.expat.errors",
            "xml.parsers.expat.model",
            "xml.sax",
            "xml.sax.handler",
            "xml.sax.saxutils",
            "xml.sax.xmlreader",
            "xmlrpc",
            "xmlrpc.client",
            "xmlrpc.server",
            "zipapp",
            "zipfile",
            "zipimport",
            "zlib"
        ]

        language_modules = set()

        for single_module_name in language_module_names:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning)

                try:
                    single_module = __import__(single_module_name)
                    language_modules.add(single_module)
                except ImportError:
                    pass

        return language_modules

    def check_if_is_language_module(self, value: types.ModuleType):
        is_language_module = (
                inspect.ismodule(value)
                and value in self._all_language_modules
        )

        return is_language_module


LANGUAGE_MODULES = LanguageModules()

@_loggerator.log_class
class SubCallSupplier(abc.ABC):

    @abc.abstractmethod
    def supply_next_sub_calls(self, api_exploration: 'ApiExploration') -> None:
        pass


@_loggerator.log_class
class Call(SubCallSupplier):

    @abc.abstractmethod
    def __eq__(self, other: 'Call') -> bool:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass


@_loggerator.log_class
class Module(Call):

    def __init__(self, name: str, value: types.ModuleType):
        self._name = name
        self._value = value

    def supply_next_sub_calls(self, api_exploration: 'ApiExploration') -> None:
        self._import_modules()
        self._supply_attributes(api_exploration=api_exploration)
        # self._supply_modules(api_exploration=api_exploration)

    def _supply_modules(self, api_exploration: 'ApiExploration') -> None:
        if self._value.__package__:
            prefix = self._value.__package__ + "."
        else:
            prefix = ""

        if hasattr(self._value, '__path__'):
            sub_modules = pkgutil.iter_modules(self._value.__path__, prefix)

        elif hasattr(self._value, '__file__'):
            sub_modules = pkgutil.iter_modules([self._value.__file__], prefix)

        else:
            sub_modules = []

        for single_module_info in sub_modules:
            module_name = single_module_info.name
            module_value = __import__(module_name)
            api_exploration.add_sub_call_to_current_chain(
                name=module_name,
                value=module_value
            )

    def _import_modules(self) -> None:
        if self._value.__package__:
            prefix = self._value.__package__ + "."
        else:
            prefix = ""

        if hasattr(self._value, '__path__'):
            sub_modules = pkgutil.iter_modules(self._value.__path__, prefix)

        elif hasattr(self._value, '__file__'):
            sub_modules = pkgutil.iter_modules([self._value.__file__], prefix)

        else:
            sub_modules = []

        for single_module_info in sub_modules:
            module_name = single_module_info.name
            __import__(module_name)

    def _supply_attributes(self, api_exploration: 'ApiExploration') -> None:
        for single_attribute_name in dir(self._value):
            single_attribute_value = getattr(self._value, single_attribute_name)
            api_exploration.add_sub_call_to_current_chain(
                name=single_attribute_name,
                value=single_attribute_value
            )

    def __eq__(self, other: 'Call') -> bool:
        pass

    def __str__(self) -> str:
        as_string = self._name

        return as_string


@_loggerator.log_class
class Class(Call):

    def __init__(self, name: str, value: _T):
        self._name = name
        self._value = value

    def __eq__(self, other: 'Call') -> bool:
        pass

    def supply_next_sub_calls(self, api_exploration: 'ApiExploration') -> None:
        for single_attribute_name in dir(self._value):
            try:
                single_attribute_value = getattr(self._value, single_attribute_name)
            except AttributeError:
                raise

            api_exploration.add_sub_call_to_current_chain(
                name=single_attribute_name,
                value=single_attribute_value
            )

    def __str__(self) -> str:
        as_string = self._name

        return as_string


@_loggerator.log_class
class Function(Call):

    def __init__(self, name: str, value: _T):
        self._name = name
        self._value = value

    def __eq__(self, other: 'Call') -> bool:
        pass

    def supply_next_sub_calls(self, api_exploration: 'ApiExploration') -> None:
        api_exploration.complete_current_chain()

    def __str__(self) -> str:
        as_string = self._name + str(inspect.signature(self._value))

        return as_string


@_loggerator.log_class
class Attribute(Call):

    def __init__(self, name: str, value: _T):
        self._name = name
        self._value = value

    def __eq__(self, other: 'Call') -> bool:
        pass

    def supply_next_sub_calls(self, api_exploration: 'ApiExploration') -> None:
        api_exploration.complete_current_chain()

    def __str__(self) -> str:
        as_string = self._name

        return as_string


@_loggerator.log_class
class CallChain(SubCallSupplier):

    def __init__(self, calls: typing.Iterable[Call]):
        self._calls = list(calls)

    def add_call(self, call: Call) -> None:
        self._calls.append(call)

    def supply_next_sub_calls(self, api_exploration: 'ApiExploration') -> None:
        self._calls[-1].supply_next_sub_calls(
            api_exploration=api_exploration
        )

    def fork(self) -> 'CallChain':
        new_chain = self.__class__(self._calls)

        return new_chain

    def __eq__(self, other: 'CallChain') -> bool:
        pass

    def __str__(self) -> str:
        as_string = ".".join(str(single_call) for single_call in self._calls)

        return as_string

    def __len__(self) -> int:
        length = len(self._calls)

        return length


@_loggerator.log_class
class Signatures(object):

    def __init__(self, chains: typing.Iterable[CallChain]):
        self._chains = list(chains)

    def add_chain(self, chain: CallChain):
        self._chains.append(chain)

    def __str__(self) -> str:
        as_string = ", ".join(
            str(single_chain)
            for single_chain
            in self._chains
        )

        return as_string

    def __len__(self):
        length = len(self._chains)

        return length

    def __iter__(self):
        iterable = iter(str(single_chain) for single_chain in self._chains)

        return iterable


@_loggerator.log_class
class ApiExploration(object):

    def __init__(
            self,
            initial_chain: CallChain,
            public_pattern: typing.Pattern,
            magic_methods: MagicMethods,
            maximum_depth: int,
            language_modules: LanguageModules
    ):

        self._incomplete_chains = [initial_chain]
        self._completed_chains = []
        self._public_pattern = public_pattern
        self._magic_methods = magic_methods
        self._maximum_depth = maximum_depth
        self._language_modules = language_modules

    def _peak_current_chain(self):
        current_chain = self._incomplete_chains[0]

        return current_chain

    def _pop_current_chain(self):
        current_chain = self._incomplete_chains.pop(0)

        return current_chain

    def explore_and_create_signatures(self) -> Signatures:
        while self._incomplete_chains:
            next_chain = self._peak_current_chain()

            if len(next_chain) < self._maximum_depth:
                next_chain.supply_next_sub_calls(api_exploration=self)
            else:
                self.complete_current_chain()

            self._pop_current_chain()

        explored_call_chains = Signatures(chains=self._completed_chains)

        return explored_call_chains

    def _check_if_is_public(self, name: str) -> bool:
        is_public = (
                self._public_pattern.match(name)
                or self._magic_methods.check_if_is_magic_method(name=name)
        )

        return is_public

    def _check_if_is_language_module(self, value: _T):
        is_language_module = self._language_modules.check_if_is_language_module(
            value=value
        )

        return is_language_module

    def _check_if_should_be_added(self, name: str, value: _T) -> bool:
        current_chain = self._peak_current_chain()
        should_be_added = (
                len(current_chain) < self._maximum_depth
                and self._check_if_is_public(name=name)
                and not self._check_if_is_language_module(value=value)
        )

        return should_be_added

    def add_sub_call_to_current_chain(self, name: str, value: _T) -> None:
        new_call = self._create_call(name=name, value=value)
        current_chain = self._peak_current_chain()

        if self._check_if_should_be_added(name=name, value=value):
            forked_chain = current_chain.fork()
            forked_chain.add_call(call=new_call)
            self._incomplete_chains.append(forked_chain)

    @staticmethod
    def _check_if_is_metaclass(value: _T) -> bool:
        is_metaclass = issubclass(value, type)

        return is_metaclass

    def _check_if_is_class(self, value: _T) -> bool:
        is_class = (
                inspect.isclass(value)
                and not self._check_if_is_metaclass(value=value)
        )

        return is_class

    def _create_call(self, name: str, value: _T) -> Call:
        if inspect.ismodule(value):
            new_call = Module(name=name, value=value)
        elif self._check_if_is_class(value=value):
            new_call = Class(name=name, value=value)
        elif inspect.isfunction(value):
            new_call = Function(name=name, value=value)
        else:
            new_call = Attribute(name=name, value=value)

        return new_call

    def complete_current_chain(self) -> None:
        current_chain = self._peak_current_chain()
        self._completed_chains.append(current_chain)


class Serializable(abc.ABC):

    @abc.abstractmethod
    def serialize(self) -> str:
        pass


class SemanticVersion(Serializable):

    def __init__(self, major: int, minor: int, patch: int):
        self._major = major
        self._minor = minor
        self._patch = patch

    def increase_major_and_serialize(self) -> str:
        new_major = self._major + 1
        new_minor = 0
        new_patch = 0

        as_string = self._to_string(
            major=new_major,
            minor=new_minor,
            patch=new_patch
        )

        return as_string

    def increase_minor_and_serialize(self) -> str:
        new_minor = self._minor + 1
        new_patch = 0

        as_string = self._to_string(
            major=self._major,
            minor=new_minor,
            patch=new_patch
        )

        return as_string

    def increase_patch_and_serialize(self) -> str:
        new_patch = self._patch + 1

        as_string = self._to_string(
            major=self._major,
            minor=self._minor,
            patch=new_patch
        )

        return as_string

    @staticmethod
    def _to_string(major: int, minor: int, patch: int) -> str:
        as_string = ".".join((str(major), str(minor), str(patch)))

        return as_string

    def serialize(self) -> str:
        as_string = str(self)

        return as_string

    def __str__(self) -> str:
        as_string = self._to_string(
            major=self._major,
            minor=self._minor,
            patch=self._patch
        )

        return as_string

    def __eq__(self, other: Serializable) -> bool:
        are_equal = self.serialize() == other.serialize()

        return are_equal


class VersionFactory(object):

    @staticmethod
    def parse_and_create_version(serialized_version: str) -> SemanticVersion:
        parsed = serialized_version.split('.')
        major = int(parsed[0])
        minor = int(parsed[1])
        patch = int(parsed[2])
        new_version = SemanticVersion(major=major, minor=minor, patch=patch)

        return new_version


class OldPublicApi(object):

    def __init__(
            self,
            version: SemanticVersion,
            signatures: Signatures,
            version_factory: VersionFactory
    ):

        self._version = version
        self._signatures = signatures
        self._version_factory = version_factory

    def create_new_version(self, new_signatures: Signatures) -> SemanticVersion:
        new_signatures_set = set(new_signatures)
        signatures_set = set(self._signatures)

        if not signatures_set <= new_signatures_set:
            serialized_version = self._version.increase_major_and_serialize()
            new_version = self._version_factory.parse_and_create_version(
                serialized_version=serialized_version
            )

        elif new_signatures_set > signatures_set:
            serialized_version = self._version.increase_minor_and_serialize()
            new_version = self._version_factory.parse_and_create_version(
                serialized_version=serialized_version
            )
        else:
            serialized_version = self._version.increase_patch_and_serialize()
            new_version = self._version_factory.parse_and_create_version(
                serialized_version=serialized_version
            )

        return new_version


def load_signatures(module_path: str) -> Signatures:
    file_name = os.path.basename(module_path)
    module_name, _ = os.path.splitext(file_name)
    spec = util.spec_from_file_location(module_name, module_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module_call = Module(name=module.__name__, value=module)
    module_chain = CallChain(calls=[module_call])
    module_exploration = ApiExploration(
        initial_chain=module_chain,
        public_pattern=PUBLIC_PATTERN,
        magic_methods=MAGIC_METHODS,
        maximum_depth=10,
        language_modules=LANGUAGE_MODULES
    )

    signatures = module_exploration.explore_and_create_signatures()

    return signatures


def calculate_version_and_serialize(
        serialized_old_version: str,
        old_module_path: str,
        new_module_path: str
) -> str:

    old_signatures = load_signatures(module_path=old_module_path)
    new_signatures = load_signatures(module_path=new_module_path)
    version_factory = VersionFactory()
    old_version = version_factory.parse_and_create_version(
        serialized_version=serialized_old_version
    )

    old_public_api = OldPublicApi(
        version=old_version,
        signatures=old_signatures,
        version_factory=version_factory
    )

    new_version = old_public_api.create_new_version(
        new_signatures=new_signatures
    )

    serialized_new_version = new_version.serialize()

    return serialized_new_version
