import ops
import iopc

TARBALL_FILE="qemu-2.12.0.tar.xz"
TARBALL_DIR="qemu-2.12.0"
INSTALL_DIR="qemu-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""
dst_usr_local_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    global dst_usr_local_lib_dir
    global dst_usr_local_libexec_dir
    global dst_usr_local_share_dir
    global src_pkgconfig_dir
    global dst_pkgconfig_dir
    global dst_bin_dir
    global install_test_utils
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")
    dst_bin_dir = ops.path_join(install_dir, "bin")
    dst_usr_local_lib_dir = ops.path_join(install_dir, "usr/local/lib")
    dst_usr_local_libexec_dir = ops.path_join(install_dir, "usr/local/libexec")
    dst_usr_local_share_dir = ops.path_join(install_dir, "usr/local/share")
    src_pkgconfig_dir = ops.path_join(pkg_path, "pkgconfig")
    dst_pkgconfig_dir = ops.path_join(install_dir, "pkgconfig")
    if ops.getEnv("INSTALL_TEST_UTILS") == 'y':
        install_test_utils = True
    else:
        install_test_utils = False


def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))

    cc_sysroot = ops.getEnv("CC_SYSROOT")
    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm/libdrm')

    ldflags = ""
    ldflags += " -L" + ops.path_join(cc_sysroot, 'lib')
    ldflags += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')

    libs = ""
    libs += " -lffi -lxml2 -lexpat -ldrm"
    #ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    #ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    #ops.exportEnv(ops.setEnv("LIBS", libs))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    extra_conf = []
    extra_conf.append("--target-list=x86_64-softmmu,x86_64-linux-user")

    cc_sysroot = ops.getEnv("CC_SYSROOT")
    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libz')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpcre3')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpixman')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libxml2')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib/glib-2.0')

    libs = ""
    libs += " -L" + ops.path_join(cc_sysroot, 'lib')
    libs += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    libs += " -lz -lglib-2.0 -lpcre -lffi -lpixman-1 -lxml2"
    extra_conf.append("--extra-cflags=" + cflags)
    extra_conf.append("--extra-ldflags=" + libs)

    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)
    ops.mkdir(dst_bin_dir)
    ops.mkdir(dst_usr_local_lib_dir)

    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/ivshmem-client"), dst_bin_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/ivshmem-server"), dst_bin_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/qemu-ga"), dst_bin_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/qemu-img"), dst_bin_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/qemu-io"), dst_bin_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/qemu-nbd"), dst_bin_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/qemu-pr-helper"), dst_bin_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/qemu-system-x86_64"), dst_bin_dir)
    if install_test_utils:
        ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/qemu-x86_64"), dst_bin_dir)

    ops.mkdir(dst_usr_local_libexec_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/libexec/qemu-bridge-helper"), dst_usr_local_libexec_dir)

    ops.mkdir(dst_usr_local_share_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/share/qemu"), dst_usr_local_share_dir)

    #ops.mkdir(tmp_include_dir)
    #ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)

    #ops.mkdir(dst_pkgconfig_dir)
    #ops.copyto(ops.path_join(src_pkgconfig_dir, '.'), dst_pkgconfig_dir)

    return True

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_bin_dir, "."), "bin")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_usr_local_lib_dir, "."), "usr/local/lib")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_usr_local_libexec_dir, "."), "usr/local/libexec")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_usr_local_share_dir, "."), "usr/local/share")
    #iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)
    #iopc.installBin(args["pkg_name"], ops.path_join(dst_pkgconfig_dir, '.'), "pkgconfig")

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

