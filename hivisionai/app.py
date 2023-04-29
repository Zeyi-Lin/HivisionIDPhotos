# -*- coding: utf-8 -*-

"""
@Time     : 2022/8/27 14:17
@Author   : cuny
@File     : app.py
@Software : PyCharm
@Introduce: 
查看包版本等一系列操作
"""
import os
import sys
import json
import shutil
import zipfile
import requests
from argparse import ArgumentParser
from importlib.metadata import version
try:  # 加上这个try的原因在于本地环境和云函数端的import形式有所不同
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
except ImportError:
    try:
        from qcloud_cos_v5 import CosConfig
        from qcloud_cos_v5 import CosS3Client
        from qcloud_cos.cos_exception import CosServiceError
    except ImportError:
        raise ImportError("请下载腾讯云COS相关代码包:pip install cos-python-sdk-v5")


class HivisionaiParams(object):
    """
    定义一些基本常量
    """
    # 文件所在路径
    # 包名称
    package_name = "HY-sdk"
    # 腾讯云相关变量
    region = "ap-beijing"
    zip_key = "HY-sdk/"  # zip存储的云端文件夹路径，这里改了publish.yml也需要更改
    # 云端用户配置，如果在cloud_config_save不存在，就需要下载此文件
    user_url = "https://hy-sdk-config-1305323352.cos.ap-beijing.myqcloud.com/sdk-user/user_config.json"
    bucket = "cloud-public-static-1306602019"
    # 压缩包类型
    file_format = ".zip"
    # 下载路径（.hivisionai文件夹路径）
    download_path = os.path.expandvars('$HOME')
    # zip文件、zip解压缩文件的存放路径
    save_folder = f"{os.path.expandvars('$HOME')}/.hivisionai/sdk"
    # 腾讯云配置文件存放路径
    cloud_config_save = f"{os.path.expandvars('$HOME')}/.hivisionai/user_config.json"
    # 项目路径
    hivisionai_path = os.path.dirname(os.path.dirname(__file__))
    # 使用hivisionai的路径
    getcwd = os.getcwd()
    # HY-func的依赖配置
    # 每个依赖会包含三个参数，保存路径（save_path，相对于HY_func的路径）、下载url（url）
    functionDependence = {
        "configs":  [
            # --------- 配置文件部分
            # _lib
            {
                "url": "https://hy-sdk-config-1305323352.cos.ap-beijing.myqcloud.com/hy-func/_lib/config/aliyun-human-matting-api.json",
                "save_path": "_lib/config/aliyun-human-matting-api.json"
            },
            {
                "url": "https://hy-sdk-config-1305323352.cos.ap-beijing.myqcloud.com/hy-func/_lib/config/megvii-face-plus-api.json",
                "save_path": "_lib/config/megvii-face-plus-api.json"
            },
            {
                "url": "https://hy-sdk-config-1305323352.cos.ap-beijing.myqcloud.com/hy-func/_lib/config/volcano-face-change-api.json",
                "save_path": "_lib/config/volcano-face-change-api.json"
            },
            # _service
            {
                "url": "https://hy-sdk-config-1305323352.cos.ap-beijing.myqcloud.com/hy-func/_service/config/func_error_conf.json",
                "save_path": "_service/utils/config/func_error_conf.json"
            },
            {
                "url": "https://hy-sdk-config-1305323352.cos.ap-beijing.myqcloud.com/hy-func/_service/config/service_config.json",
                "save_path": "_service/utils/config/service_config.json"
            },
            # --------- 模型部分
            # 模型部分存储在Notion文档当中
            # https://www.notion.so/HY-func-cc6cc41ba6e94b36b8fa5f5d67d1683f
        ],
        "weights": "https://www.notion.so/HY-func-cc6cc41ba6e94b36b8fa5f5d67d1683f"
    }


class HivisionaiUtils(object):
    """
    本类为一些基本工具类，包含代码复用相关内容
    """
    @staticmethod
    def get_client():
        """获取cos客户端对象"""
        def get_secret():
            # 首先判断cloud_config_save下是否存在
            if not os.path.exists(HivisionaiParams.cloud_config_save):
                print("Downloading user_config...")
                resp = requests.get(HivisionaiParams.user_url)
                open(HivisionaiParams.cloud_config_save, "wb").write(resp.content)
            config = json.load(open(HivisionaiParams.cloud_config_save, "r"))
            return config["secret_id"], config["secret_key"]
        # todo 接入HY-Auth-Sync
        secret_id, secret_key = get_secret()
        return CosS3Client(CosConfig(Region=HivisionaiParams.region, Secret_id=secret_id, Secret_key=secret_key))

    def get_all_versions(self):
        """获取云端的所有版本号"""
        def getAllVersion_base():
            """
            返回cos存储桶内部的某个文件夹的内部名称
            ps:如果需要修改默认的存储桶配置，请在代码运行的时候加入代码 s.bucket = 存储桶名称 （s是对象实例）
            返回的内容存储在response["Content"]，不过返回的数据大小是有限制的，具体内容还是请看官方文档。
            Returns:
                [版本列表]
            """
            resp = client.list_objects(
                Bucket=HivisionaiParams.bucket,
                Prefix=HivisionaiParams.zip_key,
                Marker=marker
            )
            versions_list.extend([x["Key"].split("/")[-1].split(HivisionaiParams.file_format)[0] for x in resp["Contents"] if int(x["Size"]) > 0])
            if resp['IsTruncated'] == 'false':  # 接下来没有数据了,就退出
                return ""
            else:
                return resp['NextMarker']
        client = self.get_client()
        marker = ""
        versions_list = []
        while True:  # 轮询
            try:
                marker = getAllVersion_base()
            except KeyError as e:
                print(e)
                raise
            if len(marker) == 0:  # 没有数据了
                break
        return versions_list

    def get_newest_version(self):
        """获取最新的版本号"""
        versions_list = self.get_all_versions()
        # reverse=True，降序
        versions_list.sort(key=lambda x: int(x.split(".")[-1]), reverse=True)
        versions_list.sort(key=lambda x: int(x.split(".")[-2]), reverse=True)
        versions_list.sort(key=lambda x: int(x.split(".")[-3]), reverse=True)
        return versions_list[0]

    def download_version(self, v):
        """
        在存储桶中下载文件，将下载好的文件解压至本地
        Args:
            v: 版本号，x.x.x

        Returns:
            None
        """
        file_name = v + HivisionaiParams.file_format
        client = self.get_client()
        print(f"Download to {HivisionaiParams.save_folder}...")
        try:
            resp = client.get_object(HivisionaiParams.bucket, HivisionaiParams.zip_key + "/" + file_name)
            contents = resp["Body"].get_raw_stream().read()
        except CosServiceError:
            print(f"[{file_name}.zip] does not exist, please check your version!")
            sys.exit()
        if not os.path.exists(HivisionaiParams.save_folder):
            os.makedirs(HivisionaiParams.save_folder)
        open(os.path.join(HivisionaiParams.save_folder, file_name), "wb").write(contents)
        print("Download success!")

    @staticmethod
    def download_dependence(path=None):
        """
        一键下载HY-sdk所需要的所有依赖，需要注意的是，本方法必须在运行pip install之后使用（运行完pip install之后才会出现hivisionai文件夹）
        Args:
            path: 文件路径，精确到hivisionai文件夹的上一个目录，如果为None，则默认下载到python环境下hivisionai安装的目录

        Returns:
            下载相应内容到指定位置
        """
        # print("指定的下载路径：", path)  # 此时在path路径下必然存在一个hivisionai文件夹
        # print("系统安装的hivisionai库的路径:", HivisionaiParams.hivisionai_path)
        print("Dependence downloading...")
        if path is None:
            path = HivisionaiParams.hivisionai_path
        # ----------------下载mtcnn模型文件
        mtcnn_path = os.path.join(path, "hivisionai/hycv/mtcnn_onnx/weights")
        base_url = "https://linimages.oss-cn-beijing.aliyuncs.com/"
        onnx_files = ["pnet.onnx",  "rnet.onnx", "onet.onnx"]
        print(f"Downloading mtcnn model in {mtcnn_path}")
        if not os.path.exists(mtcnn_path):
            os.mkdir(mtcnn_path)
        for onnx_file in onnx_files:
            if not os.path.exists(os.path.join(mtcnn_path, onnx_file)):
                # download onnx model
                onnx_url = base_url + onnx_file
                print("Downloading Onnx Model in:", onnx_url)
                r = requests.get(onnx_url, stream=True)
                if r.status_code == 200:
                    open(os.path.join(mtcnn_path, onnx_file), 'wb').write(r.content)  # 将内容写入文件
                    print(f"Download finished -- {onnx_file}")
                del r
        # ----------------
        print("Dependence download finished...")


class HivisionaiApps(object):
    """
    本类为app对外暴露的接口，为了代码规整性，这里使用类来对暴露接口进行调整
    """
    @staticmethod
    def show_cloud_version():
        """查看在cos中的所有HY-sdk版本"""
        print("Connect to COS...")
        versions_list = hivisionai_utils.get_all_versions()
        # reverse=True，降序
        versions_list.sort(key=lambda x: int(x.split(".")[-1]), reverse=True)
        versions_list.sort(key=lambda x: int(x.split(".")[-2]), reverse=True)
        versions_list.sort(key=lambda x: int(x.split(".")[-3]), reverse=True)
        if len(versions_list) == 0:
            print("There is no version currently, please release it first!")
            sys.exit()
        versions = "The currently existing versions (Keep 10): \n"
        for i, v in enumerate(versions_list):
            versions += str(v) + " "
            if i == 9:
                break
        print(versions)

    @staticmethod
    def upgrade(v: str, enforce: bool = False, save_cached: bool = False):
        """
        自动升级HY-sdk到指定版本
        Args:
            v: 指定的版本号，格式为x.x.x
            enforce: 是否需要强制执行更新命令
            save_cached: 是否保存下载的wheel文件，默认为否
        Returns:
            None
        """
        def check_format():
            # noinspection PyBroadException
            try:
                major, minor, patch = v.split(".")
                int(major)
                int(minor)
                int(patch)
            except Exception as e:
                print(f"Illegal version number!\n{e}")
            pass
        print("Upgrading, please wait a moment...")
        if v == "-1":
            v = hivisionai_utils.get_newest_version()
        # 检查format的格式
        check_format()
        if v == version(HivisionaiParams.package_name) and not enforce:
            print(f"Current version: {v} already exists, skip installation.")
            sys.exit()
        hivisionai_utils.download_version(v)
        # 下载完毕（下载至save_folder），解压文件
        target_zip = os.path.join(HivisionaiParams.save_folder, f"{v}.zip")
        assert zipfile.is_zipfile(target_zip), "Decompression failed, and the target was not a zip file."
        new_dir = target_zip.replace('.zip', '')  # 解压的文件名
        if os.path.exists(new_dir):  # 判断文件夹是否存在
            shutil.rmtree(new_dir)
        os.mkdir(new_dir)  # 新建文件夹
        f = zipfile.ZipFile(target_zip)
        f.extractall(new_dir)  # 提取zip文件
        print("Decompressed, begin to install...")
        os.system(f'pip3 install {os.path.join(new_dir, "**.whl")}')
        # 开始自动下载必要的模型依赖
        hivisionai_utils.download_dependence()
        # 安装完毕，如果save_cached为真，删除"$HOME/.hivisionai/sdk"内部的所有文件元素
        if save_cached is True:
            os.system(f'rm -rf {HivisionaiParams.save_folder}/**')

    @staticmethod
    def export(path):
        """
        输出最新版本的文件到命令运行的path目录
        Args:
            path: 用户输入的路径

        Returns:
            输出最新的hivisionai到path目录
        """
        # print(f"当前路径: {os.path.join(HivisionaiParams.getcwd, path)}")
        # print(f"文件路径: {os.path.dirname(__file__)}")
        export_path = os.path.join(HivisionaiParams.getcwd, path)
        # 判断输出路径存不存在，如果不存在，就报错
        assert os.path.exists(export_path), f"{export_path} dose not Exists!"
        v = hivisionai_utils.get_newest_version()
        # 下载文件到.hivisionai/sdk当中
        hivisionai_utils.download_version(v)
        # 下载完毕（下载至save_folder），解压文件
        target_zip = os.path.join(HivisionaiParams.save_folder, f"{v}.zip")
        assert zipfile.is_zipfile(target_zip), "Decompression failed, and the target was not a zip file."
        new_dir = os.path.basename(target_zip.replace('.zip', ''))  # 解压的文件名
        new_dir = os.path.join(export_path, new_dir)  # 解压的文件路径
        if os.path.exists(new_dir):  # 判断文件夹是否存在
            shutil.rmtree(new_dir)
        os.mkdir(new_dir)  # 新建文件夹
        f = zipfile.ZipFile(target_zip)
        f.extractall(new_dir)  # 提取zip文件
        print("Decompressed, begin to export...")
        # 强制删除bin/hivisionai和hivisionai/以及HY_sdk-**
        bin_path = os.path.join(export_path, "bin")
        hivisionai_path = os.path.join(export_path, "hivisionai")
        sdk_path = os.path.join(export_path, "HY_sdk-**")
        os.system(f"rm -rf {bin_path} {hivisionai_path} {sdk_path}")
        # 删除完毕，开始export
        os.system(f'pip3 install {os.path.join(new_dir, "**.whl")} -t {export_path}')
        hivisionai_utils.download_dependence(export_path)
        # 将下载下来的文件夹删除
        os.system(f'rm -rf {target_zip} && rm -rf {new_dir}')
        print("Done.")

    @staticmethod
    def hy_func_init(force):
        """
        在HY-func目录下使用hivisionai --init，可以自动将需要的依赖下载到指定位置
        不过对于比较大的模型——修复模型而言，需要手动下载
        Args:
            force: 如果force为True，则会强制重新下载所有的内容，包括修复模型这种比较大的模型
        Returns:
            程序执行完毕，会将一些必要的依赖也下载完毕
        """
        cwd = HivisionaiParams.getcwd
        # 判断当前文件夹是否是HY-func
        dirName = os.path.basename(cwd)
        assert dirName == "HY-func", "请在正确的文件目录下初始化HY-func!"
        # 需要下载的内容会存放在HivisionaiParams的functionDependence变量下
        functionDependence = HivisionaiParams.functionDependence
        # 下载配置文件
        configs = functionDependence["configs"]
        print("正在下载配置文件...")
        for config in configs:
            if not force and os.path.exists(config['save_path']):
                print(f"[pass]: {os.path.basename(config['url'])}")
                continue
            print(f"[Download]: {config['url']}")
            resp = requests.get(config['url'])
            # json文件存储在text区域，但是其他的不一定
            open(os.path.join(cwd, config['save_path']), 'w').write(resp.text)
        # 其他文件，提示访问notion文档
        print(f"[NOTICE]: 一切准备就绪，请访问下面的文档下载剩下的模型文件:\n{functionDependence['weights']}")

    @staticmethod
    def hy_func_deploy(functionName: str = None, functionPath: str = None):
        """
        在HY-func目录下使用此命令，并且随附功能函数的名称，就可以将HY-func的部署版放到桌面上
        但是需要注意的是，本方式不适合修复功能使用，修复功能依旧需要手动制作镜像
        Args:
            functionName: 功能函数名称
            functionPath: 需要注册的HY-func路径

        Returns:
            程序执行完毕，桌面会出现一个同名文件夹
        """
        # 为了代码撰写的方便，这里仅仅把模型文件删除，其余配置文件保留
        # 为了实现在任意位置输入hivisionai --deploy funcName都能成功，在使用前需要在.hivisionai/user_config.json中注册
        # print(functionName, functionPath)
        if functionPath is not None:
            # 更新/添加路径
            # functionPath为相对于使用路径的路径
            assert os.path.basename(functionPath) == "HY-func", "所指向路径非HY-func!"
            func_path = os.path.join(HivisionaiParams.getcwd, functionPath)
            assert os.path.join(func_path), f"路径不存在: {func_path}"
            # functionPath的路径写到user_config当中
            user_config = json.load(open(HivisionaiParams.cloud_config_save, 'rb'))
            user_config["func_path"] = func_path
            open(HivisionaiParams.cloud_config_save, 'w').write(json.dumps(user_config))
            print("HY-func全局路径保存成功!")
        try:
            user_config = json.load(open(HivisionaiParams.cloud_config_save, 'rb'))
            func_path = user_config['func_path']
        except KeyError:
            return print("请先使用-p命令注册全局HY-func路径!")
        # 此时func_path必然存在
        # print(os.listdir(func_path))
        assert functionName in os.listdir(func_path), functionName + "功能不存在!"
        func_path_deploy = os.path.join(func_path, functionName)
        # 开始复制文件到指定目录
        # 我们默认移动到Desktop目录下，如果没有此目录，需要先创建一个
        target_dir = os.path.join(HivisionaiParams.download_path, "Desktop")
        assert os.path.exists(target_dir), target_dir + "文件路径不存在,你需要先创建一下!"
        # 开始移动
        target_dir = os.path.join(target_dir, functionName)
        print("正在复制需要部署的文件...")
        os.system(f"rm -rf {target_dir}")
        os.system(f'cp -rf {func_path_deploy} {target_dir}')
        os.system(f"cp -rf {os.path.join(func_path, '_lib')} {target_dir}")
        os.system(f"cp -rf {os.path.join(func_path, '_service')} {target_dir}")
        # 生成最新的hivisionai
        print("正在生成hivisionai代码包...")
        os.system(f'hivisionai -t {target_dir}')
        # 移动完毕，删除模型文件
        print("移动完毕，正在删除不需要的文件...")
        # 模型文件
        os.system(f"rm -rf {os.path.join(target_dir, '_lib', 'weights', '**')}")
        # hivisionai生成时的多余文件
        os.system(f"rm -rf {os.path.join(target_dir, 'bin')} {os.path.join(target_dir, 'HY_sdk**')}")
        print("部署文件生成成功，你可以开始部署了!")


hivisionai_utils = HivisionaiUtils()


def entry_point():
    parser = ArgumentParser()
    # 查看版本号
    parser.add_argument("-v", "--version", action="store_true", help="View the current HY-sdk version, which does not represent the final cloud version.")
    # 自动更新
    parser.add_argument("-u", "--upgrade", nargs='?', const="-1", type=str, help="Automatically update HY-sdk to the latest version")
    # 查找云端的HY-sdk版本
    parser.add_argument("-l", "--list", action="store_true", help="Find HY-sdk versions of the cloud, and keep up to ten")
    # 下载云端的版本到本地路径
    parser.add_argument("-t", "--export", nargs='?', const="./", help="Add a path parameter to automatically download the latest version of sdk to this path. If there are no parameters, the default is the current path")
    # 强制更新附带参数，当一个功能需要强制执行一遍的时候，需要附带此参数
    parser.add_argument("-f", "--force", action="store_true", help="Enforcement of other functions, execution of a single parameter is meaningless")
    # 初始化HY-func
    parser.add_argument("--init", action="store_true", help="Initialization HY-func")
    # 部署HY-func
    parser.add_argument("-d", "--deploy", nargs='?', const="-1", type=str, help="Deploy HY-func")
    # 涉及注册一些自定义内容的时候，需要附带此参数，并写上自定义内容
    parser.add_argument("-p", "--param", nargs='?', const="-1", type=str, help="When registering some custom content, you need to attach this parameter and write the custom content.")
    args = parser.parse_args()
    if args.version:
        print(version(HivisionaiParams.package_name))
        sys.exit()
    if args.upgrade:
        HivisionaiApps.upgrade(args.upgrade, args.force)
        sys.exit()
    if args.list:
        HivisionaiApps.show_cloud_version()
        sys.exit()
    if args.export:
        HivisionaiApps.export(args.export)
        sys.exit()
    if args.init:
        HivisionaiApps.hy_func_init(args.force)
        sys.exit()
    if args.deploy:
        HivisionaiApps.hy_func_deploy(args.deploy, args.param)


if __name__ == "__main__":
    entry_point()
